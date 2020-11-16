from __future__ import division, print_function

import unicodedata
from functools import partial, lru_cache
from itertools import chain
from typing import Sequence, Tuple, List

import numpy as np
from Levenshtein import editops as c_editops, distance as c_distance
from multimethod import multimethod
from uniseg.graphemecluster import grapheme_clusters
from tqdm import tqdm

from .extracted_text import ExtractedText
from .config import Config


def levenshtein_matrix(seq1: Sequence, seq2: Sequence):
    """Compute the matrix commonly computed to produce the Levenshtein distance.
    This is also known as the Wagner-Fischer algorithm. The matrix element at the bottom right contains the desired
    edit distance.

    This algorithm is implemented here because we need an implementation that can work with sequences other than
    strings, e.g. lists of grapheme clusters or lists of word strings.
    """

    # Internally, we use a cached version. As the cache only works on hashable parameters, we convert the input
    # sequences to tuples to make them hashable.
    return _levenshtein_matrix(tuple(seq1), tuple(seq2))


@lru_cache(maxsize=10)
def _levenshtein_matrix(seq1: Tuple, seq2: Tuple):
    """Compute the matrix commonly computed to produce the Levenshtein distance.

    This is a LRU cached function not meant to be used directly. Use levenshtein_matrix() instead.
    """
    m = len(seq1)
    n = len(seq2)

    def from_to(start, stop):
        return range(start, stop + 1, 1)

    D = np.zeros((m + 1, n + 1), np.int)
    D[0, 0] = 0
    for i in from_to(1, m):
        D[i, 0] = i
    for j in from_to(1, n):
        D[0, j] = j
    for i in tqdm(from_to(1, m), disable=not Config.progress):
        for j in from_to(1, n):
            D[i, j] = min(
                D[i - 1, j - 1]
                + 1 * (seq1[i - 1] != seq2[j - 1]),  # Same or Substitution
                D[i, j - 1] + 1,  # Insertion
                D[i - 1, j] + 1,  # Deletion
            )

    return D


def levenshtein(seq1, seq2):
    """Compute the Levenshtein edit distance between two sequences"""
    m = len(seq1)
    n = len(seq2)

    D = levenshtein_matrix(seq1, seq2)
    return D[m, n]


def levenshtein_matrix_cache_clear():
    """Clear internal Levenshtein matrix cache.

    You want to do this between different input file pairs to decrease memory
    usage by not caching results from prior input files.
    """
    _levenshtein_matrix.cache_clear()


@multimethod
def distance(s1: str, s2: str):
    """Compute the Levenshtein edit distance between two Unicode strings

    Note that this is different from levenshtein() as this function knows about Unicode
    normalization and grapheme clusters.

    This should be the correct way to compare two Unicode strings.
    """
    seq1 = list(grapheme_clusters(unicodedata.normalize("NFC", s1)))
    seq2 = list(grapheme_clusters(unicodedata.normalize("NFC", s2)))
    if any(len(s) > 1 for s in chain(seq1, seq2)):
        return distance(seq1, seq2)
    else:
        return distance_fast("".join(seq1), "".join(seq2))


@multimethod
def distance(s1: ExtractedText, s2: ExtractedText):
    return distance(s1.text, s2.text)


@multimethod
def distance(s1: List, s2: List):
    return levenshtein(s1, s2)


def distance_fast(s1: str, s2: str):
    """Compute the Levenshtein edit distance between two Unicode strings

    Also see `distance()`.

    The difference is that this implementation does not care about grapheme clusters or
    unicode normalization, assuming that this already has been done in preprocessing.
    """
    return c_distance(s1, s2)


@multimethod
def editops(seq1: List, seq2: List):
    """
    Return sequence of edit operations transforming one sequence to another.

    This aims to return the same/similar results as python-Levenshtein's editops(),
    just generalized to arbitrary sequences.
    """
    seq1 = list(seq1)
    seq2 = list(seq2)
    m = len(seq1)
    n = len(seq2)
    D = levenshtein_matrix(seq1, seq2)

    def _tail_backtrace(i, j, accumulator):
        if i > 0 and D[i - 1, j] + 1 == D[i, j]:
            return partial(
                _tail_backtrace, i - 1, j, [("delete", i - 1, j)] + accumulator
            )
        if j > 0 and D[i, j - 1] + 1 == D[i, j]:
            return partial(
                _tail_backtrace, i, j - 1, [("insert", i, j - 1)] + accumulator
            )
        if i > 0 and j > 0 and D[i - 1, j - 1] + 1 == D[i, j]:
            return partial(
                _tail_backtrace, i - 1, j - 1, [("replace", i - 1, j - 1)] + accumulator
            )
        if i > 0 and j > 0 and D[i - 1, j - 1] == D[i, j]:
            return partial(_tail_backtrace, i - 1, j - 1, accumulator)  # NOP
        return accumulator

    def backtrace(i, j):
        result = partial(_tail_backtrace, i, j, [])
        while isinstance(result, partial):
            result = result()

        return result

    b = backtrace(m, n)
    return b


@multimethod
def editops(s1: str, s2: str):
    """
    Return sequence of edit operations transforming one string to another.

    Note that this returns indices to the _grapheme clusters_, not characters!
    """
    s1 = list(grapheme_clusters(unicodedata.normalize("NFC", s1)))
    s2 = list(grapheme_clusters(unicodedata.normalize("NFC", s2)))
    if any(len(s) > 1 for s in chain(s1, s2)):
        return editops(s1, s2)
    else:
        return editops_fast("".join(s1), "".join(s2))


def editops_fast(s1: str, s2: str):
    """Return sequence of edit operations transforming one string to another.

    Also see `editops()`.

    The difference is that this implementation does not care about grapheme clusters or
    unicode normalization, assuming that this already has been done in preprocessing.
    """
    return c_editops(s1, s2)
