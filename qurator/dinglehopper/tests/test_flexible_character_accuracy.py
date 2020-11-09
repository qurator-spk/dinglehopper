"""
Tests for the implementation of the flexible character accuracy

Citation:
    Flexible character accuracy measure for reading-order-independent evaluation
    C. Clausner, S. Pletschacher, A. Antonacopoulos
    Pattern Recognition Letters, Volume 131, March 2020, Pages 390-397
Link: http://www.primaresearch.org/publications/PRL_Clausner_FlexibleCharacterAccuracy
DOI: 10.1016/j.patrec.2020.02.003
"""

import pytest

from ..flexible_character_accuracy import *

CASE_ARGS = "gt,ocr,first_line_score,all_line_score"

SIMPLE_CASES = [
    ("a", "", 0, 0),
    ("a", "a", 1, 1),
    ("a\nb", "a\nb", 1, 1),
    ("a\nb", "b\na", 1, 1),
    ("aaa\nbbb\nccc", "ccc\naaa\nbbb", 1, 1),
    ("aaa\nbbb\nccc", "aaa\nbbb", 1, 1 - 3 / 9),
    ("bbb", "aaa\nbbb\nccc", 1, 1 - 6 / 3),
    ("a", "a\nbb\nccc", 1, 1 - 5 / 1),
    ("bb", "a\nbb\nccc", 1, 1 - 4 / 2),
]

COMPLEX_CASES = [
    ("accc", "a\nbb\nccc", 0, 1 - 2 / 4),
    ("aaa\nbbb\nccc", "bbb", 1, 1 - 6 / 9),
]

EXTENDED_CASES = [
    # A: No errors
    ((0, 1, 2, 3, 4, 11, 5, 6, 7, 8, 9),
     (0, 1, 2, 3, 4, 11, 5, 6, 7, 8, 9),
     1, 1),
    # B: Different ordering of text blocks
    ((0, 1, 2, 3, 4, 11, 5, 6, 7, 8, 9),
     (5, 6, 7, 8, 9, 11, 0, 1, 2, 3, 4),
     1, 1),
    # C: Merge across columns
    ((0, 1, 2, 11, 3, 4, 11, 5, 6, 7, 11, 8, 9),
     (0, 1, 2, 5, 6, 7, 11, 3, 4, 8, 9),
     1, 0.964),
    # D: Over-segmentation
    ((0, 1, 2, 3, 4, 11, 5, 6, 7, 8, 9),
     (0, 1, 2, 11, 5, 6, 7, 11, 3, 4, 11, 8, 9),
     1, 0.966),
    # E: Part missing
    ((0, 1, 2, 3, 4, 11, 5, 6, 7, 8, 9),
     (0, 1, 2, 3, 4),
     1, 0.50),
    # E.2: Part missing
    ((0, 1, 2, 3, 4, 11, 5, 6, 7, 8, 9),
     (5, 6, 7, 8, 9),
     1, 0.50),
    # F: All missing
    ((0, 1, 2, 3, 4, 11, 5, 6, 7, 8, 9),
     (),
     1, 0),
    # G: Added parts
    ((0, 1, 2, 3, 4),
     (0, 1, 2, 3, 4, 11, 5, 6),
     1, 0.621),
]

EDIT_ARGS = "gt,ocr,expected_dist"

SIMPLE_EDITS = [
    (Part(text="a").substring(), Part(text="a"), Distance(match=1)),
    (Part(text="a").substring(), Part(text="b"), Distance(replace=1)),
    (Part(text="abcd").substring(), Part(text="beed"),
     Distance(match=2, replace=1, insert=1, delete=1)),
]


def extended_case_to_text(gt, ocr):
    sentence = ("Eight", "happy", "frogs", "scuba", "dived",
                "Jenny", "chick", "flaps", "white", "wings",
                "", "\n")

    gt_sentence = " ".join(sentence[i] for i in gt).replace(" \n ", "\n")
    ocr_sentence = " ".join(sentence[i] for i in ocr).replace(" \n ", "\n")
    return gt_sentence, ocr_sentence


@pytest.mark.parametrize(CASE_ARGS, [*SIMPLE_CASES, *COMPLEX_CASES])
def test_flexible_character_accuracy_simple(gt, ocr, first_line_score, all_line_score):
    score, _ = flexible_character_accuracy(gt, ocr)
    assert score == pytest.approx(all_line_score)


