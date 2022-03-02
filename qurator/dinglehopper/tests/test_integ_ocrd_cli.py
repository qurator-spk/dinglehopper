import os
import shutil
import json
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner
from .util import working_directory


from ..ocrd_cli import ocrd_dinglehopper

data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


@pytest.mark.integration
@pytest.mark.skipif(sys.platform == 'win32', reason="only on unix")
def test_ocrd_cli(tmp_path):
    """Test OCR-D interface"""

    # Copy test workspace
    test_workspace_dir_source = Path(data_dir) / "actevedef_718448162"
    test_workspace_dir = tmp_path / "test_ocrd_cli"
    shutil.copytree(test_workspace_dir_source, test_workspace_dir)

    # Run through the OCR-D interface
    with working_directory(test_workspace_dir):
        runner = CliRunner()
        args = [
            "-m",
            "mets.xml",
            "-I",
            "OCR-D-GT-PAGE,OCR-D-OCR-CALAMARI",
            "-O",
            "OCR-D-OCR-CALAMARI-EVAL",
        ]
        sys.argv[
            1:
        ] = args  # XXX Hack to satisfy ocrd_cli_wrap_processor() check for arguments
        result = runner.invoke(ocrd_dinglehopper, args)
    assert result.exit_code == 0
    result_json = list((test_workspace_dir / "OCR-D-OCR-CALAMARI-EVAL").glob("*.json"))
    assert json.load(open(str(result_json[0])))["cer"] < 0.03
