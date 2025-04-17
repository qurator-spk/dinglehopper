from __future__ import division, print_function

import os

import pytest
from lxml import etree as ET

from .. import alto_text, distance, page_text

data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


@pytest.mark.integration
def test_distance_between_page_files():
    # In the fake OCR file, we changed 2 characters and replaced a fi ligature with fi.
    # Due to normalization, we don't count the ligature.
    # → 2 differences
    gt = page_text(ET.parse(os.path.join(data_dir, "test-gt.page2018.xml")))
    ocr = page_text(ET.parse(os.path.join(data_dir, "test-fake-ocr.page2018.xml")))
    assert distance(gt, ocr) == 2 / 827


@pytest.mark.integration
def test_distance_between_page_alto():
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
    assert distance(gt, ocr) == 0


@pytest.mark.integration
def test_distance_between_page_alto_2():
    gt = page_text(
        ET.parse(
            os.path.join(data_dir, "lorem-ipsum", "lorem-ipsum-scan-bad.gt.page.xml")
        )
    )
    ocr = alto_text(
        ET.parse(
            os.path.join(
                data_dir, "lorem-ipsum", "lorem-ipsum-scan-bad.ocr.tesseract.alto.xml"
            )
        )
    )

    assert distance(gt, ocr) == 8 / 594  # Manually verified
