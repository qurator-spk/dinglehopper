from collections import Counter
from unicodedata import normalize

from uniseg.graphemecluster import grapheme_clusters

from .utils import bag_accuracy, MetricResult, Weights


def bag_of_chars_accuracy(
    reference: str, compared: str, weights: Weights = Weights(1, 0, 1)
) -> MetricResult:
    """Compute Bag of Chars accuracy and error rate.

    We are using sets to calculate the errors.
    See :func:`bag_accuracy` for details.

    :param reference: String used as reference (e.g. ground truth).
    :param compared: String that gets evaluated (e.g. ocr result).
    :param weights: Weights/costs for editing operations.
    :return: Class representing the results of this metric.
    """
    reference_chars: Counter = Counter(grapheme_clusters(normalize("NFC", reference)))
    compared_chars: Counter = Counter(grapheme_clusters(normalize("NFC", compared)))
    return bag_accuracy(
        reference_chars, compared_chars, weights, bag_of_chars_accuracy.__name__
    )
