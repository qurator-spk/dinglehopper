from __future__ import division, print_function

import unicodedata
from itertools import chain
from typing import List, Union, Tuple

from Levenshtein import editops as c_editops, distance as c_distance
from multimethod import multimethod
from uniseg.graphemecluster import grapheme_clusters

from .extracted_text import ExtractedText


@multimethod
def distance_unicode(s1: str, s2: str):
    """Compute the Levenshtein edit distance between two Unicode strings

    Note that this is different from distance() as this function knows about Unicode
    normalization and grapheme clusters.

    This should be the correct way to compare two Unicode strings.
    """
    s1, s2 = transform_unicode(s1, s2)
    return distance(s1, s2)


@multimethod
def distance_unicode(s1: ExtractedText, s2: ExtractedText):
    """Compute the Levenshtein edit distance between two Unicode strings

    Note that this is different from distance() as this function knows about Unicode
    normalization and grapheme clusters.

    This should be the correct way to compare two Unicode strings.
    """
    return distance_unicode(s1.text, s2.text)


@multimethod
def distance(l1: List, l2: List):
    """Compute the Levenshtein edit distance between two lists.

    Also see `distance_unicode()`.

    The difference is that this implementation does not care about grapheme clusters or
    unicode normalization, assuming that this already has been done in preprocessing.
    """
    s1, s2 = transform_lists(l1, l2)
    return c_distance(s1, s2)


@multimethod
def distance(s1: str, s2: str):
    """Compute the Levenshtein edit distance between two strings.

    Also see `distance_unicode()`.

    The difference is that this implementation does not care about grapheme clusters or
    unicode normalization, assuming that this already has been done in preprocessing.
    """
    return c_distance(s1, s2)


@multimethod
def distance(s1: ExtractedText, s2: ExtractedText):
    """Compute the Levenshtein edit distance between two strings.

    Also see `distance_unicode()`.

    The difference is that this implementation does not care about grapheme clusters or
    unicode normalization, assuming that this already has been done in preprocessing.
    """
    return distance(s1.text, s2.text)


@multimethod
def editops_unicode(s1: str, s2: str):
    """Return sequence of edit operations transforming one string to another.

    Note that this returns indices to the _grapheme clusters_, not characters!
    """
    s1, s2 = transform_unicode(s1, s2)
    return editops(s1, s2)


@multimethod
def editops(l1: List, l2: List):
    """Return sequence of edit operations transforming one list to another.

    Also see `editops_unicode()`.

    The difference is that this implementation does not care about grapheme clusters or
    unicode normalization, assuming that this already has been done in preprocessing.
    """
    s1, s2 = transform_lists(l1, l2)
    return c_editops(s1, s2)


@multimethod
def editops(s1: str, s2: str):
    """Return sequence of edit operations transforming one string to another.

    Also see `editops_unicode()`.

    The difference is that this implementation does not care about grapheme clusters or
    unicode normalization, assuming that this already has been done in preprocessing.
    """
    return c_editops(s1, s2)


def transform_lists(l1: List, l2: List) -> Tuple[str, str]:
    """Transform two lists into string representation.

    We need this transformation to be able to calculate a Levenshtein distance
    between two sequences.

    Note that we can only process 1,114,111 unique elements with this implementation.
    See https://docs.python.org/3/library/functions.html#chr
    """
    mapping = {el: chr(i) for i, el in enumerate(frozenset(chain(l1, l2)))}
    s1 = "".join([mapping[el] for el in l1])
    s2 = "".join([mapping[el] for el in l2])
    return s1, s2


def transform_unicode(s1: str, s2: str) -> Union[Tuple[str, str], Tuple[List[str]]]:
    """Transform two text sequences to unicode representation.

    Normalize to unicode and decides whether we have wide chars
    that needs to be represented by lists.
    """
    s1 = list(grapheme_clusters(unicodedata.normalize("NFC", s1)))
    s2 = list(grapheme_clusters(unicodedata.normalize("NFC", s2)))
    if all(len(s) < 2 for s in chain(s1, s2)):
        s1, s2 = "".join(s1), "".join(s2)
    return s1, s2
