import os
import re
import textwrap

import lxml.etree as ET

from .. import alto_namespace, alto_text, page_namespace, page_text, plain_text, text
from .util import working_directory

data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def test_alto_namespace():
    tree = ET.parse(os.path.join(data_dir, "test.alto3.xml"))
    assert alto_namespace(tree) == "http://www.loc.gov/standards/alto/ns-v3#"


def test_alto_text():
    tree = ET.parse(os.path.join(data_dir, "test.alto3.xml"))
    result = alto_text(tree)
    expected = textwrap.dedent(
        """\
        über die vielen Sorgen wegen deſſelben vergaß
        Hartkopf, der Frau Amtmännin das ver-
        ſprochene zu überliefern."""
    )
    assert result == expected


def test_alto_text_ALTO1():
    tree = ET.parse(os.path.join(data_dir, "test.alto1.xml"))
    assert "being erected at the Broadway stock" in alto_text(tree)


def test_alto_text_ALTO2():
    tree = ET.parse(os.path.join(data_dir, "test.alto2.xml"))
    assert (
        "Halbmonde, die genau durch einen Ouerstrich halbiert\nsind und an beiden Enden"
        in alto_text(tree)
    )


def test_alto_text_ALTO3():
    tree = ET.parse(os.path.join(data_dir, "test.alto3.xml"))
    assert "über die vielen Sorgen wegen deſſelben vergaß" in alto_text(tree)


def test_page_namespace():
    tree = ET.parse(os.path.join(data_dir, "test.page2018.xml"))
    assert (
        page_namespace(tree)
        == "http://schema.primaresearch.org/PAGE/gts/pagecontent/2018-07-15"
    )


def test_page_test():
    tree = ET.parse(os.path.join(data_dir, "test.page2018.xml"))
    result = page_text(tree)

    # We are currently normalizing on extraction, so the text is normalized.
    #
    #  expected = textwrap.dedent("""\
    #      ber die vielen Sorgen wegen deelben vergaß
    #      Hartkopf, der Frau Amtmnnin das ver⸗
    #      ſproene zu berliefern. — Ein Erpreer
    #      wurde an ihn abgeſit, um ihn ums Him⸗
    #      melswien zu ſagen, daß er das Verſproene
    #      glei den Augenbli berbringen mte, die
    #      Frau Amtmnnin htte  auf ihn verlaen,
    #      und nun wßte e nit, was e anfangen
    #      ſote. Den Augenbli ſote er kommen,
    #      ſon vergieng e in ihrer Ang. — Die
    #      Ge wren ſon angekommen, und es fehlte
    #      ihr do no an aem. —
    #      Hartkopf mußte  er bennen, und
    #      endli na langem Nadenken ﬁel es ihm er
    #      wieder ein. — Er langte den Zettel aus dem
    #      Accisbue heraus, und ſagte ſeiner Frau, daß
    #      e das, was da wre, herbeyſaﬀen mte.
    #      Jndeß mangelten do einige Generalia, die
    #      alſo wegﬁelen. — Hartkopf gieng ſelb
    #      mit und berbrate es. —""")
    expected = textwrap.dedent(
        """\
        über die vielen Sorgen wegen deſſelben vergaß
        Hartkopf, der Frau Amtmännin das ver-
        ſprochene zu überliefern. – Ein Erpreſſer
        wurde an ihn abgeſchickt, um ihn ums Him-
        melswillen zu ſagen, daß er das Verſprochene
        gleich den Augenblick überbringen möchte, die
        Frau Amtmännin hätte ſich auf ihn verlaſſen,
        und nun wüßte ſie nicht, was ſie anfangen
        ſollte. Den Augenblick ſollte er kommen,
        ſonſt vergieng ſie in ihrer Angſt. – Die
        Gäſte wären ſchon angekommen, und es fehlte
        ihr doch noch an allem. –
        Hartkopf mußte ſich erſt beſinnen, und
        endlich nach langem Nachdenken fiel es ihm erſt
        wieder ein. – Er langte den Zettel aus dem
        Accisbuche heraus, und ſagte ſeiner Frau, daß
        ſie das, was da wäre, herbeyſchaffen möchte.
        Jndeß mangelten doch einige Generalia, die
        alſo wegfielen. – Hartkopf gieng ſelbſt
        mit und überbrachte es. –"""
    )
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
    tree = ET.parse(
        os.path.join(data_dir, "brochrnx_73075507X/00000139.ocrd-tess.ocr.page.xml")
    )
    result = page_text(tree)
    assert result


def test_page_order():
    # This file contains TextRegions where file order is not the same as reading order.
    tree = ET.parse(os.path.join(data_dir, "order.page.xml"))
    result = page_text(tree)

    print(result)
    assert re.search(
        r"Herr Konfrater.*75.*Etwas f.r Wittwen.*Ein gewi.{1,2}er Lord.*76\. Die",
        result,
        re.DOTALL,
    )


def test_page_mixed_regions():
    # This file contains ImageRegions and TextRegions in the ReadingOrder
    tree = ET.parse(os.path.join(data_dir, "mixed-regions.page.xml"))
    result = page_text(tree)

    assert "non exaudiam uos. Chriſtiani uero quia orant iuxta" in result


def test_page_level():
    # This file contains inconsistent TextRegion and TextLine texts

    # TextRegion
    tree = ET.parse(os.path.join(data_dir, "levels-are-different.page.xml"))
    result = page_text(tree)
    assert result == "Inconsistent dummy region text"
    tree = ET.parse(os.path.join(data_dir, "levels-are-different.page.xml"))
    result = page_text(tree, textequiv_level="region")
    assert result == "Inconsistent dummy region text"

    # TextLine
    tree = ET.parse(os.path.join(data_dir, "levels-are-different.page.xml"))
    result = page_text(tree, textequiv_level="line")
    assert (
        result
        == "Hand, Mylord? fragte der Graf von Rocheſter.\n"
        + "Als er einsmals in dem Oberhauſe eine Bill we-"
    )


def test_text():
    assert "being erected at the Broadway stock" in text(
        os.path.join(data_dir, "test.alto1.xml")
    )
    assert "wieder ein. – Er langte den Zettel aus dem" in text(
        os.path.join(data_dir, "test.page2018.xml")
    )
    assert "Lorem ipsum" in text(os.path.join(data_dir, "test.txt"))


def test_plain(tmp_path):
    with working_directory(tmp_path):
        with open("ocr.txt", "w") as ocrf:
            ocrf.write("AAAAB")

        result = plain_text("ocr.txt")
        expected = "AAAAB"
        assert result == expected
