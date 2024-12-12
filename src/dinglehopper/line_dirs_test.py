import os.path
import itertools
from typing import Iterator, Tuple

def is_hidden(filepath):
    filename = os.path.basename(os.path.abspath(filepath))
    return filename.startswith(".")

def find_all_files(dir_: str, pred=None, return_hidden=False) -> Iterator[str]:
    """
    Find all files in dir_, returning filenames

    If pred is given, pred(filename) must be True for the filename.

    Does not return hidden files by default.
    """
    for root, _, filenames in os.walk(dir_):
        for fn in filenames:
            if not return_hidden and is_hidden(fn):
                continue
            if pred and not pred(fn):
                continue
            yield os.path.join(root, fn)


def find_gt_and_ocr_files(gt_dir, gt_suffix, ocr_dir, ocr_suffix) -> Iterator[Tuple[str, str]]:
    """
    Find GT files and matching OCR files.

    Returns pairs of GT and OCR files.
    """
    for gt_fn in find_all_files(gt_dir, lambda fn: fn.endswith(gt_suffix)):
        ocr_fn = os.path.join(
            ocr_dir,
            os.path.relpath(gt_fn, start=gt_dir).removesuffix(gt_suffix)
            + ocr_suffix,
        )
        if not os.path.exists(ocr_fn):
            raise RuntimeError(f"{ocr_fn} (matching {gt_fn}) does not exist")

        yield gt_fn, ocr_fn

def all_equal(iterable):
    g = itertools.groupby(iterable)
    return next(g, True) and not next(g, False)

def common_prefix(its):
    return [p[0] for p in itertools.takewhile(all_equal, zip(*its))]


def common_suffix(its):
    return reversed(common_prefix(reversed(it) for it in its))


def find_gt_and_ocr_files_autodetect(gt_dir, ocr_dir):
    """
    Find GT files and matching OCR files, autodetect suffixes.

    This only works if gt_dir (or respectivley ocr_dir) only contains GT (OCR)
    files with a common suffix. Currently the files must have a suffix, e.g.
    ".gt.txt" (e.g. ".ocr.txt").

    Returns pairs of GT and OCR files.
    """

    # Autodetect suffixes
    gt_files = find_all_files(gt_dir)
    gt_suffix = "".join(common_suffix(gt_files))
    if len(gt_suffix) == 0:
        raise RuntimeError(f"Files in GT directory {gt_dir} do not have a common suffix")
    ocr_files = find_all_files(ocr_dir)
    ocr_suffix = "".join(common_suffix(ocr_files))
    if len(ocr_suffix) == 0:
        raise RuntimeError(f"Files in OCR directory {ocr_dir} do not have a common suffix")

    yield from find_gt_and_ocr_files(gt_dir, gt_suffix, ocr_dir, ocr_suffix)


def test_basic():
    """Test the dumb method: User gives directories and suffixes."""
    pairs = list(
        find_gt_and_ocr_files(
            "line_dirs_test/basic/gt",
            ".gt.txt",
            "line_dirs_test/basic/ocr",
            ".some-ocr.txt",
        )
    )

    assert len(pairs) == 2

def test_basic_autodetect():
    """Test the autodetect method: User gives directories, suffixes are autodetected if possible"""
    pairs = list(
        find_gt_and_ocr_files_autodetect(
            "line_dirs_test/basic/gt",
            "line_dirs_test/basic/ocr",
        )
    )

    assert len(pairs) == 2


def test_subdirs():
    """Test the dumb method: Should also work when subdirectories are involved."""
    pairs = list(
        find_gt_and_ocr_files(
            "line_dirs_test/subdirs/gt",
            ".gt.txt",
            "line_dirs_test/subdirs/ocr",
            ".some-ocr.txt",
        )
    )

    assert len(pairs) == 2


def test_subdirs_autodetect():
    """Test the autodetect method: Should also work when subdirectories are involved."""
    pairs = list(
        find_gt_and_ocr_files_autodetect(
            "line_dirs_test/subdirs/gt",
            "line_dirs_test/subdirs/ocr",
        )
    )

    assert len(pairs) == 2

def test_merged():
    """Test the dumb method: Should also work when GT and OCR texts are in the same directories."""
    pairs = list(
        find_gt_and_ocr_files(
            "line_dirs_test/merged",
            ".gt.txt",
            "line_dirs_test/merged",
            ".some-ocr.txt",
        )
    )

    assert len(pairs) == 2

if __name__ == "__main__":
    test_basic()
    test_subdirs()
    test_merged()

    test_basic_autodetect()
    test_subdirs_autodetect()
