import unicodedata
from typing import Tuple

from multimethod import multimethod
from uniseg2.graphemecluster import grapheme_clusters

from .edit_distance import distance
from .extracted_text import ExtractedText


@multimethod
def character_error_rate_n(
    reference: list[str], compared: list[str]
) -> Tuple[float, int]:
    """
    Compute character error rate.

    :return: character error rate and length of the reference
    """

    d = distance(reference, compared)
    n = len(reference)

    if d == 0:
        return 0, n
    if n == 0:
        return float("inf"), n
    return d / n, n

    # XXX Should we really count newlines here?


@multimethod
def character_error_rate_n(reference: str, compared: str) -> Tuple[float, int]:
    seq1 = list(grapheme_clusters(unicodedata.normalize("NFC", reference)))
    seq2 = list(grapheme_clusters(unicodedata.normalize("NFC", compared)))
    return character_error_rate_n(seq1, seq2)


@multimethod
def character_error_rate_n(
    reference: ExtractedText, compared: ExtractedText
) -> Tuple[float, int]:
    return character_error_rate_n(
        reference.grapheme_clusters, compared.grapheme_clusters
    )


def character_error_rate(reference, compared) -> float:
    """
    Compute character error rate.

    :return: character error rate
    """
    cer, _ = character_error_rate_n(reference, compared)
    return cer
