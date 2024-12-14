import json
import os.path
import re

import pytest

from ..cli_line_dirs import process
from .util import working_directory

data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


@pytest.mark.integration
def test_cli_line_dirs_basic(tmp_path):
    """Test that the cli/process() produces a good report"""

    with working_directory(tmp_path):
        gt_dir = os.path.join(data_dir, "line_dirs/basic/gt")
        ocr_dir = os.path.join(data_dir, "line_dirs/basic/ocr")
        process(gt_dir, ocr_dir, "report")
        with open("report.json", "r") as jsonf:
            print(jsonf.read())
        with open("report.json", "r") as jsonf:
            j = json.load(jsonf)
            assert j["cer"] == pytest.approx(0.1071429)
            assert j["wer"] == pytest.approx(0.5)


@pytest.mark.integration
def test_cli_line_dirs_basic_report_diff(tmp_path):
    """Test that the cli/process() produces a report wiff char+word diff"""

    with working_directory(tmp_path):
        gt_dir = os.path.join(data_dir, "line_dirs/basic/gt")
        ocr_dir = os.path.join(data_dir, "line_dirs/basic/ocr")
        process(gt_dir, ocr_dir, "report")

        with open("report.html", "r") as htmlf:
            html_report = htmlf.read()

    # Counting GT lines in the diff
    assert len(re.findall(r"gt.*l\d+-cdiff", html_report)) == 2
    assert len(re.findall(r"gt.*l\d+-wdiff", html_report)) == 2


@pytest.mark.integration
def test_cli_line_dirs_merged(tmp_path):
    """Test that the cli/process() produces a good report"""

    with working_directory(tmp_path):
        gt_dir = os.path.join(data_dir, "line_dirs/merged")
        ocr_dir = os.path.join(data_dir, "line_dirs/merged")
        process(
            gt_dir, ocr_dir, "report", gt_suffix=".gt.txt", ocr_suffix=".some-ocr.txt"
        )
        with open("report.json", "r") as jsonf:
            print(jsonf.read())
        with open("report.json", "r") as jsonf:
            j = json.load(jsonf)
            assert j["cer"] == pytest.approx(0.1071429)
            assert j["wer"] == pytest.approx(0.5)
