from __future__ import division, print_function

from warnings import warn

from lxml import etree as ET
from lxml.etree import XMLSyntaxError
import sys
import attr
import enum
import unicodedata


@attr.s(frozen=True)
class ExtractedText:
    segments = attr.ib()
    joiner = attr.ib(type=str)
    # TODO Use type annotations for attr.ib types when support for Python 3.5 is dropped
    # TODO Types are not validated (attr does not do this yet)

    @property
    def text(self):
        return self.joiner.join(s.text for s in self.segments)

    def segment_id_for_pos(self, pos):
        i = 0
        for s in self.segments:
            if i <= pos < i + len(s.text):
                return s.id
            i += len(s.text)
            if i <= pos < i + len(self.joiner):
                return None
            i += len(self.joiner)
        # XXX Cache results


class Normalization(enum.Enum):
    NFC = 1
    NFC_MUFI = 2


def normalize(text, normalization):
    if normalization == Normalization.NFC:
        return unicodedata.normalize('NFC', text)
    else:
        raise ValueError()


@attr.s(frozen=True)
class ExtractedTextSegment:
    id = attr.ib(type=str)
    text = attr.ib(type=str)
    @text.validator
    def check(self, attribute, value):
        if normalize(value, self.normalization) != value:
            raise ValueError('String "{}" is not normalized.'.format(value))
    normalization = attr.ib(converter=Normalization, default=Normalization.NFC)


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

    return ExtractedText((ExtractedTextSegment(None, line_text) for line_text in lines), '\n')
    # TODO This currently does not extract any segment id, because we are
    #      clueless about the ALTO format.
    # FIXME needs to handle normalization


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

    def region_text(region):
        try:
            return region.find('./page:TextEquiv/page:Unicode', namespaces=nsmap).text
        except AttributeError:
            return None

    region_texts = []
    reading_order = tree.find('.//page:ReadingOrder', namespaces=nsmap)
    if reading_order is not None:
        for group in reading_order.iterfind('./*', namespaces=nsmap):
            if ET.QName(group.tag).localname == 'OrderedGroup':
                region_ref_indexeds = group.findall('./page:RegionRefIndexed', namespaces=nsmap)
                for region_ref_indexed in sorted(region_ref_indexeds, key=lambda r: int(r.attrib['index'])):
                    region_id = region_ref_indexed.attrib['regionRef']
                    region = tree.find('.//page:TextRegion[@id="%s"]' % region_id, namespaces=nsmap)
                    if region is not None:
                        region_texts.append(region_text(region))
                    else:
                        warn('Not a TextRegion: "%s"' % region_id)
            else:
                raise NotImplementedError
    else:
        for region in tree.iterfind('.//page:TextRegion', namespaces=nsmap):
            region_texts.append(region_text(region))

    # XXX Does a file have to have regions etc.? region vs lines etc.
    # Filter empty region texts
    region_texts = (t for t in region_texts if t)
    return ExtractedText((ExtractedTextSegment(None, region_text) for region_text in region_texts), '\n')
    # TODO This currently does not extract any segment id
    # FIXME needs to handle normalization


def page_text(tree):
    return page_extract(tree).text


def text(filename):
    """Read the text from the given file.

    Supports PAGE, ALTO and falls back to plain text.
    """

    try:
        tree = ET.parse(filename)
    except XMLSyntaxError:
        with open(filename, 'r') as f:
            return f.read()
    try:
        return page_text(tree)
    except ValueError:
        return alto_text(tree)


if __name__ == '__main__':
    print(text(sys.argv[1]))
