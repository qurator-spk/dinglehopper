import os

import click
from jinja2 import Environment, FileSystemLoader


from qurator.dinglehopper import *


def gen_diff_report(gt_things, ocr_things, css_prefix, joiner, none, align):
    gtx = ''
    ocrx = ''

    def format_thing(t, css_classes=None):
        if t is None:
            t = none
            css_classes += ' ellipsis'
        if t == '\n':
            t = '<br>'

        if css_classes:
            return '<span class="{css_classes}">{t}</span>'.format(css_classes=css_classes, t=t)
        else:
            return '{t}'.format(t=t)

    for k, (g, o) in enumerate(align(gt_things, ocr_things)):
        if g == o:
            css_classes = None
        else:
            css_classes = '{css_prefix}diff{k} diff'.format(css_prefix=css_prefix, k=k)

        gtx += joiner + format_thing(g, css_classes)
        ocrx += joiner + format_thing(o, css_classes)

    return \
        '''
        <div class="row">
           <div class="col-md-6 gt">{}</div>
           <div class="col-md-6 ocr">{}</div>
        </div>
        '''.format(gtx, ocrx)


def process(gt, ocr, report_prefix):
    """Check OCR result against GT.

    The @click decorators change the signature of the decorated functions, so we keep this undecorated version and use
    Click on a wrapper.
    """

    gt_text = text(gt)
    ocr_text = text(ocr)

    gt_text = substitute_equivalences(gt_text)
    ocr_text = substitute_equivalences(ocr_text)

    cer = character_error_rate(gt_text, ocr_text)
    wer = word_error_rate(gt_text, ocr_text)

    char_diff_report = gen_diff_report(gt_text, ocr_text, css_prefix='c', joiner='', none='·', align=align)

    gt_words = words_normalized(gt_text)
    ocr_words = words_normalized(ocr_text)
    word_diff_report = gen_diff_report(gt_words, ocr_words, css_prefix='w', joiner=' ', none='⋯', align=seq_align)

    env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates')))
    for report_suffix in ('.html', '.json'):
        template_fn = 'report' + report_suffix + '.j2'
        out_fn = report_prefix + report_suffix

        template = env.get_template(template_fn)
        template.stream(
            gt=gt, ocr=ocr,
            cer=cer, wer=wer,
            char_diff_report=char_diff_report,
            word_diff_report=word_diff_report
        ).dump(out_fn)


@click.command()
@click.argument('gt', type=click.Path(exists=True))
@click.argument('ocr', type=click.Path(exists=True))
@click.argument('report_prefix', type=click.Path(), default='report')
def main(gt, ocr, report_prefix):
    process(gt, ocr, report_prefix)


if __name__ == '__main__':
    main()
