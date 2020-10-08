import unicodedata
import pytest
from qurator.dinglehopper import ExtractedText
from uniseg.graphemecluster import grapheme_clusters
from qurator.dinglehopper import seq_align
from collections import namedtuple


def test_text():
    test1 = ExtractedText(None, [
        ExtractedText('s0', None, None, 'foo'),
        ExtractedText('s1', None, None, 'bar'),
        ExtractedText('s2', None, None, 'bazinga')
    ], ' ', None)

    assert test1.text == 'foo bar bazinga'
    assert test1.segment_id_for_pos(0) == 's0'
    assert test1.segment_id_for_pos(3) is None
    assert test1.segment_id_for_pos(10) == 's2'


def test_normalization_check():
    with pytest.raises(ValueError, match=r'.*is not in NFC.*'):
        ExtractedText('foo', None, None, unicodedata.normalize('NFD', 'Schlyñ'))
    assert ExtractedText('foo', None, None, unicodedata.normalize('NFC', 'Schlyñ'))


AlignmentElement = namedtuple('AlignmentElement', 'left right left_id right_id')


def test_align():
    """
    Test aligning by character while retaining segment id info

    The difficulty here is that aligning should work on grapheme clusters,
    not Python characters.
    """

    test1 = ExtractedText(None, [
        ExtractedText('s0', None, None, 'foo'),
        ExtractedText('s1', None, None, 'bar'),
        ExtractedText('s2', None, None, 'batzinga')
    ], ' ', None)
    test2 = ExtractedText(None, [
        ExtractedText('x0', None, None, 'foo'),
        ExtractedText('x1', None, None, 'bar'),
        ExtractedText('x2', None, None, '.'),  # extra .
        ExtractedText('x3', None, None, 'bazim̃ga'),  # deletion + different grapheme cluster, m̃ also is two Python characters
    ], ' ', None)

    left_pos = 0; right_pos = 0; alignment = []
    for left, right in seq_align(grapheme_clusters(test1.text), grapheme_clusters(test2.text)):
        left_id = test1.segment_id_for_pos(left_pos) if left is not None else None
        right_id = test2.segment_id_for_pos(right_pos) if right is not None else None
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
