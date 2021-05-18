from __future__ import division, print_function

from typing import Iterator
from warnings import warn
import sys

from lxml import etree as ET
from lxml.etree import XMLSyntaxError

from .extracted_text import ExtractedText, normalize_sbb


def alto_namespace(tree: ET.ElementTree) -> str:
    """Return the ALTO namespace used in the given ElementTree.

    This relies on the assumption that, in any given ALTO file, the root element has the local name "alto". We do not
    check if the files uses any valid ALTO namespace.
    """
    root_name = ET.QName(tree.getroot().tag)
    if root_name.localname == "alto":
        return root_name.namespace
    else:
        raise ValueError("Not an ALTO tree")


def alto_extract_lines(tree: ET.ElementTree) -> Iterator[ExtractedText]:
    nsmap = {"alto": alto_namespace(tree)}
    for line in tree.iterfind(".//alto:TextLine", namespaces=nsmap):
        line_id = line.attrib.get("ID")
        line_text = " ".join(
            string.attrib.get("CONTENT")
            for string in line.iterfind("alto:String", namespaces=nsmap)
        )
        yield ExtractedText(line_id, None, None, normalize_sbb(line_text))
        # FIXME hardcoded SBB normalization


def alto_extract(tree: ET.ElementTree) -> ExtractedText:
    """Extract text from the given ALTO ElementTree."""
    return ExtractedText(None, list(alto_extract_lines(tree)), "\n", None)


def alto_text(tree):
    return alto_extract(tree).text


def page_namespace(tree):
    """Return the PAGE content namespace used in the given ElementTree.

    This relies on the assumption that, in any given PAGE content file, the root element has the local name "PcGts". We
    do not check if the files uses any valid PAGE namespace.
    """
    root_name = ET.QName(tree.getroot().tag)
    if root_name.localname == "PcGts":
        return root_name.namespace
    else:
        raise ValueError("Not a PAGE tree")


def page_extract(tree, *, textequiv_level="region"):
    """Extract text from the given PAGE content ElementTree."""

    # Internally, this is just parsing the Reading Order (if it exists) and
    # and leaves reading the TextRegions to ExtractedText.from_text_segment().

    nsmap = {"page": page_namespace(tree)}

    regions = []
    reading_order = tree.find(".//page:ReadingOrder", namespaces=nsmap)
    if reading_order is not None:
        for group in reading_order.iterfind("./*", namespaces=nsmap):
            regions.extend(
                extract_texts_from_reading_order_group(
                    group, tree, nsmap, textequiv_level
                )
            )
    else:
        for region in tree.iterfind(".//page:TextRegion", namespaces=nsmap):
            regions.append(
                ExtractedText.from_text_segment(
                    region, nsmap, textequiv_level=textequiv_level
                )
            )

    # Filter empty region texts
    regions = [r for r in regions if r.text != ""]

    return ExtractedText(None, regions, "\n", None)


def extract_texts_from_reading_order_group(group, tree, nsmap, textequiv_level):
    """Recursive function to extract the texts from TextRegions in ReadingOrder."""
    regions = []

    if ET.QName(group.tag).localname in ["OrderedGroup", "OrderedGroupIndexed"]:
        ro_children = list(group)

        ro_children = filter(lambda child: "index" in child.attrib.keys(), ro_children)
        ro_children = sorted(ro_children, key=lambda child: int(child.attrib["index"]))
    elif ET.QName(group.tag).localname in ["UnorderedGroup","UnorderedGroupIndexed"]:
        ro_children = list(group)
    else:
        raise NotImplementedError


    for ro_child in ro_children:
        if ET.QName(ro_child.tag).localname in ["OrderedGroup", "OrderedGroupIndexed", "UnorderedGroup", "UnorderedGroupIndexed"]:
            regions.extend(
                extract_texts_from_reading_order_group(
                    ro_child, tree, nsmap, textequiv_level
                )
            )
        else:
            region_id = ro_child.attrib["regionRef"]
            region = tree.find(
                './/page:TextRegion[@id="%s"]' % region_id, namespaces=nsmap
            )
            if region is not None:
                regions.append(
                    ExtractedText.from_text_segment(
                        region, nsmap, textequiv_level=textequiv_level
                    )
                )
            else:
                pass  # Not a TextRegion
    return regions


def page_text(tree, *, textequiv_level="region"):
    return page_extract(tree, textequiv_level=textequiv_level).text


def plain_extract(filename):
    with open(filename, "r") as f:
        return ExtractedText(
            None,
            [
                ExtractedText("line %d" % no, None, None, normalize_sbb(line))
                for no, line in enumerate(f.readlines())
            ],
            "\n",
            None,
        )
    # XXX hardcoded SBB normalization


def plain_text(filename):
    return plain_extract(filename).text


def extract(filename, *, textequiv_level="region"):
    """Extract the text from the given file.

    Supports PAGE, ALTO and falls back to plain text.
    """
    try:
        tree = ET.parse(filename)
    except XMLSyntaxError:
        return plain_extract(filename)
    try:
        return page_extract(tree, textequiv_level=textequiv_level)
    except ValueError:
        return alto_extract(tree)


def text(filename):
    return extract(filename).text


if __name__ == "__main__":
    print(text(sys.argv[1]))
