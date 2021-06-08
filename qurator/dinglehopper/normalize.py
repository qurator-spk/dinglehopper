import unicodedata
from typing import Union

import uniseg.wordbreak
from uniseg.graphemecluster import grapheme_clusters

from .extracted_text import ExtractedText


def chars_normalized(s: Union[str, ExtractedText]):
    """Normalize characters in string."""
    if isinstance(s, ExtractedText):
        s = s.text
    return list(grapheme_clusters(unicodedata.normalize("NFC", s)))


def words(s: Union[str, ExtractedText]):
    """Extract words from a string"""

    if isinstance(s, ExtractedText):
        s = s.text

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

    # We follow Unicode Standard Annex #29 on Unicode Text Segmentation here:
    # Split on word boundaries using uniseg.wordbreak.words() and ignore all
    # "words" that contain only whitespace, punctuation "or similar characters."
    for word in uniseg.wordbreak.words(s):
        if all(unwanted(c) for c in word):
            pass
        else:
            yield word


def words_normalized(s: Union[str, ExtractedText]):
    """Extract words from string and normalize them."""
    if isinstance(s, ExtractedText):
        s = s.text
    return words(unicodedata.normalize("NFC", s))
