from pathlib import Path

import pytest

from .util import working_directory
from ..cli import process


@pytest.mark.integration
def test_cli_unknown_metric(tmp_path):
    """Test that unknown metrics are handled appropriately."""

    with working_directory(str(tmp_path)):
        with open("gt.txt", "w") as gtf:
            gtf.write("")
        with open("ocr.txt", "w") as ocrf:
            ocrf.write("")

        with pytest.raises(ValueError, match="Unknown metric 'unknown'."):
            process("gt.txt", "ocr.txt", "report", metrics="cer,unknown")


@pytest.mark.integration
def test_cli_html_report_parameter(tmp_path):
    """Test that html report can get turned off."""

    with working_directory(str(tmp_path)):
        with open("gt.txt", "w") as gtf:
            gtf.write("")
        with open("ocr.txt", "w") as ocrf:
            ocrf.write("")

        process("gt.txt", "ocr.txt", "report", html=False)

        assert Path("report").with_suffix(".json").exists()
        assert not Path("report").with_suffix(".html").exists()
