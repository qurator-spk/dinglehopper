import os

import click
from jinja2 import Environment, FileSystemLoader


from qurator.dinglehopper import *


def gen_diff_report(gt_things, ocr_things, css_prefix, joiner, none):
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


@click.command()
@click.argument('gt', type=click.Path(exists=True))
@click.argument('ocr', type=click.Path(exists=True))
def process(gt, ocr):
    """Check OCR result against GT"""

    gt_text = text(gt)
    ocr_text = text(ocr)

    gt_text = substitute_equivalences(gt_text)
    ocr_text = substitute_equivalences(ocr_text)

    cer = character_error_rate(gt_text, ocr_text)
    wer = word_error_rate(gt_text, ocr_text)
    uwer = unordered_word_error_rate(gt_text, ocr_text)

    char_diff_report = gen_diff_report(gt_text, ocr_text, css_prefix='c', joiner='', none='·')

    gt_words = words(gt_text)
    ocr_words = words(ocr_text)
    word_diff_report = gen_diff_report(gt_words, ocr_words, css_prefix='w', joiner=' ', none='⋯')

    env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates')))
    for out_fn in ('report.html', 'report.json'):
        template_fn = out_fn + '.j2'
        template = env.get_template(template_fn)
        template.stream(
            gt=gt, ocr=ocr,
            cer=cer, wer=wer, uwer=uwer,
            char_diff_report=char_diff_report,
            word_diff_report=word_diff_report
        ).dump(out_fn)


def main():
    process()


if __name__ == '__main__':
    main()
