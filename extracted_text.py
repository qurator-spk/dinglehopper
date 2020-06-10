import attr
import unicodedata


# TODO handle grapheme cluster positions?


@attr.s(frozen=True)
class ExtractedText:
    segments = attr.ib()
    joiner = attr.ib(type=str)
    # XXX Use type annotations for attr types when support for Python 3.5 is dropped
    # XXX Also I think these are not validated?

    @property
    def text(self):
        return self.joiner.join(s.text for s in self.segments)

    def segment_id_for_pos(self, pos):
        i = 0
        for s in self.segments:
            if i <= pos < i + len(s.text):
                return s.id
            i += len(s.text)
            if i <= pos < i + len(self.joiner):
                return None
            i += len(self.joiner)


NORM_NFC = 0


def normalize(text, normalization):
    if normalization == NORM_NFC:
        return unicodedata.normalize('NFC', text)
    else:
        raise ValueError()


@attr.s(frozen=True)
class ExtractedTextSegment:
    id = attr.ib(type=str)
    text = attr.ib(type=str)
    @text.validator
    def check(self, attribute, value):
        if normalize(value, self.normalization) != value:
            raise ValueError('String "{}" is not normalized.'.format(value))
    normalization = attr.ib(default=NORM_NFC)
