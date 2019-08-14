import os
import re

import lxml.etree as ET
import textwrap

from .. import alto_namespace, alto_text, page_namespace, page_text, text

data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


def test_alto_namespace():
    tree = ET.parse(os.path.join(data_dir, 'test.alto3.xml'))
    assert alto_namespace(tree) == 'http://www.loc.gov/standards/alto/ns-v3#'


def test_alto_text():
    tree = ET.parse(os.path.join(data_dir, 'test.alto3.xml'))
    result = alto_text(tree)
    expected = textwrap.dedent("""\
        über die vielen Sorgen wegen deſſelben vergaß
        Hartkopf, der Frau Amtmännin das ver-
        ſprochene zu überliefern.""")
    assert result == expected


def test_alto_text_ALTO1():
    tree = ET.parse(os.path.join(data_dir, 'test.alto1.xml'))
    assert "being erected at the Broadway stock" in alto_text(tree)


def test_alto_text_ALTO2():
    tree = ET.parse(os.path.join(data_dir, 'test.alto2.xml'))
    assert "Halbmonde, die genau durch einen Ouerstrich halbiert\nsind und an beiden Enden" in alto_text(tree)


def test_alto_text_ALTO3():
    tree = ET.parse(os.path.join(data_dir, 'test.alto3.xml'))
    assert "über die vielen Sorgen wegen deſſelben vergaß" in alto_text(tree)


def test_page_namespace():
    tree = ET.parse(os.path.join(data_dir, 'test.page2018.xml'))
    assert page_namespace(tree) == 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2018-07-15'


def test_page_test():
    tree = ET.parse(os.path.join(data_dir, 'test.page2018.xml'))
    result = page_text(tree)
    expected = textwrap.dedent("""\
        ber die vielen Sorgen wegen deelben vergaß
        Hartkopf, der Frau Amtmnnin das ver⸗
        ſproene zu berliefern. — Ein Erpreer
        wurde an ihn abgeſit, um ihn ums Him⸗
        melswien zu ſagen, daß er das Verſproene
        glei den Augenbli berbringen mte, die
        Frau Amtmnnin htte  auf ihn verlaen,
        und nun wßte e nit, was e anfangen
        ſote. Den Augenbli ſote er kommen,
        ſon vergieng e in ihrer Ang. — Die
        Ge wren ſon angekommen, und es fehlte
        ihr do no an aem. —
        Hartkopf mußte  er bennen, und
        endli na langem Nadenken ﬁel es ihm er
        wieder ein. — Er langte den Zettel aus dem
        Accisbue heraus, und ſagte ſeiner Frau, daß
        e das, was da wre, herbeyſaﬀen mte.
        Jndeß mangelten do einige Generalia, die
        alſo wegﬁelen. — Hartkopf gieng ſelb
        mit und berbrate es. —""")
    assert result == expected


def test_page_with_empty_region():
    # This file contains an empty TextRegion:
    #
    #     <TextRegion id="region0000">
    #         <Coords points="488,133 1197,133 1197,193 488,193"/>
    #         <TextEquiv>
    #             <Unicode></Unicode>
    #         </TextEquiv>
    #     </TextRegion>
    tree = ET.parse(os.path.join(data_dir, 'brochrnx_73075507X/00000139.ocrd-tess.ocr.page.xml'))
    result = page_text(tree)
    assert result


def test_page_order():
    # This file contains TextRegions where file order is not the same as reading order.
    tree = ET.parse(os.path.join(data_dir, 'order.page.xml'))
    result = page_text(tree)

    assert re.search(r'Herr Konfrater.*75.*Etwas f.r Wittwen.*Ein gewi.er Lord.*76\. Die', result, re.DOTALL)


def test_text():
    assert "being erected at the Broadway stock" in text(os.path.join(data_dir, 'test.alto1.xml'))
    assert "wieder ein. — Er langte den Zettel aus dem" in text(os.path.join(data_dir, 'test.page2018.xml'))
    assert "Lorem ipsum" in text(os.path.join(data_dir, 'test.txt'))
