from __future__ import division, print_function

import unicodedata

import pytest

from .. import levenshtein, distance


TEST_PARAMS = "seq1,seq2,expected_dist"

TEST_STRINGS = [
    ("a", "a", 0),
    ("a", "b", 1),
    ("Foo", "Bar", 3),
    ("", "", 0),
    ("Foo", "", 3),
    ("", "Foo", 3),
    ("Foo", "Food", 1),
    ("Fnord", "Food", 2),
    ("Müll", "Mull", 1),
    ("Abstand", "Sand", 4),
]

TEST_SEQUENCES = [(["a", "ab"], ["a", "ab", "c"], 1), (["a", "ab"], ["a", "c"], 1)]


@pytest.mark.parametrize(TEST_PARAMS, [*TEST_STRINGS, *TEST_SEQUENCES])
def test_distance_sequences(seq1, seq2, expected_dist):
    dist = distance(seq1, seq2)
    assert dist == expected_dist


@pytest.mark.parametrize(TEST_PARAMS, TEST_STRINGS)
def test_distance(seq1, seq2, expected_dist):
    dist = distance(seq1, seq2)
    assert dist == expected_dist


def test_distance_unicode_wide():
    word1 = unicodedata.normalize("NFC", "Schlyñ")
    word2 = unicodedata.normalize("NFD", "Schlyñ")  # Different, decomposed!
    assert distance(word1, word2) == 0

    word1 = "Schlyñ"
    assert (
        len(word1) == 6
    )  # This ends with LATIN SMALL LETTER N WITH TILDE, so 6 code points
    word2 = "Schlym̃"
    assert (
        len(word2) == 7
    )  # This, OTOH, ends with LATIN SMALL LETTER M + COMBINING TILDE, 7 code points
    assert distance(word1, word2) == 1
