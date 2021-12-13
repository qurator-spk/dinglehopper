import os
import sys
import itertools

import click
from jinja2 import Environment, FileSystemLoader
from markupsafe import escape
from uniseg.graphemecluster import grapheme_clusters
from ocrd_utils import initLogging

from .character_error_rate import character_error_rate_n
from .word_error_rate import word_error_rate_n, words_normalized
from .align import seq_align
from .extracted_text import ExtractedText
from .ocr_files import plain_extract
from .config import Config
from .cli import gen_diff_report


def all_equal(iterable):
    g = itertools.groupby(iterable)
    return next(g, True) and not next(g, False)


def common_prefix(its):
    return [p[0] for p in itertools.takewhile(all_equal, zip(*its))]


def common_suffix(its):
    return reversed(common_prefix(reversed(it) for it in its))


def removesuffix(text, suffix):
    if suffix and text.endswith(suffix):
        return text[:-len(suffix)]
    return text


def process(gt_dir, ocr_dir, report_prefix, *, metrics=True):
    gt_suffix = "".join(common_suffix(os.listdir(gt_dir)))
    ocr_suffix = "".join(common_suffix(os.listdir(ocr_dir)))

    cer = None
    n_characters = None
    char_diff_report = ""

    for gt in os.listdir(gt_dir):
        # Find a match by replacing the suffix
        ocr = removesuffix(gt, gt_suffix) + ocr_suffix

        gt_text = plain_extract(os.path.join(gt_dir, gt))
        ocr_text = plain_extract(os.path.join(ocr_dir, ocr))

        # Compute CER
        l_cer, l_n_characters = character_error_rate_n(gt_text, ocr_text)
        if cer is None:
            cer, n_characters = l_cer, l_n_characters
        else:
            # Rolling update
            cer = (cer * n_characters + l_cer * l_n_characters) / (n_characters + l_n_characters)
            n_characters = n_characters + l_n_characters

        # Compute WER
        # TODO wer, n_words = word_error_rate_n(gt_text, ocr_text)
        wer = 9999; n_words = 0

        char_diff_report += gen_diff_report(
             gt_text, ocr_text, css_prefix="c", joiner="", none="·"
        )

        # TODO
        #  gt_words = words_normalized(gt_text)
        #  ocr_words = words_normalized(ocr_text)
        #  word_diff_report = gen_diff_report(
        #      gt_words, ocr_words, css_prefix="w", joiner=" ", none="⋯"
        #  )
        word_diff_report = "TODO"


    # XXX this is a copy from cli.py
    def json_float(value):
        """Convert a float value to an JSON float.

        This is here so that float('inf') yields "Infinity", not "inf".
        """
        if value == float("inf"):
            return "Infinity"
        elif value == float("-inf"):
            return "-Infinity"
        else:
            return str(value)

    env = Environment(
        loader=FileSystemLoader(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "templates")
        )
    )
    env.filters["json_float"] = json_float

    for report_suffix in (".html", ".json"):
        template_fn = "report" + report_suffix + ".j2"
        out_fn = report_prefix + report_suffix

        template = env.get_template(template_fn)
        template.stream(
            gt=gt,
            ocr=ocr,
            cer=cer,
            n_characters=n_characters,
            wer=wer,
            n_words=n_words,
            char_diff_report=char_diff_report,
            word_diff_report=word_diff_report,
            metrics=metrics,
        ).dump(out_fn)


@click.command()
@click.argument("gt", type=click.Path(exists=True))
@click.argument("ocr", type=click.Path(exists=True))
@click.argument("report_prefix", type=click.Path(), default="report")
@click.option(
    "--metrics/--no-metrics", default=True, help="Enable/disable metrics and green/red"
)
def main(gt, ocr, report_prefix, metrics):
    """
    Compare the GT line text directory against the OCR line text directory.

    This assumes that the GT line text directory contains textfiles with a common
    suffix like ".gt.txt", and the OCR line text directory contains textfiles with
    a common suffix like ".some-ocr.txt". The text files also need to be paired,
    i.e. the GT file "line001.gt.txt" needs to match a file "line001.some-ocr.txt"
    in the OCT lines directory.

    The GT and OCR directories are usually round truth line texts and the results of
    an OCR software, but you may use dinglehopper to compare two OCR results. In
    that case, use --no-metrics to disable the then meaningless metrics and also
    change the color scheme from green/red to blue.

    The comparison report will be written to $REPORT_PREFIX.{html,json}, where
    $REPORT_PREFIX defaults to "report". The reports include the character error
    rate (CER) and the word error rate (WER).

    """
    initLogging()
    process(gt, ocr, report_prefix, metrics=metrics)


if __name__ == "__main__":
    main()
