from __future__ import division, print_function

import os

import pytest
from lxml import etree as ET

from .. import alto_text, character_error_rate, page_text

data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


@pytest.mark.integration
def test_bigger_texts():
    gt = page_text(
        ET.parse(os.path.join(data_dir, "bigger-texts", "00008228", "00008228.gt.xml"))
    )
    ocr = alto_text(
        ET.parse(
            os.path.join(
                data_dir, "bigger-texts", "00008228", "00008228-00236534.gt4hist.xml"
            )
        )
    )

    # Only interested in a result here: In earlier versions this would have used
    # tens of GB of RAM and should now not break a sweat.
    assert character_error_rate(gt, ocr) >= 0.0
