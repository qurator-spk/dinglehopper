from __future__ import division, print_function

import math

from .. import word_error_rate, words


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
            "ber die vielen Sorgen wegen deelben vergaß Hartkopf, "
            "der Frau Amtmnnin das ver⸗\n"
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
        word_error_rate("Dies ist ein Beispielsatz!", "Dies ist ein Beispielsatz!") == 0
    )
    assert (
        word_error_rate("Dies. ist ein Beispielsatz!", "Dies ist ein Beispielsatz!")
        == 0
    )
    assert (
        word_error_rate("Dies. ist ein Beispielsatz!", "Dies ist ein Beispielsatz.")
        == 0
    )

    assert (
        word_error_rate("Dies ist ein Beispielsatz!", "Dies ist ein Beispielsarz:")
        == 1 / 4
    )
    assert (
        word_error_rate("Dies ist ein Beispielsatz!", "Dies ein ist Beispielsatz!")
        == 2 / 4
    )

    assert word_error_rate("Dies ist ein Beispielsatz!", "") == 4 / 4
    assert word_error_rate("", "Dies ist ein Beispielsatz!") == 4 / 4
    assert word_error_rate("", "") == 0

    assert (
        word_error_rate(
            "Schlyñ lorem ipsum dolor sit amet,", "Schlym̃ lorem ipsum dolor sit amet."
        )
        == 1 / 6
    )
