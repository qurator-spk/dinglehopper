import os

import pytest
from lxml import etree as ET

from .. import distance, page_text, extract
from .. import flexible_character_accuracy, split_matches

data_dir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data", "table-order"
)


@pytest.mark.parametrize("file", ["table-order-0002.xml", "table-no-reading-order.xml"])
@pytest.mark.integration
def test_fac_ignoring_reading_order(file):
    expected = "1\n2\n3\n4\n5\n6\n7\n8\n9"

    gt = page_text(ET.parse(os.path.join(data_dir, "table-order-0001.xml")))
    assert gt == expected

    ocr = page_text(ET.parse(os.path.join(data_dir, file)))
    assert distance(gt, ocr) > 0

    fac, matches = flexible_character_accuracy(gt, ocr)
    assert fac == pytest.approx(1.0)

    gt_segments, ocr_segments, ops = split_matches(matches)
    assert not any(ops)
    assert "".join(gt_segments) == expected
    assert "".join(ocr_segments) == expected


@pytest.mark.parametrize(
    "file,expected_text",
    [
        ("table-order-0001.xml", "1\n2\n3\n4\n5\n6\n7\n8\n9"),
        ("table-order-0002.xml", "1\n4\n7\n2\n5\n8\n3\n6\n9"),
        ("table-no-reading-order.xml", "5\n6\n7\n8\n9\n1\n2\n3\n4"),
        ("table-unordered.xml", "5\n6\n7\n8\n9\n1\n2\n3\n4"),
    ],
)
@pytest.mark.integration
def test_reading_order_settings(file, expected_text):
    if "table-unordered.xml" == file:
        with pytest.raises(NotImplementedError):
            page_text(ET.parse(os.path.join(data_dir, file)))
    else:
        ocr = page_text(ET.parse(os.path.join(data_dir, file)))
        assert ocr == expected_text


@pytest.mark.integration
@pytest.mark.parametrize(
    "gt,ocr,expected",
    [
        (
            "brochrnx_73075507X/00000139.gt.page.xml",
            "brochrnx_73075507X/00000139.ocrd-tess.ocr.page.xml",
            0.93,
        ),
        (
            "actevedef_718448162/OCR-D-GT-PAGE/00000024.page.xml",
            "actevedef_718448162/OCR-D-OCR-TESS/OCR-D-OCR-TESS_0001.xml",
            0.96,
        ),
        (
            "actevedef_718448162/OCR-D-GT-PAGE/00000024.page.xml",
            "actevedef_718448162/OCR-D-OCR-CALAMARI/OCR-D-OCR-CALAMARI_0001.xml",
            0.97,
        ),
        (
            "lorem-ipsum/lorem-ipsum-scan.gt.page.xml",
            "lorem-ipsum/lorem-ipsum-scan.ocr.tesseract.alto.xml",
            1.0,
        ),
        (
            "lorem-ipsum/lorem-ipsum-scan-bad.gt.page.xml",
            "lorem-ipsum/lorem-ipsum-scan-bad.ocr.tesseract.alto.xml",
            0.98,
        ),
    ],
)
def test_ocr_files(gt, ocr, expected):
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    gt_et = extract(os.path.join(data_dir, gt))
    ocr_et = extract(os.path.join(data_dir, ocr))
    score, _ = flexible_character_accuracy(gt_et, ocr_et)
    assert score == pytest.approx(expected, abs=0.01)
