from __future__ import division

from typing import Iterable, Tuple

from multimethod import multimethod

from ..edit_distance import levenshtein
from ..extracted_text import ExtractedText
from ..normalize import words_normalized


@multimethod
def word_error_rate_n(reference: str, compared: str) -> Tuple[float, int]:
    reference_seq = list(words_normalized(reference))
    compared_seq = list(words_normalized(compared))
    return word_error_rate_n(reference_seq, compared_seq)


@multimethod
def word_error_rate_n(
    reference: ExtractedText, compared: ExtractedText
) -> Tuple[float, int]:
    return word_error_rate_n(reference.text, compared.text)


@multimethod
def word_error_rate_n(reference: Iterable, compared: Iterable) -> Tuple[float, int]:
    reference_seq = list(reference)
    compared_seq = list(compared)

    d = levenshtein(reference_seq, compared_seq)
    n = len(reference_seq)

    if d == 0:
        return 0, n
    if n == 0:
        return float("inf"), n
    return d / n, n


def word_error_rate(reference, compared) -> float:
    wer, _ = word_error_rate_n(reference, compared)
    return wer
