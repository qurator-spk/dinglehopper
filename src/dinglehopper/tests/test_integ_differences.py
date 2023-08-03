import json
import os
import pytest
from ocrd_utils import initLogging
from dinglehopper.cli import process

data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


@pytest.mark.integration
def test_cli_differences(tmp_path):
    """Test that the cli/process() yields a JSON report that includes
        the differences found between the GT and OCR text"""

    initLogging()
    process(os.path.join(data_dir, "test-gt.page2018.xml"),
            os.path.join(data_dir, "test-fake-ocr.page2018.xml"),
            "report", tmp_path, differences=True)

    assert os.path.exists(tmp_path / "report.json")

    with open(tmp_path / "report.json", "r") as jsonf:
        j = json.load(jsonf)

        assert j["differences"] == {"character_level": {'n :: m': 1, 'ſ :: f': 1},
                                    "word_level": {'Augenblick :: Augemblick': 1,
                                                   'Verſprochene :: Verfprochene': 1}}
