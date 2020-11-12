from .edit_distance import *


def align(t1, t2):
    """Align text."""
    s1 = list(grapheme_clusters(unicodedata.normalize("NFC", t1)))
    s2 = list(grapheme_clusters(unicodedata.normalize("NFC", t2)))
    return seq_align(s1, s2)


def seq_align_linewise(s1, s2, ops):
    """Align two lists of lines linewise."""
    assert len(s1) == len(s2)
    assert len(s2) == len(ops)
    for l1, l2, line_ops in zip(s1, s2, ops):
        yield from seq_align(l1, l2, ops=line_ops)


def seq_align(s1, s2, ops=None):
    """Align general sequences."""
    s1 = list(s1)
    s2 = list(s2)
    if not ops:
        ops = seq_editops(s1, s2)
    i = 0
    j = 0

    while i < len(s1) or j < len(s2):
        o = None
        try:
            ot = ops[0]
            if ot[1] == i and ot[2] == j:
                ops = ops[1:]
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
