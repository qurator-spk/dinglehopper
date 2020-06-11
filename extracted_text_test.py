import unicodedata
import pytest
from extracted_text import ExtractedText, ExtractedTextSegment
from uniseg.graphemecluster import grapheme_clusters
from qurator.dinglehopper import seq_align


def test_text():
    test1 = ExtractedText([
        ExtractedTextSegment('s0', 'foo'),
        ExtractedTextSegment('s1', 'bar'),
        ExtractedTextSegment('s2', 'bazinga')
    ], ' ')

    assert test1.text == 'foo bar bazinga'
    assert test1.segment_id_for_pos(0) == 's0'
    assert test1.segment_id_for_pos(3) is None
    assert test1.segment_id_for_pos(10) == 's2'


def test_normalization_check():
    with pytest.raises(ValueError, match=r'.*is not normalized.*'):
        ExtractedTextSegment('foo', unicodedata.normalize('NFD', 'Schlyñ'))
    assert ExtractedTextSegment('foo', unicodedata.normalize('NFC', 'Schlyñ'))


def test_align():
    """
    Test aligning by character while retaining segment id info

    The difficulty here is that aligning should work on grapheme clusters,
    not Python characters.
    """

    test1 = ExtractedText([
        ExtractedTextSegment('s0', 'foo'),
        ExtractedTextSegment('s1', 'bar'),
        ExtractedTextSegment('s2', 'bazinga')
    ], ' ')
    test2 = ExtractedText([
        ExtractedTextSegment('x0', 'foo'),
        ExtractedTextSegment('x1', 'bar'),
        ExtractedTextSegment('x2', '.'),  # extra .
        ExtractedTextSegment('x2', 'bazim̃ga'),  # different grapheme cluster, m̃ also is two Python characters
    ], ' ')

    left_pos = 0; right_pos = 0
    for left, right in seq_align(grapheme_clusters(test1.text), grapheme_clusters(test2.text)):
        print(left, right, test1.segment_id_for_pos(left_pos), test2.segment_id_for_pos(right_pos))
        if left is not None:
            left_pos += len(left)
        if right is not None:
            right_pos += len(right)
    assert False
