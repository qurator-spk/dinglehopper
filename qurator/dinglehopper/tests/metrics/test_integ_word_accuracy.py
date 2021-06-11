from __future__ import division, print_function

import os

import pytest
from lxml import etree as ET

from ... import alto_text, page_text
from ...metrics import word_accuracy
from ...normalize import words

data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../", "data")


@pytest.mark.integration
def test_word_error_rate_between_page_files():
    # In the fake OCR file, we changed 2 characters and replaced a fi ligature with fi. So we have 3 changed words,
    # the ligature does not count → 2 errors
    gt = page_text(ET.parse(os.path.join(data_dir, "test-gt.page2018.xml")))

    gt_word_count = (
        7 + 6 + 5 + 8 + 7 + 6 + 7 + 8 + 6 + 7 + 7 + 5 + 6 + 8 + 8 + 7 + 7 + 6 + 5 + 4
    )  # Manually verified word count per line
    assert len(list(words(gt))) == gt_word_count

    ocr = page_text(ET.parse(os.path.join(data_dir, "test-fake-ocr.page2018.xml")))
    assert word_accuracy(gt, ocr).error_rate == 2 / gt_word_count


@pytest.mark.integration
def test_word_error_rate_between_page_alto():
    gt = page_text(
        ET.parse(os.path.join(data_dir, "lorem-ipsum", "lorem-ipsum-scan.gt.page.xml"))
    )
    ocr = alto_text(
        ET.parse(
            os.path.join(
                data_dir, "lorem-ipsum", "lorem-ipsum-scan.ocr.tesseract.alto.xml"
            )
        )
    )

    assert gt == ocr
    assert word_accuracy(gt, ocr).error_rate == 0


@pytest.mark.integration
def test_word_error_rate_between_page_alto_2():
    gt = page_text(
        ET.parse(
            os.path.join(data_dir, "lorem-ipsum", "lorem-ipsum-scan-bad.gt.page.xml")
        )
    )

    gt_word_count = (
        14 + 18 + 17 + 14 + 17 + 17 + 3
    )  # Manually verified word count per line
    assert len(list(words(gt))) == gt_word_count

    ocr = alto_text(
        ET.parse(
            os.path.join(
                data_dir, "lorem-ipsum", "lorem-ipsum-scan-bad.ocr.tesseract.alto.xml"
            )
        )
    )

    assert (
        word_accuracy(gt, ocr).error_rate == 7 / gt_word_count
    )  # Manually verified, 6 words are wrong, 1 got split (=2 errors)
