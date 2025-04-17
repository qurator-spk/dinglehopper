from __future__ import division, print_function

import math

import pytest

from .. import character_error_rate, plain_text
from .util import working_directory


@pytest.mark.integration
@pytest.mark.parametrize(
    "gt_file_content,ocr_file_content,cer_expected",
    [
        ("", "Lorem ipsum", 1.0),
        ("Lorem ipsum", "", 1.0),
        ("\ufeff", "Lorem ipsum", 1.0),
        ("Lorem ipsum", "\ufeff", 1.0),
        ("", "", 0.0),
        ("\ufeff", "", 0.0),
        ("", "\ufeff", 0.0),
    ],
)
def test_empty_files(tmp_path, gt_file_content, ocr_file_content, cer_expected):
    with working_directory(tmp_path):

        with open("gt.txt", "w") as gtf:
            gtf.write(gt_file_content)
        with open("ocr.txt", "w") as ocrf:
            ocrf.write(ocr_file_content)

        gt_text = plain_text("gt.txt")
        ocr_text = plain_text("ocr.txt")

        assert character_error_rate(gt_text, ocr_text) == cer_expected
