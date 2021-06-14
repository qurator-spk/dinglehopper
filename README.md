dinglehopper
============

dinglehopper is an OCR evaluation tool and reads
[ALTO](https://github.com/altoxml),
[PAGE](https://github.com/PRImA-Research-Lab/PAGE-XML) and text files.  It
compares a ground truth (GT) document page with a OCR result page to compute
metrics and a word/character differences report.

[![Build Status](https://circleci.com/gh/qurator-spk/dinglehopper.svg?style=svg)](https://circleci.com/gh/qurator-spk/dinglehopper)

Goals
-----
* Useful
  * As a UI tool
  * For an automated evaluation
  * As a library
* Unicode support

Installation
------------
It's best to use pip, e.g.:
~~~
sudo pip install .
~~~

Usage
-----
~~~
Usage: dinglehopper [OPTIONS] GT OCR [REPORT_PREFIX]

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

  The html report can be enabled/disabled using --html/--no-html.

  By default, the text of PAGE files is extracted on 'region' level. You may
  use "--textequiv-level line" to extract from the level of TextLine tags.

Options:
  --metrics                 Enable different metrics like ca|cer, wa|wer, boc and bow.
  --textequiv-level LEVEL   PAGE TextEquiv level to extract text from
  --html / --no-html        Enabling/disabling html report.
  --progress                Show progress bar
  --help                    Show this message and exit.
~~~

For example:
~~~
dinglehopper some-document.gt.page.xml some-document.ocr.alto.xml
~~~
This generates `report.html` and `report.json`.

![dinglehopper displaying metrics and character differences](.screenshots/dinglehopper.png?raw=true)

### dinglehopper-extract
The tool `dinglehopper-extract` extracts the text of the given input file on
stdout, for example:

~~~
dinglehopper-extract --textequiv-level line OCR-D-GT-PAGE/00000024.page.xml
~~~

### OCR-D
As a OCR-D processor:
~~~
ocrd-dinglehopper -I OCR-D-GT-PAGE,OCR-D-OCR-TESS -O OCR-D-OCR-TESS-EVAL
~~~
This generates HTML and JSON reports in the `OCR-D-OCR-TESS-EVAL` filegroup.

The OCR-D processor has these parameters:

| Parameter                 | Meaning                                                             |
| ------------------------- | ------------------------------------------------------------------- |
| `-P metrics cer,wer`      | Enable character error rate and word error rate (default)           |
| `-P textequiv_level line` | (PAGE) Extract text from TextLine level (default: TextRegion level) |
| `-P html false`           | Enabling/disabling html report (default: enabled).                  |

For example:
~~~
ocrd-dinglehopper -I ABBYY-FULLTEXT,OCR-D-OCR-CALAMARI -O OCR-D-OCR-COMPARE-ABBYY-CALAMARI -P metrics cer,wer -P html false
~~~

Developer information
---------------------
*Please refer to [README-DEV.md](README-DEV.md).*
