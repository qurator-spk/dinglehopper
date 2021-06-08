from collections import Counter
from typing import Tuple, Union

from .utils import bag_accuracy, Weights
from .. import ExtractedText
from ..normalize import words_normalized


def bag_of_words_accuracy(
    reference: Union[str, ExtractedText],
    compared: Union[str, ExtractedText],
    weights: Weights,
) -> float:
    acc, _ = bag_of_words_accuracy_n(reference, compared, weights)
    return acc


def bag_of_words_accuracy_n(
    reference: Union[str, ExtractedText],
    compared: Union[str, ExtractedText],
    weights: Weights,
) -> Tuple[float, int]:
    if isinstance(reference, ExtractedText):
        reference = reference.text
    if isinstance(compared, ExtractedText):
        compared = compared.text
    reference_words = Counter(words_normalized(reference))
    compared_words = Counter(words_normalized(compared))
    e, n = bag_accuracy(reference_words, compared_words, weights)
    return (float("inf") if n == 0 else 1 - e / n), n
