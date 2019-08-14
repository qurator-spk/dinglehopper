from __future__ import division, print_function

from lxml import etree as ET
import sys

from lxml.etree import XMLSyntaxError


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


def alto_text(tree):
    """Extract text from the given ALTO ElementTree."""

    nsmap = {'alto': alto_namespace(tree)}

    lines = (
        ' '.join(string.attrib.get('CONTENT') for string in line.iterfind('alto:String', namespaces=nsmap))
        for line in tree.iterfind('.//alto:TextLine', namespaces=nsmap))
    text_ = '\n'.join(lines)

    return text_


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


def page_text(tree):
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
                for region_ref_indexed in sorted(region_ref_indexeds, key=lambda r: r.attrib['index']):
                    region_id = region_ref_indexed.attrib['regionRef']
                    region = tree.find('.//page:TextRegion[@id="%s"]' % region_id, namespaces=nsmap)
                    if region is not None:
                        region_texts.append(region_text(region))
                    else:
                        raise ValueError('Invalid region id "%s" in file' % region_id)
            else:
                raise NotImplementedError
    else:
        for region in tree.iterfind('.//page:TextRegion', namespaces=nsmap):
            region_texts.append(region_text(region))

    # XXX Does a file have to have regions etc.? region vs lines etc.
    # Filter empty region texts
    region_texts = (t for t in region_texts if t)

    text_ = '\n'.join(region_texts)

    return text_


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
