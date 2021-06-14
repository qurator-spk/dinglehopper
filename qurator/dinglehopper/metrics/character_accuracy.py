from .utils import MetricResult, Weights
from ..edit_distance import distance
from ..normalize import chars_normalized


def character_accuracy(
    reference: str, compared: str, weights: Weights = Weights(1, 1, 1)
) -> MetricResult:
    """Compute character accuracy and error rate.

    We are using the Levenshtein distance between reference and compared.

    :param reference: String used as reference (e.g. ground truth).
    :param compared: String that gets evaluated (e.g. ocr result).
    :param weights: Weights/costs for editing operations (not supported yet).
    :return: Class representing the results of this metric.
    """
    if weights != Weights(1, 1, 1):
        raise NotImplementedError("Setting weights is not supported yet.")
    weighted_errors = distance(reference, compared)
    n_ref = len(chars_normalized(reference))
    n_cmp = len(chars_normalized(compared))

    return MetricResult(
        metric=character_accuracy.__name__,
        weights=weights,
        weighted_errors=int(weighted_errors),
        reference_elements=n_ref,
        compared_elements=n_cmp,
    )

    # XXX Should we really count newlines here?
