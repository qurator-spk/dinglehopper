from __future__ import division

from typing import Tuple

from multimethod import multimethod

from .. import distance
from ..extracted_text import ExtractedText
from ..normalize import chars_normalized


@multimethod
def character_error_rate_n(reference: str, compared: str) -> Tuple[float, int]:
    """
    Compute character error rate.

    :return: character error rate and length of the reference
    """

    d = distance(reference, compared)
    n = len(chars_normalized(reference))

    if d == 0:
        return 0, n
    if n == 0:
        return float("inf"), n
    return d / n, n

    # XXX Should we really count newlines here?


@multimethod
def character_error_rate_n(
    reference: ExtractedText, compared: ExtractedText
) -> Tuple[float, int]:
    return character_error_rate_n(reference.text, compared.text)


def character_error_rate(reference, compared) -> float:
    """
    Compute character error rate.

    :return: character error rate
    """
    cer, _ = character_error_rate_n(reference, compared)
    return cer
