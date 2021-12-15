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
  an OCR software, but you may use dinglehopper to compare two OCR results.
  In that case, use --no-metrics to disable the then meaningless metrics and
  also change the color scheme from green/red to blue.

  The comparison report will be written to $REPORT_PREFIX.{html,json}, where
  $REPORT_PREFIX defaults to "report". The reports include the character
  error rate (CER) and the word error rate (WER).

  By default, the text of PAGE files is extracted on 'region' level. You may
  use "--textequiv-level line" to extract from the level of TextLine tags.

Options:
  --metrics / --no-metrics  Enable/disable metrics and green/red
  --textequiv-level LEVEL   PAGE TextEquiv level to extract text from
  --progress                Show progress bar
  --help                    Show this message and exit.
~~~

For example:
~~~
dinglehopper some-document.gt.page.xml some-document.ocr.alto.xml
~~~
This generates `report.html` and `report.json`.

![dinglehopper displaying metrics and character differences](.screenshots/dinglehopper.png?raw=true)

### dinglehopper-line-dirs
You also may want to compare a directory of GT text files (i.e. `gt/line0001.gt.txt`)
with a directory of OCR text files (i.e. `ocr/line0001.some-ocr.txt`) with a separate
CLI interface:

~~~
dinglehopper-line-dirs gt/ ocr/
~~~

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
| `-P metrics false`        | Disable metrics and the green-red color scheme (default: enabled)   |
| `-P textequiv_level line` | (PAGE) Extract text from TextLine level (default: TextRegion level) |

For example:
~~~
ocrd-dinglehopper -I ABBYY-FULLTEXT,OCR-D-OCR-CALAMARI -O OCR-D-OCR-COMPARE-ABBYY-CALAMARI -P metrics false
~~~

Developer information
---------------------
*Please refer to [README-DEV.md](README-DEV.md).*
