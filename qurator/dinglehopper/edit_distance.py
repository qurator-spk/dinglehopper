import unicodedata

from multimethod import multimethod
from uniseg2.graphemecluster import grapheme_clusters
from rapidfuzz.distance import Levenshtein

from .extracted_text import ExtractedText


@multimethod
def distance(seq1: list[str], seq2: list[str]):
    """Compute the Levenshtein edit distance between two Unicode strings

    Note that this is different from levenshtein() as this function knows about Unicode
    normalization and grapheme clusters. This should be the correct way to compare two
    Unicode strings.
    """
    return Levenshtein.distance(seq1, seq2)


@multimethod
def distance(s1: str, s2: str):
    """Compute the Levenshtein edit distance between two Unicode strings

    Note that this is different from levenshtein() as this function knows about Unicode
    normalization and grapheme clusters. This should be the correct way to compare two
    Unicode strings.
    """
    seq1 = list(grapheme_clusters(unicodedata.normalize("NFC", s1)))
    seq2 = list(grapheme_clusters(unicodedata.normalize("NFC", s2)))
    return Levenshtein.distance(seq1, seq2)


@multimethod
def distance(s1: ExtractedText, s2: ExtractedText):
    return Levenshtein.distance(s1.grapheme_clusters, s2.grapheme_clusters)


def editops(word1, word2):
    """
    Return sequence of edit operations transforming one string to another.

    Note that this returns indices to the _grapheme clusters_, not characters!
    """
    word1 = list(grapheme_clusters(unicodedata.normalize("NFC", word1)))
    word2 = list(grapheme_clusters(unicodedata.normalize("NFC", word2)))
    return Levenshtein.editops(word1, word2).as_list()
