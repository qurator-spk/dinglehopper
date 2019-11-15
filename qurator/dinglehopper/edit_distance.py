from __future__ import division, print_function

import unicodedata
from functools import partial

import numpy as np
import hashlib
import os
import tempfile
from uniseg.graphemecluster import grapheme_clusters


def levenshtein_matrix(seq1, seq2, tempcache=True):
    """Compute the matrix commonly computed to produce the Levenshtein distance.

    The first algorithm is based on the hypothesis that the set of individual graphemes is smaller than
    the length of the grapheme cluster array.

    The second algorithm is also known as the Wagner-Fischer algorithm.
    The matrix element at the bottom right contains the desired edit distance.

    This algorithm is implemented here because we need an implementation that can work with sequences other than
    strings, e.g. lists of grapheme clusters or lists of word strings.
    """
    if tempcache:
        hashseq1 = hashlib.sha1(("؟".join(seq1)).encode("utf-8")).hexdigest()
        hashseq2 = hashlib.sha1(("؟".join(seq2)).encode("utf-8")).hexdigest()
        tempdir = os.path.join(tempfile.gettempdir(), "dinglehopper/")
        if not os.path.exists(tempdir):
            os.makedirs(tempdir)
        tempfilename = os.path.join(tempdir, hashseq1 + "." + hashseq2 + ".npy")
        if os.path.exists(tempfilename):
            return np.load(tempfilename)

    m = len(seq1)
    n = len(seq2)

    D = np.zeros((m + 1, n + 1), np.int)
    D[:, 0] = np.arange(m+1)
    D[0, :] = np.arange(n+1)

    if m > 26 and n > 26:
        # All grapheme which occur in both sets
        interset = set(seq1).intersection(set(seq2))

        # Generate a boolean-mask for each interset grapheme
        masks = {grapheme: [0] * (len(seq2) + 1) for grapheme in interset}

        for idx, grapheme in enumerate(seq2):
            if grapheme in interset:
                masks[grapheme][idx] = -1

        # Calculate the levensthein matrix
        for row, grapheme in enumerate(seq1):
            if grapheme in interset:
                mask = masks[grapheme]
                for col in range(0,n):
                    D[row + 1, col + 1] = 1 + min(D[row, col] + mask[col], # same or subsitution
                                              D[row + 1, col], # insertion
                                              D[row, col + 1]) # deletion
            else:
                for col in range(0,n):
                    D[row+1, col+1] = 1 + min(D[row, col], # substitution
                                         D[row+1, col], # insertion
                                         D[row, col+1]) # deletion
    else:
        for row in range(1, m+1):
            for col in range(1, n+1):
                D[row, col] = min(
                    D[row - 1, col - 1] + 1 * (seq1[row - 1] != seq2[col - 1]),  # Same or Substitution
                    D[row, col - 1] + 1,  # Insertion
                    D[row - 1, col] + 1   # Deletion
                )
    if tempcache:
        np.save(tempfilename,D)
    return D

def levenshtein(seq1, seq2):
    """Compute the Levenshtein edit distance between two sequences"""
    m = len(seq1)
    n = len(seq2)

    D = levenshtein_matrix(seq1, seq2)
    return D[m, n]


def distance(s1, s2):
    """Compute the Levenshtein edit distance between two Unicode strings

    Note that this is different from levenshtein() as this function knows about Unicode normalization and grapheme
    clusters. This should be the correct way to compare two Unicode strings.
    """
    s1 = list(grapheme_clusters(unicodedata.normalize('NFC', s1)))
    s2 = list(grapheme_clusters(unicodedata.normalize('NFC', s2)))
    return levenshtein(s1, s2)


def seq_editops(seq1, seq2):
    seq1 = list(seq1)
    seq2 = list(seq2)
    m = len(seq1)
    n = len(seq2)
    D = levenshtein_matrix(seq1, seq2)

    def _tail_backtrace(i, j, accumulator):
        if i > 0 and D[i - 1, j] + 1 == D[i, j]:
            return partial(_tail_backtrace, i - 1, j, [('delete', i-1, j)] + accumulator)
        if j > 0 and D[i, j - 1] + 1 == D[i, j]:
            return partial(_tail_backtrace, i, j - 1, [('insert', i, j-1)] + accumulator)
        if i > 0 and j > 0 and D[i - 1, j - 1] + 1 == D[i, j]:
            return partial(_tail_backtrace, i - 1, j - 1, [('replace', i-1, j-1)] + accumulator)
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


def editops(word1, word2):
    # XXX Note that this returns indices to the _grapheme clusters_, not characters!
    word1 = list(grapheme_clusters(unicodedata.normalize('NFC', word1)))
    word2 = list(grapheme_clusters(unicodedata.normalize('NFC', word2)))
    return seq_editops(word1, word2)
