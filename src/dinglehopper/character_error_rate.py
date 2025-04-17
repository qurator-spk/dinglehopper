import unicodedata
from typing import List, Tuple, TypeVar

from multimethod import multimethod
from uniseg.graphemecluster import grapheme_clusters

from .edit_distance import distance
from .extracted_text import ExtractedText

T = TypeVar("T")


@multimethod
def character_error_rate_n(
    reference: List[str], compared: List[str]
) -> Tuple[float, int]:
    """
    Compute character error rate.

    :return: character error rate and length of the reference
    """

    return distance(reference, compared), len(reference)

    # XXX Should we really count newlines here?


@character_error_rate_n.register
def _(reference: str, compared: str) -> Tuple[float, int]:
    seq1 = list(grapheme_clusters(unicodedata.normalize("NFC", reference)))
    seq2 = list(grapheme_clusters(unicodedata.normalize("NFC", compared)))
    cer, n = character_error_rate_n(seq1, seq2)
    return cer, n


@character_error_rate_n.register
def _(reference: ExtractedText, compared: ExtractedText) -> Tuple[float, int]:
    cer, n = character_error_rate_n(
        reference.grapheme_clusters, compared.grapheme_clusters
    )
    return cer, n


def character_error_rate(reference: T, compared: T) -> float:
    """
    Compute character error rate.

    :return: character error rate
    """
    cer: float
    cer, _ = character_error_rate_n(reference, compared)
    return cer
