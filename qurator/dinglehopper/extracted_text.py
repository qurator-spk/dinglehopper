import enum
import re
import unicodedata
from contextlib import suppress
from itertools import repeat
from typing import Optional

import attr

from .substitute_equivalences import substitute_equivalences


class Normalization(enum.Enum):
    NFC = 1
    NFC_MUFI = 2  # TODO
    NFC_SBB = 3


def normalize(text, normalization):
    if normalization == Normalization.NFC:
        return unicodedata.normalize('NFC', text)
    if normalization == Normalization.NFC_MUFI:
        raise NotImplementedError()
    if normalization == Normalization.NFC_SBB:
        return substitute_equivalences(text)
    else:
        raise ValueError()


# XXX hack
def normalize_sbb(t):
    return normalize(t, Normalization.NFC_SBB)


@attr.s(frozen=True)
class ExtractedText:
    """
    Extracted text

    Objects of this class are guaranteed to be a. always in their normalization and
    b. in NFC.
    """
    segment_id = attr.ib(type=Optional[str])

    @segment_id.validator
    def check(self, _, value):
        if value is None:
            return
        if not re.match(r'[\w\d_-]+', value):
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
        if value is not None and unicodedata.normalize('NFC', value) != value:
            raise ValueError('String "{}" is not in NFC.'.format(value))
        if value is not None and normalize(value, self.normalization) != value:
            raise ValueError('String "{}" is not normalized.'.format(value))

    normalization = attr.ib(converter=Normalization, default=Normalization.NFC_SBB)

    @property
    def text(self):
        if self._text is not None:
            if self._text == '':
                return None
            else:
                return self._text
        else:
            return self.joiner.join(s.text for s in self.segments)

    _segment_id_for_pos = None

    def segment_id_for_pos(self, pos):
        # Calculate segment ids once, on the first call
        if not self._segment_id_for_pos:
            segment_id_for_pos = []
            for s in self.segments:
                segment_id_for_pos.extend(repeat(s.segment_id, len(s.text)))
                segment_id_for_pos.extend(repeat(None, len(self.joiner)))
            segment_id_for_pos = segment_id_for_pos[:-len(self.joiner)]
            # This is frozen, so we have to jump through the hoop:
            object.__setattr__(self, '_segment_id_for_pos', segment_id_for_pos)
            assert self._segment_id_for_pos

        return self._segment_id_for_pos[pos]

    @classmethod
    def from_text_segment(cls, text_segment, nsmap):
        """Build an ExtractedText from a PAGE content text element"""

        segment_id = text_segment.attrib['id']
        segment_text = None
        with suppress(AttributeError):
            segment_text = text_segment.find('./page:TextEquiv/page:Unicode', namespaces=nsmap).text
            segment_text = segment_text or ''
            segment_text = normalize_sbb(segment_text)  # FIXME hardcoded SBB normalization
        segment_text = segment_text or ''
        return cls(segment_id, None, None, segment_text)

    @classmethod
    def from_str(cls, text, normalization=Normalization.NFC_SBB):
        normalized_text = normalize(text, normalization)
        return cls(None, None, None, normalized_text, normalization=normalization)