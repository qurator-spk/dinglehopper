from collections import Counter
from typing import NamedTuple, Tuple


class Weights(NamedTuple):
    """Represent weights/costs for editing operations."""

    deletes: int = 1
    inserts: int = 1
    replacements: int = 1


def bag_accuracy(
    reference: Counter, compared: Counter, weights: Weights
) -> Tuple[int, int]:
    """Calculates the the weighted errors for two bags (Counter).

    Basic algorithm idea:
     - All elements in reference not occurring in compared are considered deletes.
     - All elements in compared not occurring in reference are considered inserts.
     - When the cost for one replacement is lower than that of one insert and one delete
       we can substitute pairs of deletes and inserts with one replacement.

    :param reference: Bag used as reference (ground truth).
    :param compared: Bag used to compare (ocr).
    :param weights: Weights/costs for editing operations.
    :return: weighted errors and number of elements in reference.
    """
    n = sum(reference.values())
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
    return weighted_errors, n
