import unicodedata

from .. import editops


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
