import math
from math import ceil

from .edit_distance import *
from rapidfuzz.distance import Levenshtein

def align(t1, t2):
    """Align text."""
    s1 = list(grapheme_clusters(unicodedata.normalize("NFC", t1)))
    s2 = list(grapheme_clusters(unicodedata.normalize("NFC", t2)))
    return seq_align(s1, s2)


def score_hint(er: float, n: int) -> int | None:
    """Calculate RapidFuzz score hint for a given error rate and count.

    Gives the score hint for the distance functions (= expected distance) or None if
    the error rate is inf.
    """
    assert not math.isnan(er)
    try:
        score_hint = int(ceil(er * n))
    except (OverflowError, ValueError):
        # ceil(er * n) can be inf or NaN (for n == 0), so int() can throw an
        # OverflowError and a ValueError.
        score_hint = None
    return score_hint


def seq_align(s1, s2, score_hint=None):
    """Align general sequences."""
    s1 = list(s1)
    s2 = list(s2)
    ops = Levenshtein.editops(s1, s2, score_hint=score_hint)
    i = 0
    j = 0

    while i < len(s1) or j < len(s2):
        o = None
        try:
            ot = ops[0]
            if ot[1] == i and ot[2] == j:
                del ops[0]
                o = ot
        except IndexError:
            pass

        if o:
            if o[0] == "insert":
                yield None, s2[j]
                j += 1
            elif o[0] == "delete":
                yield s1[i], None
                i += 1
            elif o[0] == "replace":
                yield s1[i], s2[j]
                i += 1
                j += 1
        else:
            yield s1[i], s2[j]
            i += 1
            j += 1
