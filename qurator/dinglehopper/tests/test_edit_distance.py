import unicodedata

from ..edit_distance import levenshtein, distance


def test_levenshtein():
    assert levenshtein("a", "a") == 0
    assert levenshtein("a", "b") == 1
    assert levenshtein("Foo", "Bar") == 3

    assert levenshtein("", "") == 0
    assert levenshtein("Foo", "") == 3
    assert levenshtein("", "Foo") == 3

    assert levenshtein("Foo", "Food") == 1
    assert levenshtein("Fnord", "Food") == 2
    assert levenshtein("Müll", "Mull") == 1
    assert levenshtein("Abstand", "Sand") == 4


def test_levenshtein_other_sequences():
    assert levenshtein(["a", "ab"], ["a", "ab", "c"]) == 1
    assert levenshtein(["a", "ab"], ["a", "c"]) == 1


def test_distance():
    assert distance("Fnord", "Food") == 2
    assert distance("Müll", "Mull") == 1

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
