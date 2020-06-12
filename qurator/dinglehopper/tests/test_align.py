from .util import unzip
from .. import align, seq_align, distance


def test_left_empty():
    result = list(align('', 'foo'))
    expected = [(None, 'f'), (None, 'o'), (None, 'o')]
    assert result == expected


def test_right_empty():
    result = list(align('foo', ''))
    expected = [('f', None), ('o', None), ('o', None)]
    assert result == expected


def test_left_longer():
    result = list(align('food', 'foo'))
    expected = [('f', 'f'), ('o', 'o'), ('o', 'o'), ('d', None)]
    assert result == expected


def test_right_longer():
    result = list(align('foo', 'food'))
    expected = [('f', 'f'), ('o', 'o'), ('o', 'o'), (None, 'd')]
    assert result == expected


def test_some_diff():
    result = list(align('abcde', 'aaadef'))
    left, right = unzip(result)
    assert list(left) == ['a', 'b', 'c', 'd', 'e', None]
    assert list(right) == ['a', 'a', 'a', 'd', 'e', 'f']


def test_longer():
    s1 = 'Dies ist eine Tst!'
    s2 = 'Dies ist ein Test.'

    result = list(align(s1, s2))  # ; diffprint(*unzip(result))
    expected = [('D', 'D'), ('i', 'i'), ('e', 'e'), ('s', 's'), (' ', ' '),
                ('i', 'i'), ('s', 's'), ('t', 't'), (' ', ' '),
                ('e', 'e'), ('i', 'i'), ('n', 'n'), ('e', None), (' ', ' '),
                ('T', 'T'), (None, 'e'), ('s', 's'), ('t', 't'), ('!', '.')]
    assert result == expected


def test_completely_different():
    assert len(list(align('abcde', 'fghij'))) == 5


def test_with_some_fake_ocr_errors():
    result = list(align('Über die vielen Sorgen wegen desselben vergaß',
                        'SomeJunk MoreJunk Übey die vielen Sorgen wegen AdditionalJunk deffelben vcrgab'))
    left, right = unzip(result)

    # Beginning
    assert list(left[:18]) == [None]*18
    assert list(right[:18]) == list('SomeJunk MoreJunk ')

    # End
    assert list(left[-1:]) == ['ß']
    assert list(right[-1:]) == ['b']


def test_lines():
    """Test comparing list of lines.

    This mainly serves as documentation for comparing lists of lines.
    """
    result = list(seq_align(
        ['This is a line.', 'This is another', 'And the last line'],
        ['This is a line.', 'This is another', 'J  u   n      k', 'And the last line']
    ))
    left, right = unzip(result)
    assert list(left)  == ['This is a line.', 'This is another', None,              'And the last line']
    assert list(right) == ['This is a line.', 'This is another', 'J  u   n      k', 'And the last line']


def test_lines_similar():
    """
    Test comparing list of lines while using a "weaker equivalence".

    This mainly serves as documentation.
    """

    class SimilarString:
        def __init__(self, string):
            self._string = string

        def __eq__(self, other):
            # Just an example!
            min_len = min(len(self._string), len(other._string))
            if min_len > 0:
                normalized_distance = distance(self._string, other._string)/min_len
                similar = normalized_distance < 0.1
            else:
                similar = False
            return similar

        def __ne__(self, other):
            return not self.__eq__(other)

        def __repr__(self):
            return 'SimilarString(\'%s\')' % self._string

        def __hash__(self):
            return hash(self._string)

    result = list(seq_align(
        [SimilarString('This is a line.'), SimilarString('This is another'),                                   SimilarString('And the last line')],
        [SimilarString('This is a ljne.'), SimilarString('This is another'), SimilarString('J  u   n      k'), SimilarString('And the last line')]
    ))
    left, right = unzip(result)
    assert list(left)  == [SimilarString('This is a line.'), SimilarString('This is another'), None,                             SimilarString('And the last line')]
    assert list(right) == [SimilarString('This is a ljne.'), SimilarString('This is another'), SimilarString('J  u   n      k'), SimilarString('And the last line')]

    # Test __eq__ (i.e. is it a substitution or a similar string?)
    assert list(left)[0] == list(right)[0]
