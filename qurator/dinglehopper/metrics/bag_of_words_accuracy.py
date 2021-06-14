from collections import Counter

from .utils import bag_accuracy, MetricResult, Weights
from ..normalize import words_normalized


def bag_of_words_accuracy(
    reference: str, compared: str, weights: Weights = Weights(1, 0, 1)
) -> MetricResult:
    """Compute Bag of Words accuracy and error rate.

    We are using sets to calculate the errors.
    See :func:`bag_accuracy` for details.

    :param reference: String used as reference (e.g. ground truth).
    :param compared: String that gets evaluated (e.g. ocr result).
    :param weights: Weights/costs for editing operations.
    :return: Class representing the results of this metric.
    """
    reference_words: Counter = Counter(words_normalized(reference))
    compared_words: Counter = Counter(words_normalized(compared))
    return bag_accuracy(
        reference_words, compared_words, weights, bag_of_words_accuracy.__name__
    )
