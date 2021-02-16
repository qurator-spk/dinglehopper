"""
Datastructures to be used with the Flexible Character Accuracy Algorithm

Separated because of version compatibility issues with Python 3.5.
"""

from collections import namedtuple
from typing import Dict


class PartVersionSpecific:
    def __init__(self, text: str = "", line: int = 0, start: int = 0):
        self.text = text
        self.line = line
        self.start = start

    def __eq__(self, other):
        return (
            self.line == other.line
            and self.start == other.start
            and self.text == other.text
        )

    def __hash__(self):
        return hash(self.text) ^ hash(self.line) ^ hash(self.start)

    def _asdict(self) -> Dict:
        return {
            "text": self.text,
            "line": self.line,
            "start": self.start,
        }


class Distance:
    def __init__(
        self, match: int = 0, replace: int = 0, delete: int = 0, insert: int = 0
    ):
        self.match = match
        self.replace = replace
        self.delete = delete
        self.insert = insert

    def _asdict(self) -> Dict:
        return {
            "match": self.match,
            "replace": self.replace,
            "delete": self.delete,
            "insert": self.insert,
        }

    def __eq__(self, other):
        return (
            self.match == other.match
            and self.replace == other.replace
            and self.delete == other.delete
            and self.insert == other.insert
        )

    def __hash__(self):
        return (
            hash(self.match)
            ^ hash(self.replace)
            ^ hash(self.delete)
            ^ hash(self.insert)
        )


Match = namedtuple("Match", ["gt", "ocr", "dist", "ops"])


class Coefficients:
    def __init__(
        self,
        edit_dist: int = 25,
        length_diff: int = 20,
        offset: int = 1,
        length: int = 4,
    ):
        self.edit_dist = edit_dist
        self.length_diff = length_diff
        self.offset = offset
        self.length = length
