import json
import os
from collections import Counter
from functools import partial
from typing import Any, Callable, Dict, List, Tuple

import click
from jinja2 import Environment, FileSystemLoader
from markupsafe import escape
from ocrd_utils import initLogging

from .align import seq_align
from .config import Config
from .extracted_text import ExtractedText
from .metrics import (
    bag_of_chars_accuracy,
    bag_of_words_accuracy,
    character_accuracy,
    word_accuracy,
)
from .normalize import chars_normalized, words_normalized
from .ocr_files import extract


def gen_count_report(
    gt_text: ExtractedText, ocr_text: ExtractedText, split_fun: Callable[[str], Counter]
) -> List[Tuple[str, int, int]]:
    gt_counter = Counter(split_fun(gt_text.text))
    ocr_counter = Counter(split_fun(ocr_text.text))
    return [
        ("".join(key), gt_counter[key], ocr_counter[key])
        for key in sorted({*gt_counter.keys(), *ocr_counter.keys()})
    ]


def gen_diff_report(
    gt_in: ExtractedText,
    ocr_in: ExtractedText,
    css_prefix: str = "c",
    joiner: str = "",
    none: str = "·",
    split_fun=chars_normalized,
) -> Tuple[str, str]:
    gtx = ""
    ocrx = ""

    def format_thing(t, css_classes=None, id_=None):
        if t is None:
            html_t = none
            css_classes += " ellipsis"
        elif t == "\n":
            html_t = "<br>"
        else:
            html_t = escape(t)

        html_custom_attrs = ""

        # Set Bootstrap tooltip to the segment id
        if id_:
            html_custom_attrs += 'data-toggle="tooltip" title="{}"'.format(id_)

        if css_classes:
            return f'<span class="{css_classes}" {html_custom_attrs}>{html_t}</span>'
        else:
            return f"{html_t}"

    gt_things = split_fun(gt_in.text)
    ocr_things = split_fun(ocr_in.text)

    g_pos = 0
    o_pos = 0
    for k, (g, o) in enumerate(seq_align(gt_things, ocr_things)):
        css_classes = None
        gt_id = None
        ocr_id = None
        if g != o:
            css_classes = "{css_prefix}diff{k} diff".format(css_prefix=css_prefix, k=k)
            gt_id = gt_in.segment_id_for_pos(g_pos) if g is not None else None
            ocr_id = ocr_in.segment_id_for_pos(o_pos) if o is not None else None
            # Deletions and inserts only produce one id + None, UI must
            # support this, i.e. display for the one id produced

        gtx += joiner + format_thing(g, css_classes, gt_id)
        ocrx += joiner + format_thing(o, css_classes, ocr_id)

        if g is not None:
            g_pos += len(g)
        if o is not None:
            o_pos += len(o)

    return gtx, ocrx


def generate_html_report(
    gt: str,
    ocr: str,
    gt_text: ExtractedText,
    ocr_text: ExtractedText,
    report_prefix: str,
    metrics_results: Dict,
):

    metric_dict: Dict[str, Callable] = {
        "character_accuracy": partial(
            gen_diff_report,
            css_prefix="c",
            joiner="",
            none="·",
            split_fun=chars_normalized,
        ),
        "word_accuracy": partial(
            gen_diff_report,
            css_prefix="w",
            joiner=" ",
            none="⋯",
            split_fun=words_normalized,
        ),
        "bag_of_chars_accuracy": partial(gen_count_report, split_fun=chars_normalized),
        "bag_of_words_accuracy": partial(gen_count_report, split_fun=words_normalized),
    }
    metrics_reports = {}
    for metric in metrics_results.keys():
        if metric not in metric_dict.keys():
            raise ValueError(f"Unknown metric '{metric}'.")
        metrics_reports[metric] = metric_dict[metric](gt_text, ocr_text)

    env = Environment(
        loader=FileSystemLoader(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "templates")
        )
    )

    report_suffix = ".html"
    template_fn = "report" + report_suffix + ".j2"
    out_fn = report_prefix + report_suffix

    template = env.get_template(template_fn)
    template.stream(
        gt=gt,
        ocr=ocr,
        metrics_reports=metrics_reports,
        metrics_results=metrics_results,
    ).dump(out_fn)


