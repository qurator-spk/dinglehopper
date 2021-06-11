import math
import unicodedata

from ...metrics import character_accuracy


def test_character_accuracy():
    assert character_accuracy("a", "a").error_rate == 0
    assert character_accuracy("a", "b").error_rate == 1 / 1
    assert character_accuracy("Foo", "Bar").error_rate == 3 / 3

    assert character_accuracy("Foo", "").error_rate == 3 / 3

    assert character_accuracy("", "").error_rate == 0
    assert math.isinf(character_accuracy("", "Foo").error_rate)

    assert character_accuracy("Foo", "Food").error_rate == 1 / 3
    assert character_accuracy("Fnord", "Food").error_rate == 2 / 5
    assert character_accuracy("Müll", "Mull").error_rate == 1 / 4
    assert character_accuracy("Abstand", "Sand").error_rate == 4 / 7


def test_character_accuracy_hard():
    s1 = unicodedata.normalize("NFC", "Schlyñ lorem ipsum.")
    s2 = unicodedata.normalize("NFD", "Schlyñ lorem ipsum!")  # Different, decomposed!
    assert character_accuracy(s1, s2).error_rate == 1 / 19

    s1 = "Schlyñ"
    assert (
        len(s1) == 6
    )  # This ends with LATIN SMALL LETTER N WITH TILDE, so 6 code points
    s2 = "Schlym̃"
    assert (
        len(s2) == 7
    )  # This, OTOH, ends with LATIN SMALL LETTER M + COMBINING TILDE, 7 code points

    # Both strings have the same length in terms of grapheme clusters.
    # So the CER should be symmetrical.
    assert character_accuracy(s2, s1).error_rate == 1 / 6
    assert character_accuracy(s1, s2).error_rate == 1 / 6
