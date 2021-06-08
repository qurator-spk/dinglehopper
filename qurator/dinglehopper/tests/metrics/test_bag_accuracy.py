import math
import unicodedata
from collections import Counter

import pytest

from ...metrics import bag_of_chars_accuracy_n, bag_of_words_accuracy_n, Weights
from ...metrics.utils import bag_accuracy


@pytest.fixture
def ex_weights():
    return (
        Weights(deletes=0, inserts=0, replacements=0),
        Weights(deletes=1, inserts=1, replacements=1),
        Weights(deletes=1, inserts=0, replacements=1),
        Weights(deletes=1, inserts=1, replacements=2),
    )


SIMPLE_CASES = (
    ("", "", 0, (0, 0, 0)),
    ("abc", "", 3, (3, 3, 3)),
    ("", "abc", 0, (3, 0, 3)),
    ("abc", "abc", 3, (0, 0, 0)),
    ("abc", "ab", 3, (1, 1, 1)),
    ("abc", "abcd", 3, (1, 0, 1)),
    ("abc", "abd", 3, (1, 1, 2)),
)


@pytest.mark.parametrize(
    "s1,s2, ex_n, ex_err",
    [
        *SIMPLE_CASES,
        (("a", "b", "c", "d", "e"), ("a", "b", "c", "d", ("e", "´")), 5, (1, 1, 2)),
        (range(5), range(6), 5, (1, 0, 1)),
    ],
)
def test_bag_accuracy_algorithm(s1, s2, ex_n, ex_err, ex_weights):
    """Test the main algorithm for calculating the bag accuracy."""
    for weights, expected_errors in zip(ex_weights, (0, *ex_err)):
        e, n = bag_accuracy(Counter(s1), Counter(s2), weights=weights)
        assert n == ex_n, f"{n} == {ex_n} for {weights}"
        assert e == expected_errors, f"{e} == {expected_errors} for {weights}"


@pytest.mark.parametrize(
    "s1,s2, ex_n, ex_err",
    [
        *SIMPLE_CASES,
        ("Schlyñ", "Schlym̃", 6, (1, 1, 2)),
        (
            unicodedata.normalize("NFC", "Schlyñ lorem ipsum."),
            unicodedata.normalize("NFD", "Schlyñ lorem ipsum!"),
            19,
            (1, 1, 2),
        ),
    ],
)
def test_bag_of_chars_accuracy_n(s1, s2, ex_n, ex_err, ex_weights):
    """Test the special behaviour of the char differentiation.

    As the algorithm and the char normalization is implemented elsewhere
    we are currently only testing that the corresponding algorithms are called.
    """
    for weights, expected_errors in zip(ex_weights, (0, *ex_err)):
        acc, n = bag_of_chars_accuracy_n(s1, s2, weights)
        assert n == ex_n, f"{n} == {ex_n} for {weights}"
        if ex_n == 0:
            assert math.isinf(acc)
        else:
            assert acc == pytest.approx(1 - expected_errors / ex_n), f"w: {weights}"


@pytest.mark.parametrize(
    "s1,s2, ex_n, ex_err",
    [
        *SIMPLE_CASES,
        ("Schlyñ", "Schlym̃", 6, (1, 1, 2)),
        (
            unicodedata.normalize("NFC", "Schlyñ lorem ipsum."),
            unicodedata.normalize("NFD", "Schlyñ lorem ipsum!"),
            3,
            (0, 0, 0),
        ),
    ],
)
def test_bag_of_words_accuracy_n(s1, s2, ex_n, ex_err, ex_weights):
    """Test the special behaviour of the word differentiation.

    As the algorithm and the word splitting is implemented elsewhere
    we are currently only testing that the corresponding algorithms are called.
    """
    if " " not in s1 and " " not in s2:
        s1 = " ".join(s1)
        s2 = " ".join(s2)
    for weights, expected_errors in zip(ex_weights, (0, *ex_err)):
        acc, n = bag_of_words_accuracy_n(s1, s2, weights)
        assert n == ex_n, f"{n} == {ex_n} for {weights}"
        if ex_n == 0:
            assert math.isinf(acc)
        else:
            assert acc == pytest.approx(1 - expected_errors / ex_n), f"w: {weights}"
