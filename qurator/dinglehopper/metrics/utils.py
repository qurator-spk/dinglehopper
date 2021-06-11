from collections import Counter
from typing import Dict, NamedTuple


class Weights(NamedTuple):
    """Represent weights/costs for editing operations."""

    deletes: int = 1
    inserts: int = 1
    replacements: int = 1


class MetricResult(NamedTuple):
    """Represent a result from a metric calculation."""

    metric: str
    weights: Weights
    weighted_errors: int
    reference_elements: int
    compared_elements: int

    @property
    def accuracy(self) -> float:
        return 1 - self.error_rate

    @property
    def error_rate(self) -> float:
        if self.reference_elements <= 0 and self.compared_elements <= 0:
            return 0
        elif self.reference_elements <= 0:
            return float("inf")
        return self.weighted_errors / self.reference_elements

    def get_dict(self) -> Dict:
        """Combines the properties to a dictionary.

        We deviate from the builtin _asdict() function by including our properties.
        """
        return {
            **{
                key: value
                for key, value in self._asdict().items()
            },
            "accuracy": self.accuracy,
            "error_rate": self.error_rate,
            "weights": self.weights._asdict(),
        }


def bag_accuracy(
    reference: Counter, compared: Counter, weights: Weights
) -> MetricResult:
    """Calculates the the weighted errors for two bags (Counter).

    Basic algorithm idea:
     - All elements in reference not occurring in compared are considered deletes.
     - All elements in compared not occurring in reference are considered inserts.
     - When the cost for one replacement is lower than that of one insert and one delete
       we can substitute pairs of deletes and inserts with one replacement.

    :param reference: Bag used as reference (ground truth).
    :param compared: Bag used to compare (ocr).
    :param weights: Weights/costs for editing operations.
    :return: NamedTuple representing the results of this metric.
    """
    n_ref = sum(reference.values())
    n_cmp = sum(compared.values())
    deletes = sum((reference - compared).values())
    inserts = sum((compared - reference).values())
    replacements = 0
    if weights.replacements < (weights.deletes + weights.inserts):
        replacements = min(deletes, inserts)
        deletes, inserts = max(deletes - inserts, 0), max(inserts - deletes, 0)
    weighted_errors = (
        weights.deletes * deletes
        + weights.inserts * inserts
        + weights.replacements * replacements
    )
    return MetricResult(
        metric=bag_accuracy.__name__,
        weights=weights,
        weighted_errors=weighted_errors,
        reference_elements=n_ref,
        compared_elements=n_cmp,
    )
