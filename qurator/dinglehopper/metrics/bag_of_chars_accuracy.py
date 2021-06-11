from collections import Counter
from unicodedata import normalize

from uniseg.graphemecluster import grapheme_clusters

from .utils import bag_accuracy, MetricResult, Weights


def bag_of_chars_accuracy(
    reference: str, compared: str, weights: Weights = Weights(1, 0, 1)
) -> MetricResult:
    reference_chars: Counter = Counter(grapheme_clusters(normalize("NFC", reference)))
    compared_chars: Counter = Counter(grapheme_clusters(normalize("NFC", compared)))
    return bag_accuracy(
        reference_chars, compared_chars, weights, bag_of_chars_accuracy.__name__
    )
