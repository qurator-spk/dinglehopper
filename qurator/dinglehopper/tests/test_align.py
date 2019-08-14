from .util import unzip
from .. import align


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
