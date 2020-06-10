import unicodedata
import pytest
from extracted_text import ExtractedText, ExtractedTextSegment


def test_text():
    test1 = ExtractedText([
        ExtractedTextSegment('s0', 'foo'),
        ExtractedTextSegment(1, 'bar'),
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
