import enum
import re
import unicodedata
from contextlib import suppress
from itertools import repeat
from typing import Optional

import attr
import numpy as np
from lxml import etree as ET
from ocrd_utils import getLogger


class Normalization(enum.Enum):
    NFC = 1
    NFC_MUFI = 2  # TODO
    NFC_SBB = 3


def normalize(text, normalization):
    if normalization == Normalization.NFC:
        return unicodedata.normalize("NFC", text)
    if normalization == Normalization.NFC_MUFI:
        raise NotImplementedError()
    if normalization == Normalization.NFC_SBB:
        return substitute_equivalences(text)
    else:
        raise ValueError()


# XXX hack
def normalize_sbb(t):
    return normalize(t, Normalization.NFC_SBB)


def unjoin_ligatures(s):
    """Unjoin ligatures, i.e. ﬀ becomes ff."""

    equivalences = {
        "": "ſſ",
        "\ueba7": "ſſi",  # MUFI: LATIN SMALL LIGATURE LONG S LONG S I
        "": "ch",
        "": "ck",
        "": "ll",
        "": "ſi",
        "": "ſt",
        "ﬁ": "fi",
        "ﬀ": "ff",
        "ﬂ": "fl",
        "ﬃ": "ffi",
        "": "ct",
        "": "tz",  # MUFI: LATIN SMALL LIGATURE TZ
        "\uf532": "as",  # eMOP: Latin small ligature as
        "\uf533": "is",  # eMOP: Latin small ligature is
        "\uf534": "us",  # eMOP: Latin small ligature us
        "\uf535": "Qu",  # eMOP: Latin ligature capital Q small u
        "ĳ": "ij",  # U+0133 LATIN SMALL LIGATURE IJ
        "\uE8BF": "q&",
        # MUFI: LATIN SMALL LETTER Q LIGATED WITH FINAL ET
        # XXX How to replace this correctly?
        "\uEBA5": "ſp",  # MUFI: LATIN SMALL LIGATURE LONG S P
        "ﬆ": "st",  # U+FB06 LATIN SMALL LIGATURE ST
    }
    s = unicodedata.normalize("NFC", s)
    for fr, to in equivalences.items():
        s = s.replace(fr, to)
    return s


def substitute_equivalences(s):
    # These are for OCR-D GT vs Tesseract frk vs Calamari GT4HistOCR
    # It might make sense to use different rules for GT and for the different OCR
    equivalences = {
        "": "ü",
        "": "ä",
        "==": "–",  # → en-dash
        "—": "–",  # em-dash → en-dash
        "": "ö",
        "’": "'",
        "⸗": "-",
        "aͤ": "ä",  # LATIN SMALL LETTER A, COMBINING LATIN SMALL LETTER E
        "oͤ": "ö",  # LATIN SMALL LETTER O, COMBINING LATIN SMALL LETTER E
        "uͤ": "ü",  # LATIN SMALL LETTER U, COMBINING LATIN SMALL LETTER E
        "\uF50E": "q́",  # U+F50E LATIN SMALL LETTER Q WITH ACUTE ACCENT
    }

    s = unicodedata.normalize("NFC", s)
    s = unjoin_ligatures(s)
    for fr, to in equivalences.items():
        s = s.replace(fr, to)
    return s


