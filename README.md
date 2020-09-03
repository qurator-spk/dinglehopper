dinglehopper
============

dinglehopper is an OCR evaluation tool and reads
[ALTO](https://github.com/altoxml),
[PAGE](https://github.com/PRImA-Research-Lab/PAGE-XML) and text files.  It
compares a ground truth (GT) document page with a OCR result page to compute
metrics and a word/character differences report.

[![Build Status](https://travis-ci.org/qurator-spk/dinglehopper.svg?branch=master)](https://travis-ci.org/qurator-spk/dinglehopper)

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

  The files GT and OCR are usually a ground truth document and the result of
  an OCR software, but you may use dinglehopper to compare two OCR results.
  In that case, use --no-metrics to disable the then meaningless metrics and
  also change the color scheme from green/red to blue.

Options:
  --metrics / --no-metrics  Enable/disable metrics and green/red
  --help                    Show this message and exit.
~~~

For example:
~~~
dinglehopper some-document.gt.page.xml some-document.ocr.alto.xml
~~~
This generates `report.html` and `report.json`.


As a OCR-D processor:
~~~
ocrd-dinglehopper -I OCR-D-GT-PAGE,OCR-D-OCR-TESS -O OCR-D-OCR-TESS-EVAL
~~~
This generates HTML and JSON reports in the `OCR-D-OCR-TESS-EVAL` filegroup.


![dinglehopper displaying metrics and character differences](.screenshots/dinglehopper.png?raw=true)

You may also want to disable metrics and the green-red color scheme by
parameter:

~~~
ocrd-dinglehopper -I ABBYY-FULLTEXT,OCR-D-OCR-CALAMARI -O OCR-D-OCR-COMPARE-ABBYY-CALAMARI -p '{"metrics": false}'
~~~

Testing
-------
Use `pytest` to run the tests in [the tests directory](qurator/dinglehopper/tests):
~~~
virtualenv -p /usr/bin/python3 venv
. venv/bin/activate
pip install -r requirements.txt
pip install pytest
pytest
~~~
