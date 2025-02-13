import os
from collections import Counter
from typing import List

import click
from jinja2 import Environment, FileSystemLoader
from markupsafe import escape
from ocrd_utils import initLogging

from dinglehopper.align import score_hint, seq_align
from dinglehopper.character_error_rate import character_error_rate_n
from dinglehopper.config import Config
from dinglehopper.extracted_text import ExtractedText
from dinglehopper.ocr_files import extract
from dinglehopper.word_error_rate import word_error_rate_n, words_normalized


def gen_diff_report(
    gt_in, ocr_in, css_prefix, joiner, none, *, differences=False, score_hint=None
):
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
            html_custom_attrs += f'data-toggle="tooltip" title="{id_}"'

        if css_classes:
            return f'<span class="{css_classes}" {html_custom_attrs}>{html_t}</span>'
        else:
            return f"{html_t}"

    if isinstance(gt_in, ExtractedText):
        if not isinstance(ocr_in, ExtractedText):
            raise TypeError()
        gt_things = gt_in.grapheme_clusters
        ocr_things = ocr_in.grapheme_clusters
    else:
        gt_things = gt_in
        ocr_things = ocr_in

    g_pos = 0
    o_pos = 0
    found_differences = []

    for k, (g, o) in enumerate(seq_align(gt_things, ocr_things, score_hint)):
        css_classes = None
        gt_id = None
        ocr_id = None
        if g != o:
            css_classes = "{css_prefix}diff{k} diff".format(css_prefix=css_prefix, k=k)
            if isinstance(gt_in, ExtractedText):
                gt_id = gt_in.segment_id_for_pos(g_pos) if g is not None else None
                ocr_id = ocr_in.segment_id_for_pos(o_pos) if o is not None else None
                # Deletions and inserts only produce one id + None, UI must
                # support this, i.e. display for the one id produced

            if differences:
                found_differences.append(f"{g} :: {o}")

        gtx += joiner + format_thing(g, css_classes, gt_id)
        ocrx += joiner + format_thing(o, css_classes, ocr_id)

        if g is not None:
            g_pos += len(g)
        if o is not None:
            o_pos += len(o)

    counted_differences = dict(Counter(elem for elem in found_differences))

    return (
        """
        <div class="row">
           <div class="col-md-6 gt">{}</div>
           <div class="col-md-6 ocr">{}</div>
        </div>
        """.format(
            gtx, ocrx
        ),
        counted_differences,
    )


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


def process(
    gt: str,
    ocr: str,
    report_prefix: str,
    reports_folder: str = ".",
    *,
    metrics: bool = True,
    differences: bool = False,
    textequiv_level: str = "region",
    plain_encoding: str = "autodetect",
) -> None:
    """Check OCR result against GT.

    The @click decorators change the signature of the decorated functions, so we keep
    this undecorated version and use Click on a wrapper.
    """

    gt_text = extract(
        gt, textequiv_level=textequiv_level, plain_encoding=plain_encoding
    )
    ocr_text = extract(
        ocr, textequiv_level=textequiv_level, plain_encoding=plain_encoding
    )
    gt_words: List[str] = list(words_normalized(gt_text))
    ocr_words: List[str] = list(words_normalized(ocr_text))

    assert isinstance(gt_text, ExtractedText)
    assert isinstance(ocr_text, ExtractedText)
    cer, n_characters = character_error_rate_n(gt_text, ocr_text)
    char_diff_report, diff_c = gen_diff_report(
        gt_text,
        ocr_text,
        css_prefix="c",
        joiner="",
        none="·",
        score_hint=score_hint(cer, n_characters),
        differences=differences,
    )

    # {gt,ocr}_words must not be a generator, so we don't drain it for the differences
    # report.
    assert isinstance(gt_words, list)
    assert isinstance(ocr_words, list)
    wer, n_words = word_error_rate_n(gt_words, ocr_words)
    word_diff_report, diff_w = gen_diff_report(
        gt_words,
        ocr_words,
        css_prefix="w",
        joiner=" ",
        none="⋯",
        score_hint=score_hint(wer, n_words),
        differences=differences,
    )

    env = Environment(
        loader=FileSystemLoader(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "templates")
        )
    )
    env.filters["json_float"] = json_float

    for report_suffix in (".html", ".json"):
        template_fn = "report" + report_suffix + ".j2"

        if not os.path.isdir(reports_folder):
            os.mkdir(reports_folder)

        out_fn = os.path.join(reports_folder, report_prefix + report_suffix)

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
            differences=differences,
            diff_c=diff_c,
            diff_w=diff_w,
        ).dump(out_fn)


