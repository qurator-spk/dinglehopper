"""
Datastructures to be used with the Flexible Character Accuracy Algorithm

Separated because of version compatibility issues with Python 3.5.
"""

from typing import List, NamedTuple


class PartVersionSpecific(NamedTuple):
    """Represent a line or part of a line.

    This data object is maintained to be able to reproduce the original text.
    """

    text: str = ""
    line: int = 0
    start: int = 0


class Distance(NamedTuple):
    """Represent distance between two sequences."""

    match: int = 0
    replace: int = 0
    delete: int = 0
    insert: int = 0


class Match(NamedTuple):
    """Represent a calculated match between ground truth and the ocr result."""

    gt: "Part"
    ocr: "Part"
    dist: "Distance"
    ops: List


class Coefficients(NamedTuple):
    """Coefficients to calculate penalty for substrings.

    See Section 3 in doi:10.1016/j.patrec.2020.02.003
    """

    edit_dist: int = 25
    length_diff: int = 20
    offset: int = 1
    length: int = 4