@pytest.mark.xfail
@pytest.mark.parametrize("ocr", [
    "1 hav\nnospecial\ntalents.\nI am one\npassionate\ncuriousity.\"\nAlberto\nEmstein",
    "1 hav\nnospecial\ntalents. Alberto\nI am one Emstein\npassionate\ncuriousity.\"",
    "Alberto\nEmstein\n1 hav\nnospecial\ntalents.\nI am one\npassionate\ncuriousity.\""
])
def test_flexible_character_accuracy(ocr):
    """Tests from figure 3 in the paper.

    TODO: We have a 2 percent deviation from the original because of redistributed
          one character alignments (e.g. the y-insert replaces the y-delete).
    """
    gt = """"I have
no special
talent.
I am only
passionately
curious."
Albert
Einstein
"""
    replacements = 3
    inserts = 5
    deletes = 7
    chars = len(gt) - gt.count("\n")
    assert replacements + inserts + deletes == 15
    edits = Distance(match=chars - deletes - replacements, replace=replacements,
                     insert=inserts, delete=deletes)
    expected = character_accuracy(edits)
    assert expected == pytest.approx(0.779, abs=0.0005)
    result, matches = flexible_character_accuracy(gt, ocr)
    assert result == pytest.approx(expected, abs=0.0005)


@pytest.mark.parametrize(CASE_ARGS, EXTENDED_CASES)
def test_flexible_character_accuracy_extended(gt, ocr, first_line_score,
                                              all_line_score):
    """Tests from figure 4 in the paper."""
    gt_sentence, ocr_sentence = extended_case_to_text(gt, ocr)
    result, _ = flexible_character_accuracy(gt_sentence, ocr_sentence)
    assert result == pytest.approx(all_line_score, abs=0.001)


@pytest.mark.parametrize(CASE_ARGS, [*SIMPLE_CASES, *COMPLEX_CASES, *EXTENDED_CASES])
def test_match_with_coefficients(gt, ocr, first_line_score, all_line_score):
    coef = Coefficients()
    if not isinstance(gt, str):
        gt, ocr = extended_case_to_text(gt, ocr)
    matches = match_with_coefficients(gt, ocr, coef)
    score = character_accuracy_for_matches(matches)
    assert score == pytest.approx(all_line_score, abs=0.001)


@pytest.mark.parametrize(CASE_ARGS, [*SIMPLE_CASES, *COMPLEX_CASES])
def test_match_longest_gt_lines(gt, ocr, first_line_score, all_line_score):
    coef = Coefficients()
    gt_lines = initialize_lines(gt)
    ocr_lines = initialize_lines(ocr)
    match = match_longest_gt_lines(gt_lines, ocr_lines, coef)
    score = 0
    if match:
        score = character_accuracy(match.dist)
    assert score == pytest.approx(first_line_score)


@pytest.mark.parametrize(CASE_ARGS, [
    *SIMPLE_CASES,
    ("accc", "a\nbb\nccc", 1.0, 1.0),
])
def test_match_gt_line(gt, ocr, first_line_score, all_line_score):
    coef = Coefficients()
    gt_lines = initialize_lines(gt)
    ocr_lines = initialize_lines(ocr)
    match, _ = match_gt_line(gt_lines[0], ocr_lines, coef)
    score = 0
    if match:
        score = character_accuracy(match.dist)
    assert score == pytest.approx(first_line_score)


@pytest.mark.parametrize("original,match,expected_lines", [
    (Part(), Part(), []),
    (Part(text="abc"), Part(), [Part(text="abc")]),
    (Part(text="abc"), Part("d"), [Part(text="bc", start=1)]),
    (Part(text="abc"), Part("a", start=100), [Part(text="abc")]),
    (Part(text="abc"), Part("a"), [Part(text="bc", start=1)]),
    (Part(text="abc"), Part("b", start=1), [Part(text="a"), Part(text="c", start=2)]),
    (Part(text="abc"), Part("c", start=2), [Part(text="ab")]),
])
def test_remove_or_split(original, match, expected_lines):
    lines = [original]
    splitted = remove_or_split(original, match, lines)
    assert splitted == (len(lines) > 0)
    assert lines == expected_lines


