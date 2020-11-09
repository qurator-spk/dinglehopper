"""
Implementation of the flexible character accuracy

Citation:
    Flexible character accuracy measure for reading-order-independent evaluation
    C. Clausner, S. Pletschacher, A. Antonacopoulos
    Pattern Recognition Letters, Volume 131, March 2020, Pages 390-397
Link: http://www.primaresearch.org/publications/PRL_Clausner_FlexibleCharacterAccuracy
DOI: https://doi.org/10.1016/j.patrec.2020.02.003

Note that we deviated from the original algorithm at some places.
"""

from collections import Counter
from functools import lru_cache, reduce
from itertools import product, takewhile
from typing import List, NamedTuple, Tuple, Optional

from . import editops


def flexible_character_accuracy(gt: str, ocr: str) -> Tuple[float, List["Match"]]:
    """Calculate the flexible character accuracy.

    Reference: contains steps 1-7 of the flexible character accuracy algorithm.

    :param gt: The ground truth text.
    :param ocr: The text to compare the ground truth with.
    :return: Score between 0 and 1 and match objects.
    """

    best_score = -float('inf')
    best_matches = []
    # TODO: this should be configurable
    combinations = product(range(15, 31, 5),
                           range(0, 24, 3),
                           range(0, 4, 1),
                           range(0, 6, 1))
    # TODO: place to parallelize the algorithm
    for (edit_dist, length_diff, offset, length) in combinations:
        coef = Coefficients(
            edit_dist=edit_dist,
            length_diff=length_diff,
            offset=offset,
            length=length
        )
        # Steps 1 - 6 of the flexible character accuracy algorithm.
        matches = match_with_coefficients(gt, ocr, coef)
        # Step 7 of the flexible character accuracy algorithm.
        score = character_accuracy_for_matches(matches)
        if score > best_score:
            best_score = score
            best_matches = matches
        # early breaking: we only need one perfect fit
        if best_score >= 1:
            break
    return best_score, best_matches


def match_with_coefficients(gt: str, ocr: str, coef: "Coefficients") -> List["Match"]:
    """Match ground truth with ocr and considers a given set of coefficients.

    Reference: contains steps 1 - 6 of the flexible character accuracy algorithm.

    :return: A list of match objects to score and align the texts.
    """
    # Steps 1 and 2 of the flexible character accuracy algorithm.
    ocr_lines = initialize_lines(ocr)
    gt_lines = initialize_lines(gt)

    matches = []

    # Step 5 of the flexible character accuracy algorithm.
    while len(gt_lines) != 0 and len(ocr_lines) != 0:
        # Steps 3 and 4 of the flexible character accuracy algorithm.
        match = match_longest_gt_lines(gt_lines, ocr_lines, coef)
        if match:
            matches.append(match)

    # Step 6 of the flexible character accuracy algorithm.
    # remaining lines are considered as deletes and inserts
    deletes = [distance(line, Part(text="", line=line.line, start=line.start))
               for line in gt_lines]
    inserts = [distance(Part(text="", line=line.line, start=line.start), line)
               for line in ocr_lines]

    return [*matches, *deletes, *inserts]


def match_longest_gt_lines(gt_lines: List["Part"],
                           ocr_lines: List["Part"],
                           coef: "Coefficients") -> Optional["Match"]:
    """Find the best match for the longest line(s) in ground truth.

    The longest lines in ground truth are matched against lines in ocr to find the
    best matching pair. This pair is then either considered a match on full line

    Reference: contains steps 3 and 4 of the flexible character accuracy algorithm.

    :return: Possible match object.
    """
    best_score, best_match, best_gt, best_ocr = -float('inf'), None, None, None
    if not ocr_lines:
        return best_match

    # Step 3 of the flexible character accuracy algorithm (variation).
    # Instead of the longest line we take all longest lines with equal length.
    length = min(gt_lines[0].length, ocr_lines[0].length)
    for gt_line in takewhile(lambda line: line.length >= length, gt_lines):
        match, ocr_line = match_gt_line(gt_line, ocr_lines, coef)
        score = 0 if not match else character_accuracy(match.dist)
        if score > best_score:
            best_score, best_match, best_gt, best_ocr = score, match, gt_line, ocr_line

    # Step 4 of the flexible character accuracy algorithm.
    # Remove on full match or split.
    if best_match and best_gt:
        splitted = remove_or_split(best_gt, best_match.gt, gt_lines)
        if splitted:
            gt_lines.append(best_match.gt)
            best_match = None
    if best_match and best_ocr:
        remove_or_split(best_ocr, best_match.ocr, ocr_lines)

    return best_match


