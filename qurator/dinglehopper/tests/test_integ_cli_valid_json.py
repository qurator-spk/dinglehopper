import json
from itertools import combinations

import pytest
from .util import working_directory

from ..cli import process


@pytest.mark.integration
@pytest.mark.parametrize(
    "metrics",
    [
        *(("",), ("cer",), ("wer",), ("fca",)),
        *combinations(("cer", "wer", "fca"), 2),
        ("cer", "wer", "fca"),
    ],
)
def test_cli_json(metrics, tmp_path):
    """Test that the cli/process() yields a loadable JSON report"""

    expected_values = {"cer": 0.2, "wer": 1.0, "fca": 0.8}

    with working_directory(str(tmp_path)):
        with open("gt.txt", "w") as gtf:
            gtf.write("AAAAA")
        with open("ocr.txt", "w") as ocrf:
            ocrf.write("AAAAB")

        with open("gt.txt", "r") as gtf:
            print(gtf.read())

        process("gt.txt", "ocr.txt", "report", metrics=",".join(metrics))

        with open("report.json", "r") as jsonf:
            print(jsonf.read())
        with open("report.json", "r") as jsonf:
            j = json.load(jsonf)
            for metric, expected_value in expected_values.items():
                if metric in metrics:
                    assert j[metric] == pytest.approx(expected_values[metric])
                else:
                    assert metric not in j.keys()


@pytest.mark.integration
def test_cli_json_cer_is_infinity(tmp_path):
    """Test that the cli/process() yields a loadable JSON report when CER == inf"""

    with working_directory(str(tmp_path)):
        with open("gt.txt", "w") as gtf:
            gtf.write("")  # Empty to yield CER == inf
        with open("ocr.txt", "w") as ocrf:
            ocrf.write("Not important")

        process("gt.txt", "ocr.txt", "report", metrics="cer,wer,fca")
        with open("report.json", "r") as jsonf:
            j = json.load(jsonf)
            assert j["cer"] == pytest.approx(float("inf"))
            assert j["fca"] == pytest.approx(-13)
