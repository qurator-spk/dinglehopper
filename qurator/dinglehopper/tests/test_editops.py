import unicodedata

from .. import seq_editops, editops


def test_trivial():
    assert seq_editops("abc", "abc") == []
    assert seq_editops("", "") == []


def test_insert():
    assert seq_editops("bc", "abc") == [("insert", 0, 0)]
    assert seq_editops("ac", "abc") == [("insert", 1, 1)]
    assert seq_editops("ab", "abc") == [("insert", 2, 2)]
    assert seq_editops("", "a") == [("insert", 0, 0)]


def test_multiple():
    assert seq_editops("bcd", "abce") == [("insert", 0, 0), ("replace", 2, 3)]


def test_delete():
    assert seq_editops("abcdef", "cdef") == [("delete", 0, 0), ("delete", 1, 0)]
    assert seq_editops("Xabcdef", "Xcdef") == [("delete", 1, 1), ("delete", 2, 1)]
    assert seq_editops("abcdefg", "acdefX") == [("delete", 1, 1), ("replace", 6, 5)]
    assert seq_editops("abcde", "aabcd") == [("insert", 1, 1), ("delete", 4, 5)]
    assert seq_editops("Foo", "") == [
        ("delete", 0, 0),
        ("delete", 1, 0),
        ("delete", 2, 0),
    ]
    assert seq_editops("Foolish", "Foo") == [
        ("delete", 3, 3),
        ("delete", 4, 3),
        ("delete", 5, 3),
        ("delete", 6, 3),
    ]


def test_ambiguous():
    assert seq_editops("bcd", "abcef") == [
        ("insert", 0, 0),
        ("replace", 2, 3),
        ("insert", 3, 4),
    ]


def test_editops():
    """Test editops() in cases where dealing with grapheme clusters matters"""

    # In these cases, one of the words has a composed form, the other one does not.
    assert editops("Schlyñ", "Schlym̃") == [("replace", 5, 5)]
    assert editops("oͤde", "öde") == [("replace", 0, 0)]


def test_editops_canonically_equivalent():
    left = unicodedata.lookup("LATIN SMALL LETTER N") + unicodedata.lookup(
        "COMBINING TILDE"
    )
    right = unicodedata.lookup("LATIN SMALL LETTER N WITH TILDE")
    assert left != right
    assert unicodedata.normalize("NFC", left) == unicodedata.normalize("NFC", right)
    assert editops(left, right) == []
