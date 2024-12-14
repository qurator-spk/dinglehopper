import json
import re

import pytest

from ..cli import process
from .util import working_directory


@pytest.mark.integration
def test_cli_json(tmp_path):
    """Test that the cli/process() yields a loadable JSON report"""

    with working_directory(tmp_path):
        with open("gt.txt", "w") as gtf:
            gtf.write("AAAAA")
        with open("ocr.txt", "w") as ocrf:
            ocrf.write("AAAAB")

        with open("gt.txt", "r") as gtf:
            print(gtf.read())
        process("gt.txt", "ocr.txt", "report")
        with open("report.json", "r") as jsonf:
            print(jsonf.read())
        with open("report.json", "r") as jsonf:
            j = json.load(jsonf)
            assert j["cer"] == pytest.approx(0.2)


@pytest.mark.integration
def test_cli_json_cer_is_infinity(tmp_path):
    """Test that the cli/process() yields a loadable JSON report when CER == inf"""

    with working_directory(tmp_path):
        with open("gt.txt", "w") as gtf:
            gtf.write("")  # Empty to yield CER == inf
        with open("ocr.txt", "w") as ocrf:
            ocrf.write("Not important")

        process("gt.txt", "ocr.txt", "report")
        with open("report.json", "r") as jsonf:
            j = json.load(jsonf)
            assert j["cer"] == pytest.approx(float("inf"))


@pytest.mark.integration
def test_cli_html(tmp_path):
    """Test that the cli/process() yields complete HTML report"""

    with working_directory(tmp_path):
        with open("gt.txt", "w") as gtf:
            gtf.write("AAAAA")
        with open("ocr.txt", "w") as ocrf:
            ocrf.write("AAAAB")

        process("gt.txt", "ocr.txt", "report")

        with open("report.html", "r") as htmlf:
            html_report = htmlf.read()
            print(html_report)

        assert re.search(r"CER: 0\.\d+", html_report)
        assert re.search(r"WER: 1\.0", html_report)
        assert len(re.findall("gt.*cdiff", html_report)) == 1
        assert len(re.findall("gt.*wdiff", html_report)) == 1
