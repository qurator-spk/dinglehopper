from collections import Counter

from .utils import bag_accuracy, MetricResult, Weights
from ..normalize import words_normalized


def bag_of_words_accuracy(
    reference: str, compared: str, weights: Weights
) -> MetricResult:
    reference_words = Counter(words_normalized(reference))
    compared_words = Counter(words_normalized(compared))
    result = bag_accuracy(reference_words, compared_words, weights)
    return MetricResult(
        **{**result._asdict(), "metric": bag_of_words_accuracy.__name__}
    )
