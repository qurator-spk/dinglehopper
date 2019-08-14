def substitute_equivalences(s):

    # These are for OCR-D GT vs Tesseract frk vs Calamari GT4HistOCR
    # It might make sense to use different rules for GT and for the different OCR
    equivalences = {
        '': 'ü',
        '': 'ſſ',
        "\ueba7": 'ſſi',  # MUFI: LATIN SMALL LIGATURE LONG S LONG S I
        '': 'ä',
        '': 'ch',
        '==': '–',  # → en-dash
        '—': '–',   # em-dash → en-dash
        '': 'ck',
        '': 'll',
        '': 'ö',
        '': 'ſi',
        '': 'ſt',
        'ﬁ': 'fi',
        'ﬀ': 'ff',
        'ﬂ': 'fl',
        'ﬃ': 'ffi',
        '': 'ct',
        '’': '\'',
        '⸗': '-',
        '': 'tz',  # MUFI: LATIN SMALL LIGATURE TZ
        'aͤ': 'ä',   # LATIN SMALL LETTER A, COMBINING LATIN SMALL LETTER E
        'oͤ': 'ö',   # LATIN SMALL LETTER O, COMBINING LATIN SMALL LETTER E
        'uͤ': 'ü',   # LATIN SMALL LETTER U, COMBINING LATIN SMALL LETTER E
    }
    for fr, to in equivalences.items():
        s = s.replace(fr, to)
    return s
