import unicodedata


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
        '': 'tz',       # MUFI: LATIN SMALL LIGATURE TZ
        'aͤ': 'ä',        # LATIN SMALL LETTER A, COMBINING LATIN SMALL LETTER E
        'oͤ': 'ö',        # LATIN SMALL LETTER O, COMBINING LATIN SMALL LETTER E
        'uͤ': 'ü',        # LATIN SMALL LETTER U, COMBINING LATIN SMALL LETTER E
        '\uf532': 'as',  # eMOP: Latin small ligature as
        '\uf533': 'is',  # eMOP: Latin small ligature is
        '\uf535': 'Qu',  # eMOP: Latin ligature capital Q small u
        'ĳ': 'ij',       # U+0133 LATIN SMALL LIGATURE IJ
        '\uE8BF': 'q&',  # MUFI: LATIN SMALL LETTER Q LIGATED WITH FINAL ET  XXX How to replace this correctly?
        '\uEBA5': 'ſp',  # MUFI: LATIN SMALL LIGATURE LONG S P
        'ﬆ': 'st',      # U+FB06 LATIN SMALL LIGATURE ST
        '\uF50E': 'q́'    # U+F50E LATIN SMALL LETTER Q WITH ACUTE ACCENT
    }

    s = unicodedata.normalize('NFC', s)
    for fr, to in equivalences.items():
        s = s.replace(fr, to)
    return s
