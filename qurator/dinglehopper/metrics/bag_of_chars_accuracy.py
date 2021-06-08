from collections import Counter
from typing import Tuple, Union
from unicodedata import normalize

from multimethod import multimethod
from uniseg.graphemecluster import grapheme_clusters

from .utils import bag_accuracy, Weights
from .. import ExtractedText


def bag_of_chars_accuracy(
    reference: Union[str, ExtractedText],
    compared: Union[str, ExtractedText],
    weights: Weights,
) -> float:
    acc, _ = bag_of_chars_accuracy_n(reference, compared, weights)
    return acc


@multimethod
def bag_of_chars_accuracy_n(
    reference: str, compared: str, weights: Weights
) -> Tuple[float, int]:
    reference_chars = Counter(grapheme_clusters(normalize("NFC", reference)))
    compared_chars = Counter(grapheme_clusters(normalize("NFC", compared)))
    e, n = bag_accuracy(reference_chars, compared_chars, weights)
    return (float("inf") if n == 0 else 1 - e / n), n


@multimethod
def bag_of_chars_accuracy_n(
    reference: ExtractedText, compared: ExtractedText, weights: Weights
) -> Tuple[float, int]:
    return bag_of_chars_accuracy_n(reference.text, compared.text, weights)
