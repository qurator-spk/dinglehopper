from .utils import MetricResult, Weights
from ..edit_distance import distance
from ..normalize import chars_normalized


def character_accuracy(
    reference: str, compared: str, weights: Weights = Weights(1, 1, 1)
) -> MetricResult:
    """Compute character accuracy and error rate.

    :return: NamedTuple representing the results of this metric.
    """

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
