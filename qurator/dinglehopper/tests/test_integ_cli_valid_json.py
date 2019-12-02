import os
import json

import pytest

from ..cli import process


class working_directory:
    """Context manager to temporarily change the working directory"""
    def __init__(self, wd):
        self.wd = wd

    def __enter__(self):
        self.old_wd = os.getcwd()
        os.chdir(self.wd)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.old_wd)


def test_cli_json(tmp_path):
    """Test that the cli/process() yields a loadable JSON report"""

    # XXX Path.__str__() is necessary for Python 3.5
    with working_directory(str(tmp_path)):
        with open('gt.txt', 'w') as gtf:
            gtf.write('AAAAA')
        with open('ocr.txt', 'w') as ocrf:
            ocrf.write('AAAAB')

        process('gt.txt', 'ocr.txt', 'report')
        with open('report.json', 'r') as jsonf:
            j = json.load(jsonf)
            assert j['cer'] == pytest.approx(0.2)


def test_cli_json_cer_is_infinity(tmp_path):
    """Test that the cli/process() yields a loadable JSON report when CER == inf"""

    # XXX Path.__str__() is necessary for Python 3.5
    with working_directory(str(tmp_path)):
        with open('gt.txt', 'w') as gtf:
            gtf.write('')  # Empty to yield CER == inf
        with open('ocr.txt', 'w') as ocrf:
            ocrf.write('Not important')

        process('gt.txt', 'ocr.txt', 'report')
        with open('report.json', 'r') as jsonf:
            j = json.load(jsonf)
            assert j['cer'] == pytest.approx(float('inf'))
