from .utils import MetricResult, Weights
from ..edit_distance import levenshtein
from ..normalize import words_normalized


def word_accuracy(
    reference: str, compared: str, weights: Weights = Weights(1, 1, 1)
) -> MetricResult:
    """Compute word accuracy and error rate.

    We are using the Levenshtein distance between reference.

    :param reference: String used as reference (e.g. ground truth).
    :param compared: String that gets evaluated (e.g. ocr result).
    :param weights: Weights/costs for editing operations (not supported yet).
    :return: Class representing the results of this metric.
    """
    if weights != Weights(1, 1, 1):
        raise NotImplementedError("Setting weights is not supported yet.")

    reference_seq = list(words_normalized(reference))
    compared_seq = list(words_normalized(compared))

    weighted_errors = levenshtein(reference_seq, compared_seq)
    n_ref = len(reference_seq)
    n_cmp = len(compared_seq)

    return MetricResult(
        metric=word_accuracy.__name__,
        weights=weights,
        weighted_errors=int(weighted_errors),
        reference_elements=n_ref,
        compared_elements=n_cmp,
    )
