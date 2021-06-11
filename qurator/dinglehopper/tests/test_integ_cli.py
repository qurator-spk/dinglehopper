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
