import os
import pytest
from ocrd_utils import initLogging
from dinglehopper.cli import process_dir

data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


@pytest.mark.integration
def test_cli_directory(tmp_path):
    """
    Test that the cli/process_dir() processes a directory of files and
    yields JSON and HTML reports.
    """

    initLogging()
    process_dir(os.path.join(data_dir, "directory-test", "gt"),
                os.path.join(data_dir, "directory-test", "ocr"),
                "report", str(tmp_path / "reports"), False, True,
                "line")

    assert os.path.exists(tmp_path / "reports/1.xml-report.json")
    assert os.path.exists(tmp_path / "reports/1.xml-report.html")
    assert os.path.exists(tmp_path / "reports/2.xml-report.json")
    assert os.path.exists(tmp_path / "reports/2.xml-report.html")


@pytest.mark.integration
def test_cli_fail_without_gt(tmp_path):
    """
    Test that the cli/process_dir skips a file if there is no corresponding file
    in the other directory.
    """

    initLogging()
    process_dir(os.path.join(data_dir, "directory-test", "gt"),
                os.path.join(data_dir, "directory-test", "ocr"),
                "report", str(tmp_path / "reports"), False, True,
                "line")

    assert len(os.listdir(tmp_path / "reports")) == 2 * 2
