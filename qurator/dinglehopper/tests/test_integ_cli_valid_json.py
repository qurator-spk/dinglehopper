import json
from itertools import combinations

import pytest

from .util import working_directory
from ..cli import process

METRIC_DICT = {
    "": "",
    "ca": "character_accuracy",
    "cer": "character_accuracy",
    "wa": "word_accuracy",
    "wer": "word_accuracy",
    "boc": "bag_of_chars_accuracy",
    "bow": "bag_of_words_accuracy",
}


@pytest.mark.integration
@pytest.mark.parametrize(
    "metrics",
    [
        *(("",), ("cer",), ("wer",), ("ca",), ("wa",), ("boc",), ("bow",)),
        *combinations(("ca", "wa", "boc", "bow"), 2),
        *combinations(("cer", "wer", "boc", "bow"), 2),
        *combinations(("ca", "wa", "boc", "bow"), 3),
        *combinations(("cer", "wer", "boc", "bow"), 3),
        ("ca", "wa", "boc", "bow"),
        ("cer", "wer", "boc", "bow"),
    ],
)
def test_cli_json(metrics, tmp_path):
    """Test that the cli/process() yields a loadable JSON report."""
    expected_values = {
        "character_accuracy": 0.2,
        "word_accuracy": 1.0,
        "bag_of_chars_accuracy": 0.2,
        "bag_of_words_accuracy": 1.0,
    }

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
            metrics_translated = {METRIC_DICT[metric] for metric in metrics}
            for metric, expected_value in expected_values.items():
                if metric in metrics_translated:
                    assert j[metric]["error_rate"] == pytest.approx(expected_value)
                else:
                    assert metric not in j.keys()


@pytest.mark.integration
@pytest.mark.parametrize(
    "gt,ocr,err",
    [("", "Not important", float("inf")), ("Lorem Ipsum", "Lorem Ipsum", 0)],
)
def test_cli_json_extremes(gt, ocr, err, tmp_path):
    """Test that the cli/process() yields a loadable JSON reports."""

    with working_directory(str(tmp_path)):
        with open("gt.txt", "w") as gtf:
            gtf.write(gt)
        with open("ocr.txt", "w") as ocrf:
            ocrf.write(ocr)

        process("gt.txt", "ocr.txt", "report", metrics="ca,wa,boc,bow")
        with open("report.json", "r") as jsonf:
            j = json.load(jsonf)
            for metric in set(METRIC_DICT.values()):
                if not metric:
                    continue
                assert j[metric]["error_rate"] == pytest.approx(err)
