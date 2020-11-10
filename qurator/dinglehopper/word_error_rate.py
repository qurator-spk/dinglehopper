from __future__ import division

import unicodedata
from typing import Tuple, Iterable
from multimethod import multimethod

import uniseg.wordbreak

from .edit_distance import levenshtein
from . import ExtractedText


@multimethod
def words(s: str):
    """Extract words from a string"""

    # Patch uniseg.wordbreak.word_break to deal with our private use characters. See also
    # https://www.unicode.org/Public/UCD/latest/ucd/auxiliary/WordBreakProperty.txt
    old_word_break = uniseg.wordbreak.word_break

    def new_word_break(c, index=0):
        if 0xE000 <= ord(c) <= 0xF8FF:  # Private Use Area
            return "ALetter"
        else:
            return old_word_break(c, index)

    uniseg.wordbreak.word_break = new_word_break

    # Check if c is an unwanted character, i.e. whitespace, punctuation, or similar
    def unwanted(c):

        # See https://www.fileformat.info/info/unicode/category/index.htm
        # and https://unicodebook.readthedocs.io/unicode.html#categories
        unwanted_categories = "O", "M", "P", "Z", "S"
        unwanted_subcategories = "Cc", "Cf"

        subcat = unicodedata.category(c)
        cat = subcat[0]
        return cat in unwanted_categories or subcat in unwanted_subcategories

    # We follow Unicode Standard Annex #29 on Unicode Text Segmentation here: Split on word boundaries using
    # uniseg.wordbreak.words() and ignore all "words" that contain only whitespace, punctation "or similar characters."
    for word in uniseg.wordbreak.words(s):
        if all(unwanted(c) for c in word):
            pass
        else:
            yield word


@multimethod
def words(s: ExtractedText):
    return words(s.text)


@multimethod
def words_normalized(s: str):
    return words(unicodedata.normalize("NFC", s))


@multimethod
def words_normalized(s: ExtractedText):
    return words_normalized(s.text)


@multimethod
def word_error_rate_n(reference: str, compared: str) -> Tuple[float, int]:
    reference_seq = list(words_normalized(reference))
    compared_seq = list(words_normalized(compared))
    return word_error_rate_n(reference_seq, compared_seq)


@multimethod
def word_error_rate_n(
    reference: ExtractedText, compared: ExtractedText
) -> Tuple[float, int]:
    return word_error_rate_n(reference.text, compared.text)


@multimethod
def word_error_rate_n(reference: Iterable, compared: Iterable) -> Tuple[float, int]:
    reference_seq = list(reference)
    compared_seq = list(compared)

    d = levenshtein(reference_seq, compared_seq)
    n = len(reference_seq)

    if d == 0:
        return 0, n
    if n == 0:
        return float("inf"), n
    return d / n, n


def word_error_rate(reference, compared) -> float:
    wer, _ = word_error_rate_n(reference, compared)
    return wer
