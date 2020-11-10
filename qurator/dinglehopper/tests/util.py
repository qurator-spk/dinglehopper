from itertools import zip_longest
from typing import Iterable

import colorama
import os


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


def unzip(an_iterable_of_tuples):
    return zip(*an_iterable_of_tuples)


class working_directory:
    """Context manager to temporarily change the working directory"""

    def __init__(self, wd):
        self.wd = wd

    def __enter__(self):
        self.old_wd = os.getcwd()
        os.chdir(self.wd)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.old_wd)
