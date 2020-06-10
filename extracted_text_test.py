from extracted_text import *

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

# TODO handle grapheme cluster positions?

# ExtractedTextSegment('foo', unicodedata.normalize('NFD', 'Schlyñ'))
ExtractedTextSegment('foo', unicodedata.normalize('NFC', 'Schlyñ'))