@pytest.mark.parametrize(EDIT_ARGS, [
    *SIMPLE_EDITS,
    (Part(text="aaabbbaaa"), Part(text="bbb"), Distance(match=3)),
    (Part(text="bbb"), Part(text="aaabbbaaa"), Distance(match=3)),
    (Part(text=""), Part(text=""), None)
])
def test_match_lines(gt, ocr, expected_dist):
    match = match_lines(gt, ocr)
    if not expected_dist:
        assert match is None
    else:
        assert match.gt.text in gt.text
        assert match.ocr.text in ocr.text
        assert match.dist == expected_dist


@pytest.mark.parametrize(EDIT_ARGS, [
    *SIMPLE_EDITS,
    (Part(text="").substring(), Part(text=""), Distance()),
    (Part(text="ab").substring(), Part("a"), Distance(match=1, delete=1)),
    (Part(text="a").substring(), Part("ab"), Distance(match=1, insert=1)),
])
def test_distance(gt, ocr, expected_dist):
    match = distance(gt, ocr)
    assert match.gt == gt
    assert match.ocr == ocr
    assert match.dist == expected_dist


@pytest.mark.parametrize("matches,expected_dist", [
    ([], 1),
    ([Match(gt=Part(text=""), ocr=Part(text=""), dist=Distance(), ops=[])], 1),
    ([Match(gt=Part(text="abee"), ocr=Part("ac"),
            dist=Distance(match=1, replace=1, delete=2), ops=[]),
      Match(gt=Part(text="cd"), ocr=Part("ceff"),
            dist=Distance(match=1, replace=1, insert=2), ops=[])],
     1 - 6 / 6),
])
def test_character_accuracy_matches(matches, expected_dist):
    assert character_accuracy_for_matches(matches) == pytest.approx(expected_dist)


@pytest.mark.parametrize("dist,expected_dist", [
    (Distance(), 1),
    (Distance(match=1), 1),
    (Distance(replace=1), 0),
    (Distance(match=1, insert=1), 0),
    (Distance(match=1, insert=2), 1 - 2 / 1),
    (Distance(match=2, insert=1), 0.5),
    (Distance(match=1, delete=1), 0.5),
])
def test_character_accuracy_dist(dist, expected_dist):
    assert character_accuracy(dist) == pytest.approx(expected_dist)


@pytest.mark.parametrize("line,subline,expected_rest", [
    (Part(), Part(), []),
    (Part("aaa bbb"), Part("aaa bbb"), []),
    (Part("aaa bbb"), Part("aaa"), [Part(" bbb", start=3)]),
    (Part("aaa bbb"), Part("bbb", start=4), [Part("aaa ")]),
    (Part("aaa bbb", start=3), Part("aaa", start=3), [Part(" bbb", start=6)]),
    (Part("aaa bbb", start=3), Part("bbb", start=7), [Part("aaa ", start=3)]),
    (Part("aaa bbb ccc"), Part("bbb", start=4), [Part("aaa "), Part(" ccc", start=7)]),
    (Part("aaa bbb ccc", start=3), Part("bbb", start=7),
     [Part("aaa ", start=3), Part(" ccc", start=10)]),
    (Part("aaa bbb"), Part(" ", start=3), [Part("aaa"), Part("bbb", start=4)]),
    (Part("aaa bbb", start=3), Part(" ", start=6),
     [Part("aaa", start=3), Part("bbb", start=7)]),
])
def test_split_line(line, subline, expected_rest):
    rest = line.split(subline)
    assert len(rest) == len(expected_rest)
    assert set(rest) == set(expected_rest)


def test_initialize_lines():
    lines = initialize_lines("")
    assert lines == []

    lines = initialize_lines("22\n1\n333")
    line1 = Part(text="22", line=0, start=0)
    line2 = Part("1", line=1, start=0)
    line3 = Part("333", line=2, start=0)
    assert lines == [line3, line1, line2]


@pytest.mark.xfail
def test_combine_lines():
    assert False


@pytest.mark.parametrize("line,start,end,expected", [
    (Part(text=""), 0, None, Part(text="")),
    (Part(text="a"), 0, None, Part(text="a")),
    (Part(text="ab"), 0, 1, Part(text="a")),
    (Part(text="abc"), 0, -1, Part(text="ab")),
    (Part(text="ab"), 1, None, Part(text="b", start=1)),
])
def test_line_substring(line, start, end, expected):
    assert line.substring(rel_start=start, rel_end=end) == expected
