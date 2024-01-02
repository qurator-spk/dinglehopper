import logging
import unicodedata
from collections import namedtuple

import pytest
from lxml import etree as ET
from uniseg.graphemecluster import grapheme_clusters

from .. import ExtractedText, seq_align


def test_text():
    test1 = ExtractedText(
        None,
        [
            ExtractedText("s0", None, None, "foo", grapheme_clusters("foo")),
            ExtractedText("s1", None, None, "bar", grapheme_clusters("bar")),
            ExtractedText("s2", None, None, "bazinga", grapheme_clusters("bazinga")),
        ],
        " ",
        None,
        None,
    )

    assert test1.text == "foo bar bazinga"
    assert test1.segment_id_for_pos(0) == "s0"
    assert test1.segment_id_for_pos(3) is None
    assert test1.segment_id_for_pos(10) == "s2"


def test_normalization_check():
    with pytest.raises(ValueError, match=r".*is not in NFC.*"):
        ExtractedText(
            "foo",
            None,
            None,
            unicodedata.normalize("NFD", "Schlyñ"),
            grapheme_clusters(unicodedata.normalize("NFD", "Schlyñ")),
        )
    assert ExtractedText(
        "foo",
        None,
        None,
        unicodedata.normalize("NFC", "Schlyñ"),
        grapheme_clusters(unicodedata.normalize("NFC", "Schlyñ")),
    )


AlignmentElement = namedtuple("AlignmentElement", "left right left_id right_id")


def test_align():
    """
    Test aligning by character while retaining segment id info

    The difficulty here is that aligning should work on grapheme clusters,
    not Python characters.
    """

    test1 = ExtractedText(
        None,
        [
            ExtractedText("s0", None, None, "foo", grapheme_clusters("foo")),
            ExtractedText("s1", None, None, "bar", grapheme_clusters("bar")),
            ExtractedText("s2", None, None, "batzinga", grapheme_clusters("batzinga")),
        ],
        " ",
        None,
        None,
    )
    test2 = ExtractedText(
        None,
        [
            ExtractedText("x0", None, None, "foo", grapheme_clusters("foo")),
            ExtractedText("x1", None, None, "bar", grapheme_clusters("bar")),
            # extra .
            ExtractedText("x2", None, None, ".", grapheme_clusters(".")),
            # deletion + different grapheme cluster, m̃ also is two Python characters
            ExtractedText("x3", None, None, "bazim̃ga", grapheme_clusters("bazim̃ga")),
        ],
        " ",
        None,
        None,
    )

    left_pos = 0
    right_pos = 0
    alignment = []
    for left, right in seq_align(
        grapheme_clusters(test1.text), grapheme_clusters(test2.text)
    ):
        left_id = test1.segment_id_for_pos(left_pos) if left is not None else None
        right_id = test2.segment_id_for_pos(right_pos) if right is not None else None
        el = AlignmentElement(left, right, left_id, right_id)
        alignment.append(el)
        if left is not None:
            left_pos += len(left)
        if right is not None:
            right_pos += len(right)

    print("test1: {}".format(test1.text))
    print("test2: {}".format(test2.text))

    assert alignment[0] == ("f", "f", "s0", "x0")
    assert alignment[8] == (None, ".", None, "x2")
    assert alignment[12] == ("t", None, "s2", None)
    assert alignment[15] == ("n", "m̃", "s2", "x3")


@pytest.mark.parametrize(
    "attributes,expected_index,expected_log",
    [
        ([], None, None),
        (['index="0"'], 0, None),
        ([""], 0, None),
        (['conf="0.5"'], 0, None),
        (['index="1"', 'index="0"'], 1, None),
        (['index="0" conf="0.4"', 'conf="0.5"'], 0, "TextEquiv without index"),
        (
            ['conf="0.4"', 'conf="0.5"', 'conf="0.9"'],
            2,
            "No index attributes, use 'conf' attribute to sort TextEquiv",
        ),
        (['index="0"', ""], 0, "TextEquiv without index"),
        (
            ["", 'conf="0.4"'],
            1,
            "No index attributes, use 'conf' attribute to sort TextEquiv",
        ),
        (["", ""], 0, "No index attributes, use first TextEquiv"),
    ],
)
def test_textequiv(attributes, expected_index, expected_log, caplog):
    """Test that extracting text from a PAGE TextEquiv is working without index attr."""
    caplog.set_level(logging.INFO)
    xml = '<?xml version="1.0"?>'
    ns = "http://schema.primaresearch.org/PAGE/gts/pagecontent/2018-07-15"
    text = ["Text {0}".format(i) for i in range(len(attributes) + 1)]

    equiv = [
        "<TextEquiv {0}><Unicode>{1}</Unicode></TextEquiv>".format(attr, text[i])
        for i, attr in enumerate(attributes)
    ]

    textline = '{0}<TextLine id="l3" xmlns="{1}">{2}</TextLine>'
    textline = textline.format(xml, ns, "".join(equiv))

    root = ET.fromstring(textline)
    result = ExtractedText.from_text_segment(
        root, {"page": ns}, textequiv_level="line"
    ).text
    if expected_index is None:
        assert not result
    else:
        assert result == text[expected_index]

    if expected_log is None:
        assert "no_index" not in caplog.text
    else:
        assert expected_log in caplog.text
