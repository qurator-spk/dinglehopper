import unicodedata
from typing import List

from multimethod import multimethod
from rapidfuzz.distance import Levenshtein
from uniseg.graphemecluster import grapheme_clusters

from .extracted_text import ExtractedText


@multimethod
def distance(seq1: List[str], seq2: List[str]) -> float:
    """Compute the Levenshtein edit distance between two lists of grapheme clusters.

    This assumes that the grapheme clusters are already normalized.

    Use distance(str, str) instead if you need to compare two Unicode strings.
    """
    return Levenshtein.normalized_distance(seq1, seq2)


@distance.register
def _(s1: str, s2: str) -> float:
    """Compute the Levenshtein edit distance between two Unicode strings

    Note that this is different from levenshtein() as this function knows about Unicode
    normalization and grapheme clusters. This should be the correct way to compare two
    Unicode strings.
    """
    seq1 = list(grapheme_clusters(unicodedata.normalize("NFC", s1)))
    seq2 = list(grapheme_clusters(unicodedata.normalize("NFC", s2)))
    return Levenshtein.normalized_distance(seq1, seq2)


@distance.register
def _(s1: ExtractedText, s2: ExtractedText) -> float:
    return Levenshtein.normalized_distance(s1.grapheme_clusters, s2.grapheme_clusters)


def editops(word1, word2):
    """
    Return sequence of edit operations transforming one string to another.

    Note that this returns indices to the _grapheme clusters_, not characters!
    """
    word1 = list(grapheme_clusters(unicodedata.normalize("NFC", word1)))
    word2 = list(grapheme_clusters(unicodedata.normalize("NFC", word2)))
    return Levenshtein.editops(word1, word2).as_list()
