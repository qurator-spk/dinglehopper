import os.path
import itertools
from typing import Iterator, Tuple




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
