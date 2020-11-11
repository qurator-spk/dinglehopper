import os

import click
from jinja2 import Environment, FileSystemLoader
from markupsafe import escape
from uniseg.graphemecluster import grapheme_clusters

from .character_error_rate import character_error_rate_n
from .flexible_character_accuracy import flexible_character_accuracy, split_matches
from .word_error_rate import word_error_rate_n, words_normalized
from .align import seq_align
from .extracted_text import ExtractedText
from .ocr_files import extract
from .config import Config


def gen_diff_report(gt_in, ocr_in, css_prefix, joiner, none, ops=None):
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
    for k, (g, o) in enumerate(seq_align(gt_things, ocr_things, ops=ops)):
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


def process(gt, ocr, report_prefix, *, metrics="cer,wer", textequiv_level="region"):
    """Check OCR result against GT.

    The @click decorators change the signature of the decorated functions,
    so we keep this undecorated version and use Click on a wrapper.
    """
    cer, char_diff_report, n_characters = None, None, None
    wer, word_diff_report, n_words = None, None, None
    fca, fca_diff_report = None, None

    gt_text = extract(gt, textequiv_level=textequiv_level)
    ocr_text = extract(ocr, textequiv_level=textequiv_level)

    if "cer" in metrics or not metrics:
        cer, n_characters = character_error_rate_n(gt_text, ocr_text)
        char_diff_report = gen_diff_report(
            gt_text, ocr_text, css_prefix="c", joiner="", none="·"
        )

    if "wer" in metrics:
        gt_words = words_normalized(gt_text)
        ocr_words = words_normalized(ocr_text)
        wer, n_words = word_error_rate_n(gt_text, ocr_text)
        word_diff_report = gen_diff_report(
            gt_words, ocr_words, css_prefix="w", joiner=" ", none="⋯"
        )
    if "fca" in metrics:
        fca, fca_matches = flexible_character_accuracy(gt_text.text, ocr_text.text)
        fca_gt_segments, fca_ocr_segments, ops = split_matches(fca_matches)
        fca_diff_report = gen_diff_report(
            fca_gt_segments,
            fca_ocr_segments,
            css_prefix="c",
            joiner="",
            none="·",
            ops=ops,
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
            fca=fca,
            char_diff_report=char_diff_report,
            word_diff_report=word_diff_report,
            fca_diff_report=fca_diff_report,
            metrics=metrics,
        ).dump(out_fn)


@click.command()
@click.argument("gt", type=click.Path(exists=True))
@click.argument("ocr", type=click.Path(exists=True))
@click.argument("report_prefix", type=click.Path(), default="report")
@click.option(
    "--metrics",
    default="cer,wer",
    help="Enable different metrics like cer, wer and fca.",
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
    that case, use --metrics='' to disable the then meaningless metrics and also
    change the color scheme from green/red to blue.

    The comparison report will be written to $REPORT_PREFIX.{html,json}, where
    $REPORT_PREFIX defaults to "report". Depending on your configuration the
    reports include the character error rate (CER), the word error rate (WER)
    and the flexible character accuracy (FCA).

    The metrics can be chosen via a comma separated combination of their acronyms
    like "--metrics=cer,wer,fca".

    By default, the text of PAGE files is extracted on 'region' level. You may
    use "--textequiv-level line" to extract from the level of TextLine tags.
    """
    Config.progress = progress
    process(gt, ocr, report_prefix, metrics=metrics, textequiv_level=textequiv_level)


if __name__ == "__main__":
    main()
