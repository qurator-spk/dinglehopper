import math

from ...metrics import word_accuracy
from ...normalize import words


def test_words():
    result = list(
        words("Der schnelle [„braune“] Fuchs kann keine 3,14 Meter springen, oder?")
    )
    expected = [
        "Der",
        "schnelle",
        "braune",
        "Fuchs",
        "kann",
        "keine",
        "3,14",
        "Meter",
        "springen",
        "oder",
    ]
    assert result == expected


def test_words_private_use_area():
    result = list(
        words(
            "ber die vielen Sorgen wegen deelben vergaß Hartkopf, der Frau Amtmnnin das ver⸗\n"
            "ſproene zu berliefern."
        )
    )
    expected = [
        "ber",
        "die",
        "vielen",
        "Sorgen",
        "wegen",
        "deelben",
        "vergaß",
        "Hartkopf",
        "der",
        "Frau",
        "Amtmnnin",
        "das",
        "ver",
        "ſproene",
        "zu",
        "berliefern",
    ]
    assert result == expected


def test_word_error_rate():
    assert (
        word_accuracy(
            "Dies ist ein Beispielsatz!", "Dies ist ein Beispielsatz!"
        ).error_rate
        == 0
    )
    assert (
        word_accuracy(
            "Dies. ist ein Beispielsatz!", "Dies ist ein Beispielsatz!"
        ).error_rate
        == 0
    )
    assert (
        word_accuracy(
            "Dies. ist ein Beispielsatz!", "Dies ist ein Beispielsatz."
        ).error_rate
        == 0
    )

    assert (
        word_accuracy(
            "Dies ist ein Beispielsatz!", "Dies ist ein Beispielsarz:"
        ).error_rate
        == 1 / 4
    )
    assert (
        word_accuracy(
            "Dies ist ein Beispielsatz!", "Dies ein ist Beispielsatz!"
        ).error_rate
        == 2 / 4
    )

    assert word_accuracy("Dies ist ein Beispielsatz!", "").error_rate == 4 / 4
    assert math.isinf(word_accuracy("", "Dies ist ein Beispielsatz!").error_rate)
    assert word_accuracy("", "").error_rate == 0

    assert (
        word_accuracy(
            "Schlyñ lorem ipsum dolor sit amet,", "Schlym̃ lorem ipsum dolor sit amet."
        ).error_rate
        == 1 / 6
    )
