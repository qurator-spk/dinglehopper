dinglehopper
============

dinglehopper is an OCR evaluation tool and reads [ALTO](https://github.com/altoxml), [PAGE](https://github.com/PRImA-Research-Lab/PAGE-XML) and text files.

[![Build Status](https://travis-ci.org/qurator-spk/dinglehopper.svg?branch=master)](https://travis-ci.org/qurator-spk/dinglehopper)

Goals
-----
* Useful
  * As a UI tool
  * For an automated evaluation
  * As a library
* Unicode support

Usage
-----
~~~
dinglehopper some-document.gt.page.xml some-document.ocr.alto.xml
~~~
This generates `report.html` and `report.json`.


As a OCR-D processor:
~~~
ocrd-dinglehopper -m mets.xml -I OCR-D-GT-PAGE,OCR-D-OCR-TESS -O OCR-D-OCR-TESS-EVAL
~~~
This generates HTML and JSON reports in the `OCR-D-OCR-TESS-EVAL` filegroup.


![dinglehopper displaying metrics and character differences](.screenshots/dinglehopper.png?raw=true)
