import os

from ..cli_line_dirs import find_gt_and_ocr_files, find_gt_and_ocr_files_autodetect

data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def test_basic():
    """Test the dumb method: User gives directories and suffixes."""
    pairs = list(
        find_gt_and_ocr_files(
            os.path.join(data_dir, "line_dirs/basic/gt"),
            ".gt.txt",
            os.path.join(data_dir, "line_dirs/basic/ocr"),
            ".some-ocr.txt",
        )
    )

    assert len(pairs) == 2


def test_basic_autodetect():
    """Test autodetect: User gives directories, suffixes are autodetected if possible"""
    pairs = list(
        find_gt_and_ocr_files_autodetect(
            os.path.join(data_dir, "line_dirs/basic/gt"),
            os.path.join(data_dir, "line_dirs/basic/ocr"),
        )
    )

    assert len(pairs) == 2


def test_subdirs():
    """Test the dumb method: Should also work when subdirectories are involved."""
    pairs = list(
        find_gt_and_ocr_files(
            os.path.join(data_dir, "line_dirs/subdirs/gt"),
            ".gt.txt",
            os.path.join(data_dir, "line_dirs/subdirs/ocr"),
            ".some-ocr.txt",
        )
    )

    assert len(pairs) == 2


def test_subdirs_autodetect():
    """Test the autodetect method: Should also work when subdirectories are involved."""
    pairs = list(
        find_gt_and_ocr_files_autodetect(
            os.path.join(data_dir, "line_dirs/subdirs/gt"),
            os.path.join(data_dir, "line_dirs/subdirs/ocr"),
        )
    )

    assert len(pairs) == 2


def test_merged():
    """Test the dumb method: GT and OCR texts are in the same directories."""
    pairs = list(
        find_gt_and_ocr_files(
            os.path.join(data_dir, "line_dirs/merged"),
            ".gt.txt",
            os.path.join(data_dir, "line_dirs/merged"),
            ".some-ocr.txt",
        )
    )

    assert len(pairs) == 2
