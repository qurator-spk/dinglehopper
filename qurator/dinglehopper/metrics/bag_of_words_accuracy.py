from collections import Counter
from typing import Union

from .utils import bag_accuracy, MetricResult, Weights
from .. import ExtractedText
from ..normalize import words_normalized


def bag_of_words_accuracy(
    reference: Union[str, ExtractedText],
    compared: Union[str, ExtractedText],
    weights: Weights,
) -> MetricResult:
    if isinstance(reference, ExtractedText):
        reference = reference.text
    if isinstance(compared, ExtractedText):
        compared = compared.text
    reference_words = Counter(words_normalized(reference))
    compared_words = Counter(words_normalized(compared))
    result = bag_accuracy(reference_words, compared_words, weights)
    return MetricResult(
        **{**result._asdict(), "metric": bag_of_words_accuracy.__name__}
    )
