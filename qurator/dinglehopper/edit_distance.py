from __future__ import division, print_function

import unicodedata
from functools import partial

import numpy as np
from uniseg.graphemecluster import grapheme_clusters


def levenshtein_matrix(seq1, seq2):
    """Compute the matrix commonly computed to produce the Levenshtein distance.

    This is also known as the Wagner-Fischer algorithm. The matrix element at the bottom right contains the desired
    edit distance.

    This algorithm is implemented here because we need an implementation that can work with sequences other than
    strings, e.g. lists of grapheme clusters or lists of word strings.
    """

    m = len(seq1)
    n = len(seq2)

    D = np.ones((m + 1, n + 1), np.int)
    D[:,0] = np.arange(m+1)
    D[0,:] = np.arange(n+1)

    if m > 10 and n > 10:
        # All grapheme which occur in both sets
        interset = set(seq1).intersection(set(seq2))

        # Generate a boolean-mask for each interset grapheme
        masks = {grapheme: [0] * (len(seq2) + 1) for grapheme in interset}

        for idx, grapheme in enumerate(seq2):
            if grapheme in interset:
                masks[grapheme][idx] = -1

        # Calculate the levensthein matrix
        for row, grapheme in enumerate(seq1):
            if seq1[row] in interset:
                mask = masks[grapheme]
                for col in range(0,n):
                    D[row + 1, col + 1] = min(D[row, col] + mask[col], D[row + 1, col], D[row, col + 1])+1
            else:
                for col in range(0,n):
                    D[row+1,col+1] = min(D[row,col],D[row+1,col],D[row,col+1])+1

    else:
        for i in range(1, m+1):
            for j in range(1, n+1):
                E[i, j] = min(
                    E[i - 1, j - 1] + 1 * (seq1[i - 1] != seq2[j - 1]),  # Same or Substitution
                    E[i, j - 1] + 1,  # Insertion
                    E[i - 1, j] + 1   # Deletion
                )

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
