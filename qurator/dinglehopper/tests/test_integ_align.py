from __future__ import division, print_function

import os

import pytest
from lxml import etree as ET

from .. import align, page_text

data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


@pytest.mark.integration
def test_align_page_files():
    # In the fake OCR file, we changed 2 characters and replaced a fi ligature with fi.
    # → 4 elements in the alignment should be different.
    # NOTE: In this example, it doesn't matter that we work with "characters", not grapheme clusters.

    gt = page_text(ET.parse(os.path.join(data_dir, 'test-gt.page2018.xml')))
    ocr = page_text(ET.parse(os.path.join(data_dir, 'test-fake-ocr.page2018.xml')))

    result = list(align(gt, ocr))
    assert sum(left != right for left, right in result) == 4
