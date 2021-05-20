import os

import click
from jinja2 import Environment, FileSystemLoader
from markupsafe import escape
from uniseg.graphemecluster import grapheme_clusters
from ocrd_utils import initLogging

from .character_error_rate import character_error_rate_n
from .word_error_rate import word_error_rate_n, words_normalized
from .align import seq_align
from .extracted_text import ExtractedText
from .ocr_files import extract
from .config import Config


def gen_diff_report(gt_in, ocr_in, css_prefix, joiner, none):
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
            return '<span class="{css_classes}" {html_custom_attrs}>{html_t}</span>'.format(
                css_classes=css_classes,
                html_t=html_t,
                html_custom_attrs=html_custom_attrs,
            )
        else:
            return "{html_t}".format(html_t=html_t)

    if isinstance(gt_in, ExtractedText):
        if not isinstance(ocr_in, ExtractedText):
            raise TypeError()
        # XXX splitting should be done in ExtractedText
        gt_things = list(grapheme_clusters(gt_in.text))
        ocr_things = list(grapheme_clusters(ocr_in.text))
    else:
        gt_things = gt_in
        ocr_things = ocr_in

    g_pos = 0
    o_pos = 0
    for k, (g, o) in enumerate(seq_align(gt_things, ocr_things)):
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

        gtx += joiner + format_thing(g, css_classes, gt_id)
        ocrx += joiner + format_thing(o, css_classes, ocr_id)

        if g is not None:
            g_pos += len(g)
        if o is not None:
            o_pos += len(o)

    return """
        <div class="row">
           <div class="col-md-6 gt">{}</div>
           <div class="col-md-6 ocr">{}</div>
        </div>
        """.format(
        gtx, ocrx
    )


def process(gt, ocr, report_prefix, *, metrics=True, textequiv_level="region"):
    """Check OCR result against GT.

    The @click decorators change the signature of the decorated functions, so we keep this undecorated version and use
    Click on a wrapper.
    """

    gt_text = extract(gt, textequiv_level=textequiv_level)
    ocr_text = extract(ocr, textequiv_level=textequiv_level)

    cer, n_characters = character_error_rate_n(gt_text, ocr_text)
    wer, n_words = word_error_rate_n(gt_text, ocr_text)

    char_diff_report = gen_diff_report(
        gt_text, ocr_text, css_prefix="c", joiner="", none="·"
    )

    gt_words = words_normalized(gt_text)
    ocr_words = words_normalized(ocr_text)
    word_diff_report = gen_diff_report(
        gt_words, ocr_words, css_prefix="w", joiner=" ", none="⋯"
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
@click.option(
    "--textequiv-level",
    default="region",
    help="PAGE TextEquiv level to extract text from",
    metavar="LEVEL",
)
@click.option("--progress", default=False, is_flag=True, help="Show progress bar")
def main(gt, ocr, report_prefix, metrics, textequiv_level, progress):
    """
    Compare the PAGE/ALTO/text document GT against the document OCR.

    dinglehopper detects if GT/OCR are ALTO or PAGE XML documents to extract
    their text and falls back to plain text if no ALTO or PAGE is detected.

    The files GT and OCR are usually a ground truth document and the result of
    an OCR software, but you may use dinglehopper to compare two OCR results. In
    that case, use --no-metrics to disable the then meaningless metrics and also
    change the color scheme from green/red to blue.

    The comparison report will be written to $REPORT_PREFIX.{html,json}, where
    $REPORT_PREFIX defaults to "report". The reports include the character error
    rate (CER) and the word error rate (WER).

    By default, the text of PAGE files is extracted on 'region' level. You may
    use "--textequiv-level line" to extract from the level of TextLine tags.
    """
    initLogging()
    Config.progress = progress
    process(gt, ocr, report_prefix, metrics=metrics, textequiv_level=textequiv_level)


if __name__ == "__main__":
    main()
