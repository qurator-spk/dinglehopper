from __future__ import division, print_function

import math
import unicodedata

from .. import character_error_rate


def test_character_error_rate():
    assert character_error_rate("a", "a") == 0
    assert character_error_rate("a", "b") == 1 / 1
    assert character_error_rate("Foo", "Bar") == 3 / 3

    assert character_error_rate("Foo", "") == 3 / 3

    assert character_error_rate("", "") == 0
    assert character_error_rate("", "Foo") == 3 / 3

    assert character_error_rate("Foo", "Food") == 1 / 4
    assert character_error_rate("Fnord", "Food") == 2 / 5
    assert character_error_rate("Müll", "Mull") == 1 / 4
    assert character_error_rate("Abstand", "Sand") == 4 / 7


def test_character_error_rate_hard():
    s1 = unicodedata.normalize("NFC", "Schlyñ lorem ipsum.")
    s2 = unicodedata.normalize("NFD", "Schlyñ lorem ipsum!")  # Different, decomposed!
    assert character_error_rate(s1, s2) == 1 / 19

    s1 = "Schlyñ"
    assert (
        len(s1) == 6
    )  # This ends with LATIN SMALL LETTER N WITH TILDE, so 6 code points
    s2 = "Schlym̃"
    assert (
        len(s2) == 7
    )  # This, OTOH, ends with LATIN SMALL LETTER M + COMBINING TILDE, 7 code points

    # Both strings have the same length in terms of grapheme clusters. So the CER should
    # be symmetrical.
    assert character_error_rate(s2, s1) == 1 / 6
    assert character_error_rate(s1, s2) == 1 / 6
