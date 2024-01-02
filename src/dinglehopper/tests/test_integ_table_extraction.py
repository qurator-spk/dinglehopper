import os

import pytest
from lxml import etree as ET

from .. import page_text


@pytest.mark.parametrize(
    "file,expected_text",
    [
        ("table-order-0001.xml", "1\n2\n3\n4\n5\n6\n7\n8\n9"),
        ("table-order-0002.xml", "1\n4\n7\n2\n5\n8\n3\n6\n9"),
        ("table-region.xml", "1\n2\n3\n4\n5\n6\n7\n8\n9"),
        ("table-no-reading-order.xml", "5\n6\n7\n8\n9\n1\n2\n3\n4"),
        ("table-unordered.xml", "1\n2\n3\n4\n5\n6\n7\n8\n9"),
    ],
)
@pytest.mark.integration
def test_reading_order_settings(file, expected_text):
    data_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "data", "table-order"
    )
    ocr = page_text(ET.parse(os.path.join(data_dir, file)))
    assert ocr == expected_text
