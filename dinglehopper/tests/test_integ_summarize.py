import json
import os
import pytest
from .util import working_directory
from .. import cli_summarize

expected_cer_avg = (0.05 + 0.10) / 2
expected_wer_avg = (0.15 + 0.20) / 2
expected_diff_c = {"a": 30, "b": 50}
expected_diff_w = {"c": 70, "d": 90}


@pytest.fixture
def create_summaries(tmp_path):
    """Create two summary reports with mock data"""
    reports_dirname = tmp_path / "reports"
    reports_dirname.mkdir()

    report1 = {"cer": 0.05, "wer": 0.15,
               "differences": {
                   "character_level": {"a": 10, "b": 20},
                   "word_level": {"c": 30, "d": 40}
               }}
    report2 = {"cer": 0.10, "wer": 0.20,
               "differences": {
                   "character_level": {"a": 20, "b": 30},
                   "word_level": {"c": 40, "d": 50}
               }}

    with open(os.path.join(reports_dirname, "report1.json"), "w") as f:
        json.dump(report1, f)
    with open(os.path.join(reports_dirname, "report2.json"), "w") as f:
        json.dump(report2, f)

    return str(reports_dirname)


@pytest.mark.integration
def test_cli_summarize_json(tmp_path, create_summaries):
    """Test that the cli/process() yields a summarized JSON report"""
    with working_directory(tmp_path):
        reports_dirname = create_summaries
        cli_summarize.process(reports_dirname)

        with open(os.path.join(reports_dirname, "summary.json"), "r") as f:
            summary_data = json.load(f)


        assert summary_data["num_reports"] == 2
        assert summary_data["cer_avg"] == expected_cer_avg
        assert summary_data["wer_avg"] == expected_wer_avg
        assert summary_data["differences"]["character_level"] == expected_diff_c
        assert summary_data["differences"]["word_level"] == expected_diff_w


@pytest.mark.integration
def test_cli_summarize_html(tmp_path, create_summaries):
    """Test that the cli/process() yields an HTML report"""
    with working_directory(tmp_path):
        reports_dirname = create_summaries
        cli_summarize.process(reports_dirname)

        html_file = os.path.join(reports_dirname, "summary.html")
        assert os.path.isfile(html_file)

        with open(html_file, "r") as f:
            contents = f.read()

            assert len(contents) > 0
            assert "Number of reports: 2" in contents
            assert f"Average CER: {round(expected_cer_avg, 4)}" in contents
            assert f"Average WER: {round(expected_wer_avg, 4)}" in contents


@pytest.mark.integration
def test_cli_summarize_html_skip_invalid(tmp_path, create_summaries):
    """
    Test that the cli/process() does not include reports that are missing a WER value.
    """
    with working_directory(tmp_path):
        reports_dirname = create_summaries

        # This third report has no WER value and should not be included in the summary
        report3 = {"cer": 0.10,
                   "differences": {
                       "character_level": {"a": 20, "b": 30},
                       "word_level": {"c": 40, "d": 50}
                   }}

        with open(os.path.join(reports_dirname, "report3-missing-wer.json"), "w") as f:
            json.dump(report3, f)

        cli_summarize.process(reports_dirname)

        html_file = os.path.join(reports_dirname, "summary.html")
        assert os.path.isfile(html_file)

        with open(html_file, "r") as f:
            contents = f.read()

            assert "Number of reports: 2" in contents  # report3 is not included