@attr.s(frozen=True)
class ExtractedText:
    """
    Extracted text.

    We need a segment id for each extracted text segment. As this should support
    extracting from the word (or even glyph) level, we need to have a
    hierarchical representation of the
    text due to the different "joiners" needed on each level.

    For example, here is pseudo code to get the text of a page:

    * from region texts:
      `'\n'.join(region_texts)`
    * from line texts:
      `'\n'.join('\n'.join(line_texts) for every region`)
    * from word texts:
      `'\n'.join(('\n'.join(' '.join(word_texts) for every line) for every region))`

    An ExtractedText object either contains a text itself or has child segments
    (and a joiner), not both.

    Objects of this class are guaranteed to be a. always in their normalization
    and b. in NFC.
    """

    segment_id = attr.ib(type=Optional[str])

    @segment_id.validator
    def check(self, _, value):
        if value is None:
            return
        if not re.match(r"[\w\d_-]+", value):
            raise ValueError('Malformed segment id "{}"'.format(value))

    # An object contains either
    # a. _text itself
    # b. or segments (ExtractedText) and a joiner

    segments = attr.ib(type=Optional[list], converter=attr.converters.optional(list))
    joiner = attr.ib(type=Optional[str])
    _text = attr.ib(type=Optional[str])

    @segments.validator
    def check(self, _, value):
        if value is not None and self._text is not None:
            raise ValueError("Can't have both segments and text")

    @_text.validator
    def check(self, _, value):
        if value is not None and self.segments is not None:
            raise ValueError("Can't have both segments and text")
        if value is not None and unicodedata.normalize("NFC", value) != value:
            raise ValueError('String "{}" is not in NFC.'.format(value))
        if value is not None and normalize(value, self.normalization) != value:
            raise ValueError('String "{}" is not normalized.'.format(value))

    normalization = attr.ib(converter=Normalization, default=Normalization.NFC_SBB)

    @property
    def text(self):
        if self._text is not None:
            return self._text
        else:
            return self.joiner.join(s.text for s in self.segments)

    _segment_id_for_pos = None

    def segment_id_for_pos(self, pos):
        # Calculate segment ids once, on the first call
        if not self._segment_id_for_pos:
            if self._text is not None:
                segment_id_for_pos = list(repeat(self.segment_id, len(self._text)))
            else:
                # Recurse
                segment_id_for_pos = []
                for s in self.segments:
                    seg_ids = [s.segment_id_for_pos(i) for i in range(len(s.text))]
                    segment_id_for_pos.extend(seg_ids)
                    segment_id_for_pos.extend(repeat(None, len(self.joiner)))
                segment_id_for_pos = segment_id_for_pos[: -len(self.joiner)]

            # This is frozen, so we have to jump through the hoop:
            object.__setattr__(self, "_segment_id_for_pos", segment_id_for_pos)
            assert self._segment_id_for_pos

        return self._segment_id_for_pos[pos]

    @classmethod
    def from_text_segment(cls, text_segment, nsmap, textequiv_level="region"):
        """Build an ExtractedText from a PAGE content text element"""

        localname_for_textequiv_level = {"region": "TextRegion", "line": "TextLine"}
        textequiv_level_for_localname = invert_dict(localname_for_textequiv_level)
        children_for_localname = {"TextRegion": "TextLine"}
        joiner_for_textequiv_level = {"line": "\n"}

        segment_id = text_segment.attrib["id"]
        localname = ET.QName(text_segment).localname
        if localname == localname_for_textequiv_level[textequiv_level]:
            segment_text = None
            with suppress(AttributeError):
                segment_text = get_textequiv_unicode(text_segment, nsmap)
                # FIXME hardcoded SBB normalization
                segment_text = normalize_sbb(segment_text)
            segment_text = segment_text or ""
            return cls(segment_id, None, None, segment_text)
        else:
            # Recurse
            sub_localname = children_for_localname[localname]
            sub_textequiv_level = textequiv_level_for_localname[sub_localname]
            segments = []
            for sub_segment in text_segment.iterfind(
                "./page:%s" % sub_localname, namespaces=nsmap
            ):
                segments.append(
                    ExtractedText.from_text_segment(
                        sub_segment, nsmap, textequiv_level=sub_textequiv_level
                    )
                )
            joiner = joiner_for_textequiv_level[sub_textequiv_level]
            return cls(segment_id, segments, joiner, None)

    @classmethod
    def from_str(cls, text, normalization=Normalization.NFC_SBB):
        normalized_text = normalize(text, normalization)
        return cls(None, None, None, normalized_text, normalization=normalization)


def invert_dict(d):
    """Invert the given dict."""
    return {v: k for k, v in d.items()}


def get_textequiv_unicode(text_segment, nsmap) -> str:
    """Get the TextEquiv/Unicode text of the given PAGE text element."""
    segment_id = text_segment.attrib["id"]
    textequivs = text_segment.findall("./page:TextEquiv", namespaces=nsmap)

    if not textequivs:
        return ""

    textequiv = get_first_textequiv(textequivs, segment_id)
    return textequiv.find("./page:Unicode", namespaces=nsmap).text or ""


def get_first_textequiv(textequivs, segment_id):
    """Get the first TextEquiv based on index or conf order if index is not present."""
    log = getLogger("processor.OcrdDinglehopperEvaluate")
    if len(textequivs) == 1:
        return textequivs[0]

    # try ordering by index
    indices = np.array([get_attr(te, "index") for te in textequivs], dtype=float)
    nan_mask = np.isnan(indices)
    if np.any(~nan_mask):
        if np.any(nan_mask):
            log.warning("TextEquiv without index in %s.", segment_id)
        index = np.nanargmin(indices)
    else:
        # try ordering by conf
        confidences = np.array([get_attr(te, "conf") for te in textequivs], dtype=float)
        if np.any(~np.isnan(confidences)):
            log.info(
                "No index attributes, use 'conf' attribute to sort TextEquiv in %s.",
                segment_id,
            )
            index = np.nanargmax(confidences)
        else:
            # fallback to first entry in case of neither index or conf present
            log.warning("No index attributes, use first TextEquiv in %s.", segment_id)
            index = 0
    return textequivs[index]


def get_attr(te, attr_name) -> float:
    """Extract the attribute for the given name.

    Note: currently only handles numeric values!
    Other or non existend values are encoded as np.nan.
    """
    attr_value = te.attrib.get(attr_name)
    try:
        return float(attr_value)
    except TypeError:
        return np.nan
