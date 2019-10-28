import os
import re
import shutil
import json
from pathlib import Path

from click.testing import CliRunner
import pytest


from ..ocrd_cli import ocrd_dinglehopper

data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


class working_directory:
    """Context manager to temporarily change the working directory"""
    def __init__(self, wd):
        self.wd = wd

    def __enter__(self):
        self.old_wd = os.getcwd()
        os.chdir(self.wd)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.wd)


def test_ocrd_cli(tmp_path):
    """Test OCR-D interface"""

    # Copy test workspace
    test_workspace_dir_source = Path(data_dir) / 'actevedef_718448162'
    test_workspace_dir = tmp_path / 'test_ocrd_cli'
    shutil.copytree(str(test_workspace_dir_source), str(test_workspace_dir)) # str() is necessary for Python 3.5's shutil.copytree()

    # Run through the OCR-D interface
    with working_directory(test_workspace_dir):
        runner = CliRunner()
        result = runner.invoke(ocrd_dinglehopper, [
            '-m', 'mets.xml',
            '-I', 'OCR-D-GT-PAGE,OCR-D-OCR-CALAMARI',
            '-O', 'OCR-D-OCR-CALAMARI-EVAL'
        ])
    assert result.exit_code == 0
    result_json = list((Path(test_workspace_dir) / 'OCR-D-OCR-CALAMARI-EVAL').glob('*.json'))
    assert json.load(open(result_json[0]))['cer'] < 0.03
