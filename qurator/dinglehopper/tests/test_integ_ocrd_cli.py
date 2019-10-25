import os
import re

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


def test_ocrd_cli():
    test_workspace_dir = os.path.join(data_dir, 'actevedef_718448162')
    with working_directory(test_workspace_dir):
        runner = CliRunner()
        result = runner.invoke(ocrd_dinglehopper, [
            '-m', 'mets.xml',
            '-I', 'OCR-D-GT-PAGE,OCR-D-OCR-CALAMARI',
            '-O', 'OCR-D-OCR-CALAMARI-EVAL'
        ])
    assert result.exit_code == 0
    # XXX Check for useful output, too
