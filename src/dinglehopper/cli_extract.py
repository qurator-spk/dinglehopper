import os

import click
from ocrd_utils import initLogging

from .extracted_text import ExtractedText
from .ocr_files import extract


@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "--textequiv-level",
    default="region",
    help="PAGE TextEquiv level to extract text from",
    metavar="LEVEL",
)
def main(input_file, textequiv_level):
    """
    Extract the text of the given INPUT_FILE.

    dinglehopper detects if INPUT_FILE is an ALTO or PAGE XML document to extract
    its text and falls back to plain text if no ALTO or PAGE is detected.

    By default, the text of PAGE files is extracted on 'region' level. You may
    use "--textequiv-level line" to extract from the level of TextLine tags.
    """
    initLogging()
    input_text = extract(input_file, textequiv_level=textequiv_level).text
    print(input_text)


if __name__ == "__main__":
    main()