def match_gt_line(gt_line: "Part",
                  ocr_lines: List["Part"],
                  coef: "Coefficients") -> Tuple[Optional["Match"],
                                                 Optional["Part"]]:
    """Match the given ground truth line against all the lines in ocr.

    Reference: contains steps 3 of the flexible character accuracy algorithm.

    TODO: Make penalty function configurable?
    TODO: Add empty ocr line to avoid having nonesense one character alignments?

    :return: Match object and the matched ocr line.
    """
    min_penalty = float('inf')
    best_match, best_ocr = None, None
    for ocr_line in ocr_lines:
        match = match_lines(gt_line, ocr_line)
        penalty = calculate_penalty(gt_line, ocr_line, match, coef)
        if penalty < min_penalty:
            min_penalty, best_match, best_ocr = penalty, match, ocr_line
    return best_match, best_ocr


def remove_or_split(original: "Part",
                    match: "Part",
                    lines: List["Part"]) -> bool:
    """Removes the matched line or splits it into parts.

    Reference: contains step 4 of the flexible character accuracy algorithm.

    :return: True if line was splitted.
    """
    splitted = False
    del lines[lines.index(original)]
    if match.length < original.length:
        lines.extend(original.split(match))
        # sorting for ocr is not mentioned in the paper, but is used as tie breaking =)
        lines.sort(key=lambda x: x.length, reverse=True)
        splitted = True
    return splitted


@lru_cache(maxsize=1000000)
def match_lines(gt_line: "Part", ocr_line: "Part") -> Optional["Match"]:
    """Matches two lines searching for a local alignment.

    The shorter line is moved along the longer line
    until the editing distance is minimized.

    Reference: see figure 2 in the paper.

    TODO: make distance function configurable?

    :return: Match object if one is found.
    """
    min_length = min(gt_line.length, ocr_line.length)
    best_match = None
    if min_length == 0:
        return best_match
    length_diff = gt_line.length - ocr_line.length
    min_edit_dist = float('inf')
    # TODO: handle deletes and replacements by extending the length.
    for i in range(0, max(1, length_diff + 1)):
        for j in range(0, max(1, -1 * length_diff + 1)):
            match = distance(gt_line.substring(rel_start=i, rel_end=i + min_length),
                             ocr_line.substring(rel_start=j, rel_end=j + min_length))
            edit_dist = score_edit_distance(match)
            if edit_dist < min_edit_dist:
                min_edit_dist = edit_dist
                best_match = match
    return best_match


@lru_cache(maxsize=1000000)
def distance(gt: "Part", ocr: "Part") -> "Match":
    """Calculate the editing distance between the two lines.

    Using the already available `editops()` function with the Levenshtein distance.

    TODO: replace with @cache annotation in Python 3.9

    :return: Match object containing the lines and the editing operations.
    """
    ops = editops(gt.text, ocr.text)
    edits = Counter([edit[0] for edit in ops])
    edits["match"] = gt.length - edits["delete"] - edits["replace"]
    return Match(gt=gt, ocr=ocr, dist=Distance(**edits), ops=ops)


def score_edit_distance(match: "Match") -> int:
    """Calculate edit distance for a match.

    Formula: $deletes + inserts + 2 * replacements$

    :return: Sum of deletes, inserts and replacements.
    """
    return match.dist.delete + match.dist.insert + 2 * match.dist.replace


def calculate_penalty(gt: "Part", ocr: "Part", match: "Match",
                      coef: "Coefficients") -> float:
    """Calculate the penalty for a given match.

    For details and discussion see Section 3 in doi:10.1016/j.patrec.2020.02.003.

    :return: Penalty for the given match.
    """
    min_edit_dist = score_edit_distance(match)
    length_diff = abs(gt.length - ocr.length)
    substring_length = min(gt.length, ocr.length)
    offset = 0.0
    if length_diff > 1:
        substring_pos = max(match.gt.start - gt.start, match.ocr.start - ocr.start)
        offset = length_diff / 2 - abs(substring_pos - length_diff / 2)
    return (min_edit_dist * coef.edit_dist
            + length_diff * coef.length_diff
            + offset * coef.offset
            - substring_length * coef.length)


