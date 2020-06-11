import unicodedata
import pytest
from extracted_text import ExtractedText, ExtractedTextSegment
from uniseg.graphemecluster import grapheme_clusters
from qurator.dinglehopper import seq_align
from collections import namedtuple


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


AlignmentElement = namedtuple('AlignmentElement', 'left right left_id right_id')


def test_align():
    """
    Test aligning by character while retaining segment id info

    The difficulty here is that aligning should work on grapheme clusters,
    not Python characters.
    """

    test1 = ExtractedText([
        ExtractedTextSegment('s0', 'foo'),
        ExtractedTextSegment('s1', 'bar'),
        ExtractedTextSegment('s2', 'batzinga')
    ], ' ')
    test2 = ExtractedText([
        ExtractedTextSegment('x0', 'foo'),
        ExtractedTextSegment('x1', 'bar'),
        ExtractedTextSegment('x2', '.'),  # extra .
        ExtractedTextSegment('x3', 'bazim̃ga'),  # deletion + different grapheme cluster, m̃ also is two Python characters
    ], ' ')

    left_pos = 0; right_pos = 0; alignment = []
    for left, right in seq_align(grapheme_clusters(test1.text), grapheme_clusters(test2.text)):
        left_id = test1.segment_id_for_pos(left_pos) if left is not None else None
        right_id = test2.segment_id_for_pos(right_pos) if right is not None else None
        # XXX note that deletions and inserts only produce one id + None, UI must
        #     support this, i.e. display for the one id produced
        # XXX otherwise, it should always display for BOTH ids
        el = AlignmentElement(left, right, left_id, right_id)
        alignment.append(el)
        if left is not None:
            left_pos += len(left)
        if right is not None:
            right_pos += len(right)

    print('test1: {}'.format(test1.text))
    print('test2: {}'.format(test2.text))

    assert alignment[0]  == ('f',  'f',  's0', 'x0')
    assert alignment[8]  == (None, '.',  None, 'x2')
    assert alignment[12] == ('t',  None, 's2', None)
    assert alignment[15] == ('n',  'm̃',  's2', 'x3')
