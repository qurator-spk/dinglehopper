from __future__ import division, print_function

import unicodedata

from .. import distance


def test_distance():
    assert distance("Fnord", "Food") == 2 / 5
    assert distance("Müll", "Mull") == 1 / 4

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
    assert distance(word1, word2) == 1 / 6
