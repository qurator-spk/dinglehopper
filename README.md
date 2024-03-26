dinglehopper
============

dinglehopper is an OCR evaluation tool and reads
[ALTO](https://github.com/altoxml),
[PAGE](https://github.com/PRImA-Research-Lab/PAGE-XML) and text files.  It
compares a ground truth (GT) document page with a OCR result page to compute
metrics and a word/character differences report. It also supports batch processing by
generating, aggregating and summarizing multiple reports.

[![Tests](https://github.com/qurator-spk/dinglehopper/actions/workflows/test.yml/badge.svg)](https://github.com/qurator-spk/dinglehopper/actions?query=workflow:"test")
[![GitHub tag](https://img.shields.io/github/tag/qurator-spk/dinglehopper?include_prereleases=&sort=semver&color=blue)](https://github.com/qurator-spk/dinglehopper/releases/)
[![License](https://img.shields.io/badge/License-Apache-blue)](#license)
[![issues - dinglehopper](https://img.shields.io/github/issues/qurator-spk/dinglehopper)](https://github.com/qurator-spk/dinglehopper/issues)

Goals
-----
* Useful
  * As a UI tool
  * For an automated evaluation
  * As a library
* Unicode support

Installation
------------

It's best to use pip to install the package from PyPI, e.g.:
```
pip install dinglehopper
```

Usage
-----
~~~
Usage: dinglehopper [OPTIONS] GT OCR [REPORT_PREFIX] [REPORTS_FOLDER]

  Compare the PAGE/ALTO/text document GT against the document OCR.

  dinglehopper detects if GT/OCR are ALTO or PAGE XML documents to extract
  their text and falls back to plain text if no ALTO or PAGE is detected.

  The files GT and OCR are usually a ground truth document and the result of
  an OCR software, but you may use dinglehopper to compare two OCR results. In
  that case, use --no-metrics to disable the then meaningless metrics and also
  change the color scheme from green/red to blue.

  The comparison report will be written to
  $REPORTS_FOLDER/$REPORT_PREFIX.{html,json}, where $REPORTS_FOLDER defaults
  to the current working directory and $REPORT_PREFIX defaults to "report".
  The reports include the character error rate (CER) and the word error rate
  (WER).

  By default, the text of PAGE files is extracted on 'region' level. You may
  use "--textequiv-level line" to extract from the level of TextLine tags.

Options:
  --metrics / --no-metrics  Enable/disable metrics and green/red
  --differences BOOLEAN     Enable reporting character and word level
                            differences
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

Batch comparison between folders of GT and OCR files can be done by simply providing
folders:
~~~
dinglehopper gt/ ocr/ report output_folder/
~~~
This assumes that you have files with the same name in both folders, e.g.
`gt/00000001.page.xml` and `ocr/00000001.alto.xml`.

The example generates reports for each set of files, with the prefix `report`, in the
(automatically created) folder `output_folder/`.

By default, the JSON report does not contain the character and word differences, only
the calculated metrics. If you want to include the differences, use the
`--differences` flag:

~~~
dinglehopper gt/ ocr/ report output_folder/ --differences
~~~

### dinglehopper-summarize
A set of (JSON) reports can be summarized into a single set of
reports. This is useful after having generated reports in batch.
Example:
~~~
dinglehopper-summarize output_folder/
~~~
This generates `summary.html` and `summary.json` in the same `output_folder`.

If you are summarizing many reports and have used the `--differences` flag while
generating them, it may be useful to limit the number of differences reported by using
the `--occurences-threshold` parameter. This will reduce the size of the generated HTML
report, making it easier to open and navigate. Note that the JSON report will still
contain all differences. Example:
~~~
dinglehopper-summarize output_folder/ --occurences-threshold 10
~~~

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
