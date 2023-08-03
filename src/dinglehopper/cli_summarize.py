import json
import os

import click
from ocrd_utils import initLogging
from jinja2 import Environment, FileSystemLoader

from dinglehopper.cli import json_float


def process(reports_folder, occurrences_threshold=1):
    cer_list = []
    wer_list = []
    cer_sum = 0
    wer_sum = 0
    diff_c = {}
    diff_w = {}

    for report in os.listdir(reports_folder):
        if report.endswith(".json"):
            with open(os.path.join(reports_folder, report), "r") as f:
                report_data = json.load(f)

                if "cer" not in report_data or "wer" not in report_data:
                    click.echo(
                        f"Skipping {report} because it does not contain CER and WER")
                    continue

                cer = report_data["cer"]
                wer = report_data["wer"]
                cer_list.append(cer)
                wer_list.append(wer)
                cer_sum += cer
                wer_sum += wer

                for key, value in report_data["differences"]["character_level"].items():
                    diff_c[key] = diff_c.get(key, 0) + value
                for key, value in report_data["differences"]["word_level"].items():
                    diff_w[key] = diff_w.get(key, 0) + value

    if len(cer_list) == 0:
        click.echo(f"No reports found in folder '{os.path.abspath(reports_folder)}'")
        return

    cer_avg = cer_sum / len(cer_list)
    wer_avg = wer_sum / len(wer_list)

    print(f"Number of reports: {len(cer_list)}")
    print(f"Average CER: {cer_avg}")
    print(f"Average WER: {wer_avg}")
    print(f"Sum of common mistakes: {cer_sum}")
    print(f"Sum of common mistakes: {wer_sum}")

    env = Environment(
        loader=FileSystemLoader(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "templates")
        )
    )
    env.filters["json_float"] = json_float
    for report_suffix in (".html", ".json"):
        template_fn = "summary" + report_suffix + ".j2"

        out_fn = os.path.join(reports_folder, 'summary' + report_suffix)
        template = env.get_template(template_fn)
        template.stream(
            num_reports=len(cer_list),
            cer_avg=cer_avg,
            wer_avg=wer_avg,
            diff_c=diff_c,
            diff_w=diff_w,
            occurrences_threshold=occurrences_threshold,
        ).dump(out_fn)


@click.command()
@click.argument("reports_folder",
                type=click.Path(exists=True),
                default="./reports"
                )
@click.option("--occurrences-threshold",
              type=int,
              default=1,
              help="Only show differences that occur at least this many times.")
def main(reports_folder, occurrences_threshold):
    """
    Summarize the results from multiple reports generated earlier by dinglehopper.
    It calculates the average CER and WER, as well as a sum of common mistakes.
    Reports include lists of mistakes and their occurrences.

    You may use a threshold to reduce the file size of the HTML report by only showing
    mistakes whose number of occurrences is above the threshold. The JSON report will
    always contain all mistakes.

    All JSON files in the provided folder will be gathered and summarized.
    """
    initLogging()
    process(reports_folder, occurrences_threshold)


if __name__ == "__main__":
    main()
