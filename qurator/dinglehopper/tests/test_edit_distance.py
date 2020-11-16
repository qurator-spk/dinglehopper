import unicodedata

import pytest

from .. import distance, distance_unicode


TEST_PARAMS = "s1,s2,expected_dist"

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

TEST_UNICODE = [
    # Different, decomposed!
    (unicodedata.normalize("NFC", "Schlyñ"), unicodedata.normalize("NFD", "Schlyñ"), 0),
    # Same decomposition
    (
        # This ends with LATIN SMALL LETTER N WITH TILDE, so 6 code points
        "Schlyñ",
        # This, OTOH, ends with LATIN SMALL LETTER M + COMBINING TILDE, 7 code points
        "Schlym̃",
        1,
    ),
]


@pytest.mark.parametrize(TEST_PARAMS, [*TEST_STRINGS, *TEST_SEQUENCES])
def test_distance_sequences(s1, s2, expected_dist):
    dist = distance(s1, s2)
    assert dist == expected_dist


@pytest.mark.parametrize(TEST_PARAMS, TEST_UNICODE)
def test_distance_with_unicode(s1, s2, expected_dist):
    dist = distance(s1, s2)
    assert dist != expected_dist


@pytest.mark.parametrize(TEST_PARAMS, TEST_UNICODE)
def test_distance_unicode(s1, s2, expected_dist):
    dist = distance_unicode(s1, s2)
    assert dist == expected_dist