def process_dir(
    gt: str,
    ocr: str,
    report_prefix: str,
    reports_folder: str = ".",
    *,
    metrics: bool = True,
    differences: bool = False,
    textequiv_level: str = "region",
    plain_encoding: str = "autodetect",
) -> None:
    for gt_file in os.listdir(gt):
        gt_file_path = os.path.join(gt, gt_file)
        ocr_file_path = os.path.join(ocr, gt_file)

        if os.path.isfile(gt_file_path) and os.path.isfile(ocr_file_path):
            process(
                gt_file_path,
                ocr_file_path,
                f"{gt_file}-{report_prefix}",
                reports_folder=reports_folder,
                metrics=metrics,
                differences=differences,
                textequiv_level=textequiv_level,
                plain_encoding=plain_encoding,
            )
        else:
            print("Skipping {0} and {1}".format(gt_file_path, ocr_file_path))


@click.command()
@click.argument("gt", type=click.Path(exists=True))
@click.argument("ocr", type=click.Path(exists=True))
@click.argument("report_prefix", type=click.Path(), default="report")
@click.argument("reports_folder", type=click.Path(), default=".")
@click.option(
    "--metrics/--no-metrics", default=True, help="Enable/disable metrics and green/red"
)
@click.option(
    "--differences",
    default=False,
    help="Enable reporting character and word level differences",
)
@click.option(
    "--textequiv-level",
    default="region",
    help="PAGE TextEquiv level to extract text from",
    metavar="LEVEL",
)
@click.option(
    "--plain-encoding",
    default="autodetect",
    help='Encoding  (e.g. "utf-8") of plain text files',
)
@click.option("--progress", default=False, is_flag=True, help="Show progress bar")
@click.version_option()
def main(
    gt,
    ocr,
    report_prefix,
    reports_folder,
    metrics,
    differences,
    textequiv_level,
    plain_encoding,
    progress,
):
    """
    Compare the PAGE/ALTO/text document GT against the document OCR.

    dinglehopper detects if GT/OCR are ALTO or PAGE XML documents to extract
    their text and falls back to plain text if no ALTO or PAGE is detected.

    The files GT and OCR are usually a ground truth document and the result of
    an OCR software, but you may use dinglehopper to compare two OCR results. In
    that case, use --no-metrics to disable the then meaningless metrics and also
    change the color scheme from green/red to blue.

    The comparison report will be written to $REPORTS_FOLDER/$REPORT_PREFIX.{html,json},
    where $REPORTS_FOLDER defaults to the current working directory and
    $REPORT_PREFIX defaults to "report". The reports include the character error
    rate (CER) and the word error rate (WER).

    By default, the text of PAGE files is extracted on 'region' level. You may
    use "--textequiv-level line" to extract from the level of TextLine tags.
    """
    initLogging()
    Config.progress = progress
    if os.path.isdir(gt):
        if not os.path.isdir(ocr):
            raise click.BadParameter(
                "OCR must be a directory if GT is a directory", param_hint="ocr"
            )
        else:
            process_dir(
                gt,
                ocr,
                report_prefix,
                reports_folder,
                metrics=metrics,
                differences=differences,
                textequiv_level=textequiv_level,
                plain_encoding=plain_encoding,
            )
    else:
        process(
            gt,
            ocr,
            report_prefix,
            reports_folder,
            metrics=metrics,
            differences=differences,
            textequiv_level=textequiv_level,
            plain_encoding=plain_encoding,
        )


if __name__ == "__main__":
    main()