def generate_json_report(gt: str, ocr: str, report_prefix: str, metrics_results: Dict):
    json_dict: Dict[str, Any] = {"gt": gt, "ocr": ocr}
    for result in metrics_results.values():
        json_dict[result.metric] = {
            key: value for key, value in result.get_dict().items() if key != "metric"
        }
    with open(f"{report_prefix}.json", "w") as fp:
        json.dump(json_dict, fp)


def process(
    gt, ocr, report_prefix, *, html=True, metrics="cer,wer", textequiv_level="region"
):
    """Check OCR result against GT.

    The @click decorators change the signature of the decorated functions,
    so we keep this undecorated version and use Click on a wrapper.
    """

    gt_text = extract(gt, textequiv_level=textequiv_level)
    ocr_text = extract(ocr, textequiv_level=textequiv_level)

    metrics_results = {}
    if metrics:
        metric_dict = {
            "ca": character_accuracy,
            "cer": character_accuracy,
            "wa": word_accuracy,
            "wer": word_accuracy,
            "boc": bag_of_chars_accuracy,
            "bow": bag_of_words_accuracy,
        }
        for metric in metrics.split(","):
            metric = metric.strip()
            if metric not in metric_dict.keys():
                raise ValueError(f"Unknown metric '{metric}'.")
            result = metric_dict[metric](gt_text.text, ocr_text.text)
            metrics_results[result.metric] = result

    generate_json_report(gt, ocr, report_prefix, metrics_results)
    if html:
        generate_html_report(gt, ocr, gt_text, ocr_text, report_prefix, metrics_results)


@click.command()
@click.argument("gt", type=click.Path(exists=True))
@click.argument("ocr", type=click.Path(exists=True))
@click.argument("report_prefix", type=click.Path(), default="report")
@click.option("--html", default=True, is_flag=True, help="Enable/disable html report.")
@click.option(
    "--metrics",
    default="cer,wer",
    help="Enable different metrics like cer, wer, boc and bow.",
)
@click.option(
    "--textequiv-level",
    default="region",
    help="PAGE TextEquiv level to extract text from",
    metavar="LEVEL",
)
@click.option("--progress", default=False, is_flag=True, help="Show progress bar")
def main(gt, ocr, report_prefix, html, metrics, textequiv_level, progress):
    """
    Compare the PAGE/ALTO/text document GT against the document OCR.

    dinglehopper detects if GT/OCR are ALTO or PAGE XML documents to extract
    their text and falls back to plain text if no ALTO or PAGE is detected.

    The files GT and OCR are usually a ground truth document and the result of
    an OCR software, but you may use dinglehopper to compare two OCR results. In
    that case, use --metrics='' to disable the then meaningless metrics and also
    change the color scheme from green/red to blue.

    The comparison report will be written to $REPORT_PREFIX.{html,json}, where
    $REPORT_PREFIX defaults to "report". Depending on your configuration the
    reports include the character error rate (CA|CER), the word error rate (WA|WER),
    the bag of chars accuracy (BoC), and the bag of words accuracy (BoW).
    The metrics can be chosen via a comma separated combination of their acronyms
    like "--metrics=ca,wer,boc,bow".

    The html report can be enabled/disabled using --html / --no-html.

    By default, the text of PAGE files is extracted on 'region' level. You may
    use "--textequiv-level line" to extract from the level of TextLine tags.
    """
    initLogging()
    Config.progress = progress
    process(
        gt,
        ocr,
        report_prefix,
        html=html,
        metrics=metrics,
        textequiv_level=textequiv_level,
    )


if __name__ == "__main__":
    main()
