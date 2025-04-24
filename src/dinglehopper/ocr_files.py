import os
import sys
from typing import Dict, Iterator, Optional

import chardet
from lxml import etree as ET
from lxml.etree import XMLSyntaxError
from ocrd_utils import getLogger
from uniseg.graphemecluster import grapheme_clusters

from .extracted_text import ExtractedText, normalize_sbb

log = getLogger("processor.OcrdDinglehopperEvaluate")


def alto_namespace(tree: ET._ElementTree) -> Optional[str]:
    """Return the ALTO namespace used in the given ElementTree.

    This relies on the assumption that, in any given ALTO file, the root element has the
    local name "alto". We do not check if the file uses any valid ALTO namespace.
    """
    root_name = ET.QName(tree.getroot().tag)
    if root_name.localname == "alto":
        assert isinstance(root_name.namespace, str)
        return root_name.namespace
    else:
        raise ValueError("Not an ALTO tree")


def alto_nsmap(tree: ET._ElementTree) -> Dict[str, str]:
    alto_ns = alto_namespace(tree)
    if alto_ns is None:
        raise ValueError("Could not determine ALTO namespace")
    return {"alto": alto_ns}


def alto_extract_lines(tree: ET._ElementTree) -> Iterator[ExtractedText]:
    nsmap = alto_nsmap(tree)
    for line in tree.iterfind(".//alto:TextLine", namespaces=nsmap):
        line_id = line.attrib.get("ID")
        line_text = " ".join(
            string.attrib.get("CONTENT", "")
            for string in line.iterfind("alto:String", namespaces=nsmap)
        )
        normalized_text = normalize_sbb(line_text)
        clusters = list(grapheme_clusters(normalized_text))
        yield ExtractedText(line_id, None, None, normalized_text, clusters)
        # FIXME hardcoded SBB normalization


def alto_extract(tree: ET._ElementTree) -> ExtractedText:
    """Extract text from the given ALTO ElementTree."""
    return ExtractedText(None, list(alto_extract_lines(tree)), "\n", None, None)


def alto_text(tree):
    return alto_extract(tree).text


def page_namespace(tree):
    """Return the PAGE content namespace used in the given ElementTree.

    This relies on the assumption that, in any given PAGE content file, the root element
    has the local name "PcGts". We do not check if the files uses any valid PAGE
    namespace.
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

    return ExtractedText(None, regions, "\n", None, None)


def extract_texts_from_reading_order_group(group, tree, nsmap, textequiv_level):
    """Recursive function to extract the texts from TextRegions in ReadingOrder."""
    regions = []

    if ET.QName(group.tag).localname in ["OrderedGroup", "OrderedGroupIndexed"]:
        ro_children = list(group)

        ro_children = [child for child in ro_children if "index" in child.attrib.keys()]
        ro_children = sorted(ro_children, key=lambda child: int(child.attrib["index"]))
    elif ET.QName(group.tag).localname in ["UnorderedGroup", "UnorderedGroupIndexed"]:
        ro_children = list(group)
    else:
        raise NotImplementedError

    for ro_child in ro_children:
        if ET.QName(ro_child.tag).localname in [
            "OrderedGroup",
            "OrderedGroupIndexed",
            "UnorderedGroup",
            "UnorderedGroupIndexed",
        ]:
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


def detect_encoding(filename):
    return chardet.detect(open(filename, "rb").read(1024))["encoding"]


def plain_extract(filename, include_filename_in_id=False, encoding="autodetect"):
    id_template = "{filename} - line {no}" if include_filename_in_id else "line {no}"

    def make_segment(no, line):
        normalized_text = normalize_sbb(line)
        clusters = list(grapheme_clusters(normalized_text))
        return ExtractedText(
            id_template.format(filename=os.path.basename(filename), no=no),
            None,
            None,
            normalized_text,
            clusters,
        )

    if encoding == "autodetect":
        fileencoding = detect_encoding(filename)
        log.warning(
            f"Autodetected encoding as '{fileencoding}'"
            ", it is recommended to specify it explicitly with --plain-encoding"
        )
    else:
        fileencoding = encoding
    with open(filename, "r", encoding=fileencoding) as f:
        return ExtractedText(
            None,
            [make_segment(no, line.strip()) for no, line in enumerate(f.readlines())],
            "\n",
            None,
            None,
        )
    # XXX hardcoded SBB normalization


def plain_text(filename, encoding="autodetect"):
    return plain_extract(filename, encoding=encoding).text


def extract(filename, *, textequiv_level="region", plain_encoding="autodetect"):
    """Extract the text from the given file.

    Supports PAGE, ALTO and falls back to plain text.
    """
    try:
        tree = ET.parse(filename)
    except (XMLSyntaxError, UnicodeDecodeError):
        return plain_extract(filename, encoding=plain_encoding)
    try:
        return page_extract(tree, textequiv_level=textequiv_level)
    except ValueError:
        return alto_extract(tree)


def text(filename):
    return extract(filename).text


if __name__ == "__main__":
    print(text(sys.argv[1]))
