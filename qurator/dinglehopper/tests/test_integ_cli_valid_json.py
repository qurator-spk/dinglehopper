import json

import pytest
from .util import working_directory

from ..cli import process


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
