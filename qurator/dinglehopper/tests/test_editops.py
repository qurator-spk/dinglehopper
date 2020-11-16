import unicodedata

import pytest

from .. import editops, editops_fast

TEST_PARAMS = "s1,s2,expected_ops"

TEST_STRINGS = [
    # trivial
    ("abc", "abc", []),
    ("", "", []),
    # insert
    ("bc", "abc", [("insert", 0, 0)]),
    ("ac", "abc", [("insert", 1, 1)]),
    ("ab", "abc", [("insert", 2, 2)]),
    ("", "a", [("insert", 0, 0)]),
    # delete
    ("abcdef", "cdef", [("delete", 0, 0), ("delete", 1, 0)]),
    ("Xabcdef", "Xcdef", [("delete", 1, 1), ("delete", 2, 1)]),
    ("abcdefg", "acdefX", [("delete", 1, 1), ("replace", 6, 5)]),
    ("abcde", "aabcd", [("insert", 1, 1), ("delete", 4, 5)]),
    ("Foo", "", [("delete", 0, 0), ("delete", 1, 0), ("delete", 2, 0)]),
    (
        "Foolish",
        "Foo",
        [("delete", 3, 3), ("delete", 4, 3), ("delete", 5, 3), ("delete", 6, 3)],
    ),
    # multiple
    ("bcd", "abce", [("insert", 0, 0), ("replace", 2, 3)]),
    # ambiguous
    ("bcd", "abcef", [("insert", 0, 0), ("insert", 2, 3), ("replace", 2, 4)]),
]

TEST_SEQUENCES = [
    (["a", "ab"], ["a", "ab", "c"], [("insert", 2, 2)]),
    (["a", "ab"], ["a", "c"], [("replace", 1, 1)]),
]

TEST_UNICODE = [
    # In these cases, one of the words has a composed form, the other one does not.
    ("Schlyñ", "Schlym̃", [("replace", 5, 5)]),
    ("oͤde", "öde", [("replace", 0, 0)]),
    # equal
    (
        unicodedata.lookup("LATIN SMALL LETTER N")
        + unicodedata.lookup("COMBINING TILDE"),
        unicodedata.lookup("LATIN SMALL LETTER N WITH TILDE"),
        [],
    ),
]


@pytest.mark.parametrize(TEST_PARAMS, TEST_STRINGS)
def test_editops_strings(s1, s2, expected_ops):
    ops = editops(s1, s2)
    assert ops == expected_ops


@pytest.mark.parametrize(TEST_PARAMS, [*TEST_STRINGS, *TEST_SEQUENCES])
def test_editops_sequences(s1, s2, expected_ops):
    ops = editops(s1, s2)
    assert ops == expected_ops


@pytest.mark.parametrize(TEST_PARAMS, TEST_STRINGS)
def test_editops_fast(s1, s2, expected_ops):
    ops = editops_fast(s1, s2)
    assert ops == expected_ops


@pytest.mark.parametrize(TEST_PARAMS, TEST_UNICODE)
def test_editops_fast_unicode(s1, s2, expected_ops):
    ops = editops_fast(s1, s2)
    assert ops != expected_ops


@pytest.mark.parametrize(TEST_PARAMS, TEST_UNICODE)
def test_editops_unicode(s1, s2, expected_ops):
    """Test editops() in cases where dealing with grapheme clusters matters"""

    if not expected_ops:
        assert s1 != s2
        assert unicodedata.normalize("NFC", s1) == unicodedata.normalize("NFC", s2)
    ops = editops(s1, s2)
    assert ops == expected_ops
