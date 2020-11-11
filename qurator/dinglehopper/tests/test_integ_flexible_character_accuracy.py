import os

import pytest
from lxml import etree as ET

from .. import distance, page_text
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
