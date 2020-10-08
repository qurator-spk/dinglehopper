from __future__ import division, print_function

from typing import Optional
from warnings import warn

from lxml import etree as ET
from lxml.etree import XMLSyntaxError
from contextlib import suppress
from itertools import repeat
from .substitute_equivalences import substitute_equivalences
import sys
import attr
import enum
import unicodedata
import re


class Normalization(enum.Enum):
    NFC = 1
    NFC_MUFI = 2  # TODO
    NFC_SBB = 3


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
    # TODO validator

    segments = attr.ib(type=Optional[list], converter=attr.converters.optional(list))
    joiner = attr.ib(type=Optional[str])
    _text = attr.ib(type=Optional[str])

    @segments.validator
    def check(self, _, value):
        if value is not None and self._text is not None:
            raise ValueError("Can't have both segments and text")

    @_text.validator
    def check(self, _, value):
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


def alto_namespace(tree):
    """Return the ALTO namespace used in the given ElementTree.

    This relies on the assumption that, in any given ALTO file, the root element has the local name "alto". We do not
    check if the files uses any valid ALTO namespace.
    """
    root_name = ET.QName(tree.getroot().tag)
    if root_name.localname == 'alto':
        return root_name.namespace
    else:
        raise ValueError('Not an ALTO tree')


def alto_extract(tree):
    """Extract text from the given ALTO ElementTree."""

    nsmap = {'alto': alto_namespace(tree)}

    lines = (
        ' '.join(string.attrib.get('CONTENT') for string in line.iterfind('alto:String', namespaces=nsmap))
        for line in tree.iterfind('.//alto:TextLine', namespaces=nsmap))

    return ExtractedText(
            None,
            (ExtractedText.from_str(normalize_sbb(line_text)) for line_text in lines),
            '\n',
            None
    )
    # FIXME hardcoded SBB normalization
    # TODO This currently does not extract any segment id, because we are
    #      clueless about the ALTO format.


def alto_text(tree):
    return alto_extract(tree).text


def page_namespace(tree):
    """Return the PAGE content namespace used in the given ElementTree.

    This relies on the assumption that, in any given PAGE content file, the root element has the local name "PcGts". We
    do not check if the files uses any valid PAGE namespace.
    """
    root_name = ET.QName(tree.getroot().tag)
    if root_name.localname == 'PcGts':
        return root_name.namespace
    else:
        raise ValueError('Not a PAGE tree')


def page_extract(tree):
    """Extract text from the given PAGE content ElementTree."""

    nsmap = {'page': page_namespace(tree)}

    regions = []
    reading_order = tree.find('.//page:ReadingOrder', namespaces=nsmap)
    if reading_order is not None:
        for group in reading_order.iterfind('./*', namespaces=nsmap):
            if ET.QName(group.tag).localname == 'OrderedGroup':
                region_ref_indexeds = group.findall('./page:RegionRefIndexed', namespaces=nsmap)
                for region_ref_indexed in sorted(region_ref_indexeds, key=lambda r: int(r.attrib['index'])):
                    region_id = region_ref_indexed.attrib['regionRef']
                    region = tree.find('.//page:TextRegion[@id="%s"]' % region_id, namespaces=nsmap)
                    if region is not None:
                        regions.append(ExtractedText.from_text_segment(region, nsmap))
                    else:
                        warn('Not a TextRegion: "%s"' % region_id)
            else:
                raise NotImplementedError
    else:
        for region in tree.iterfind('.//page:TextRegion', namespaces=nsmap):
            regions.append(ExtractedText.from_text_segment(region, nsmap))

    # Filter empty region texts
    regions = (r for r in regions if r.text is not None)

    return ExtractedText(None, regions, '\n', None)


def page_text(tree):
    return page_extract(tree).text


def plain_extract(filename):
    with open(filename, 'r') as f:
        return ExtractedText(
                None,
                [ExtractedText('line %d' % no, None, None, line) for no, line in enumerate(f.readlines())],
                '\n',
                None
        )


def plain_text(filename):
    return plain_extract(filename).text


def extract(filename):
    """Extract the text from the given file.

    Supports PAGE, ALTO and falls back to plain text.
    """
    try:
        tree = ET.parse(filename)
    except XMLSyntaxError:
        return plain_extract(filename)
    try:
        return page_extract(tree)
    except ValueError:
        return alto_extract(tree)


def text(filename):
    return extract(filename).text


if __name__ == '__main__':
    print(text(sys.argv[1]))
