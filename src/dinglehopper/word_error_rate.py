import unicodedata
from typing import Generator, Iterable, Tuple, TypeVar

import uniseg.wordbreak
from multimethod import multimethod
from rapidfuzz.distance import Levenshtein

from .extracted_text import ExtractedText

T = TypeVar("T")

# Did we patch uniseg.wordbreak.word_break already?
word_break_patched = False


def patch_word_break():
    """
    Patch uniseg.wordbreak.word_break to deal with our private use characters.

    See also
    https://www.unicode.org/Public/UCD/latest/ucd/auxiliary/WordBreakProperty.txt
    """
    old_word_break = uniseg.wordbreak.word_break
    if hasattr(uniseg.wordbreak, 'Word_Break'):
        aletter = uniseg.wordbreak.Word_Break.ALetter
    else:
        # uniseg<0.9
        aletter = uniseg.wordbreak.WordBreak.ALETTER

    def new_word_break(c):
        if 0xE000 <= ord(c) <= 0xF8FF:  # Private Use Area
            return aletter
        else:
            return old_word_break(c)

    uniseg.wordbreak.word_break = new_word_break
    global word_break_patched
    word_break_patched = True


@multimethod
def words(s: str) -> Generator[str, None, None]:
    """Extract words from a string"""

    global word_break_patched
    if not word_break_patched:
        patch_word_break()

    # Check if c is an unwanted character, i.e. whitespace, punctuation, or similar
    def unwanted(c):
        # See https://www.fileformat.info/info/unicode/category/index.htm
        # and https://unicodebook.readthedocs.io/unicode.html#categories
        unwanted_categories = "O", "M", "P", "Z", "S"
        unwanted_subcategories = "Cc", "Cf"

        subcat = unicodedata.category(c)
        cat = subcat[0]
        return cat in unwanted_categories or subcat in unwanted_subcategories

    # We follow Unicode Standard Annex #29 on Unicode Text Segmentation here: Split on
    # word boundaries using uniseg.wordbreak.words() and ignore all "words" that contain
    # only whitespace, punctuation "or similar characters."
    for word in uniseg.wordbreak.words(s):
        if all(unwanted(c) for c in word):
            pass
        else:
            yield word


@words.register
def _(s: ExtractedText) -> Generator[str, None, None]:
    yield from words(s.text)


@multimethod
def words_normalized(s: str) -> Generator[str, None, None]:
    yield from words(unicodedata.normalize("NFC", s))


@words_normalized.register
def _(s: ExtractedText) -> Generator[str, None, None]:
    yield from words_normalized(s.text)


@multimethod
def word_error_rate_n(reference: str, compared: str) -> Tuple[float, int]:
    reference_seq = list(words_normalized(reference))
    compared_seq = list(words_normalized(compared))
    wer, n = word_error_rate_n(reference_seq, compared_seq)
    return wer, n


@word_error_rate_n.register
def _(reference: ExtractedText, compared: ExtractedText) -> Tuple[float, int]:
    wer, n = word_error_rate_n(reference.text, compared.text)
    return wer, n


@word_error_rate_n.register
def _(reference: Iterable[T], compared: Iterable[T]) -> Tuple[float, int]:
    reference_seq = list(reference)
    compared_seq = list(compared)

    d = Levenshtein.normalized_distance(reference_seq, compared_seq)
    n = len(reference_seq)

    return d, n

def word_error_rate(reference: T, compared: T) -> float:
    wer: float
    wer, _ = word_error_rate_n(reference, compared)
    return wer