def character_accuracy_for_matches(matches: List["Match"]) -> float:
    """Character accuracy of a full text represented by a list of matches.

    See other `character_accuracy` for details.

    """
    agg: Counter = reduce(lambda acc, match: acc + Counter(match.dist._asdict()),
                          matches, Counter())

    score = character_accuracy(Distance(**agg))
    return score


def character_accuracy(edits: "Distance") -> float:
    """Character accuracy calculated by necessary edit operations.

    Edit operations are needed edits to transform one text into another.

    The character accuracy is given by $1 - errors / characters$.

    Errors are replacements, deletes and inserts.

    Note that is is possible to have more errors than characters in which case the
    character accuracy turns negative.

    Comparing two empty strings (having no edits) results in a character accuracy of 1.
    """
    errors = edits.replace + edits.delete + edits.insert
    chars = edits.match + edits.replace + edits.delete
    if not chars and not errors:
        # comparison of empty strings is considered a full match
        score = 1
    else:
        score = 1 - errors / chars
    return score


def initialize_lines(text: str) -> List["Part"]:
    """Splits a text into lines and converts them to our line data object.

    The line objects are sorted by their length descending.

    Reference: contains steps 1 and 2 of the flexible character accuracy algorithm.

    :param text: Text to split into lines.
    :return: List of sorted line objects.
    """
    lines = [Part(text=line, line=i, start=0)
             for i, line in enumerate(text.splitlines())
             if len(line) > 0]
    lines.sort(key=lambda x: x.length, reverse=True)
    return lines


def combine_lines(matches: List["Match"]) -> Tuple[str, str]:
    """Combines the matches to aligned texts.

    TODO: just hacked, needs tests and refinement. Also missing insert/delete marking.

    :param matches: List of match objects.
    :return: the aligned ground truth and ocr as texts.
    """
    matches.sort(key=lambda x: x.gt.line + x.gt.start / 10000)
    line = 0
    gt, ocr = "", ""
    for match in matches:
        if match.gt.line > line:
            gt += "\n"
            ocr += "\n"
            line += 1
        gt += match.gt.text
        ocr += match.ocr.text
    return gt, ocr


class Part(NamedTuple):
    """Represent a line or part of a line.

    This data object is maintained to be able to reproduce the original text.
    """
    text: str = ""
    line: int = 0
    start: int = 0

    @property
    def end(self) -> int:
        return self.start + self.length

    @property
    def length(self) -> int:
        return len(self.text)

    def split(self, split: "Part") -> List["Part"]:
        """Split the line part by another and returns the remaining parts.

        `abc.split("b")` will return ´["a", "c"]`.

        :param split: The line part we want to use to split.
        :return: The parts before and after the split.
        """
        rest = []
        if self.start < split.start:
            rest.append(self.substring(rel_end=split.start - self.start))
        if split.end < self.end:
            rest.append(self.substring(rel_start=split.end - self.start))
        return rest

    def substring(self, rel_start: int = 0, rel_end: int = None) -> "Part":
        """Get part of the given line.

        Automatically handles the offset of the line.
        Therefore `substring(rel_start=2)` will return `Part[start+rel_start:]`.

        :param rel_start: start relative to the part of the line.
        :param rel_end: end relative to the part of the line.
        :return: Extracted part of the given part of the line.
        """
        text = self.text[rel_start:rel_end]
        start = self.start + rel_start
        return Part(text=text, line=self.line, start=start)


class Distance(NamedTuple):
    """Represent distance between two sequences."""
    match: int = 0
    replace: int = 0
    delete: int = 0
    insert: int = 0


class Match(NamedTuple):
    """Represent a calculated match between ground truth and the ocr result."""
    gt: "Part"
    ocr: "Part"
    dist: "Distance"
    ops: List


class Coefficients(NamedTuple):
    """Coefficients to calculate penalty for substrings.

    See Section 3 in doi:10.1016/j.patrec.2020.02.003
    """
    edit_dist: int = 25
    length_diff: int = 20
    offset: int = 1
    length: int = 4
