from __future__ import division

import unicodedata

from uniseg.graphemecluster import grapheme_clusters

from qurator.dinglehopper.edit_distance import distance


def character_error_rate(reference, compared):
    d = distance(reference, compared)
    if d == 0:
        return 0

    n = len(list(grapheme_clusters(unicodedata.normalize('NFC', reference))))
    if n == 0:
        return float('inf')

    return d/n

    # XXX Should we really count newlines here?
