from itertools import zip_longest
from typing import Iterable

import colorama


def diffprint(x, y):
    """Print elements or lists x and y, with differences in red"""

    def _diffprint(x, y):
        if x != y:
            print(colorama.Fore.RED, x, y, colorama.Fore.RESET)
        else:
            print(x, y)

    if isinstance(x, Iterable):
        for xe, ye in zip_longest(x, y):
            _diffprint(xe, ye)
    else:
        _diffprint(x, y)


def unzip(l):
    return zip(*l)
