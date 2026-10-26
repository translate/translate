"""Resource budgets for compressed translation inputs."""

from __future__ import annotations

import bz2
import gzip
from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import pytest

from translate.storage import factory, po
from translate.storage.base import ParseError
from translate.storage.extraction_limits import ExtractionBudget
from translate.storage.idml import INLINE_ELEMENTS, NO_TRANSLATE_ELEMENTS, open_idml
from translate.storage.odf_io import open_odf
from translate.storage.odf_shared import inline_elements, no_translate_content_elements
from translate.storage.xliff import Xliff1File
from translate.storage.xml_extract.extract import (
    IdMaker,
    ParseState,
    build_idml_store,
    build_store,
    make_postore_adder,
)

OFFICE_NS = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
TEXT_NS = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"


def _odf_xml(paragraphs: int) -> bytes:
    start = (
        f'<office:document-content xmlns:office="{OFFICE_NS}" '
        f'xmlns:text="{TEXT_NS}"><office:body><office:text>'
    )
    body = "".join(f"<text:p>Unique paragraph {i}</text:p>" for i in range(paragraphs))
    return (
        start + body + "</office:text></office:body></office:document-content>"
    ).encode()


def test_odf_xml_size_limit_precedes_read(tmp_path) -> None:
    archive = tmp_path / "large.odt"
    xml = _odf_xml(100)
    with ZipFile(archive, "w", ZIP_DEFLATED) as output:
        output.writestr("content.xml", xml)

    with pytest.raises(ParseError, match="byte extraction limit"):
        open_odf(archive, budget=ExtractionBudget(max_xml_bytes=len(xml) - 1))


def test_odf_element_and_unit_limits() -> None:
    xml = _odf_xml(12)
    state = ParseState(no_translate_content_elements, inline_elements)
    store = Xliff1File()
    with pytest.raises(ParseError, match="element extraction limit"):
        build_store(
            BytesIO(xml), store, state, budget=ExtractionBudget(max_elements=10)
        )
    assert not store.units

    state = ParseState(no_translate_content_elements, inline_elements)
    store = Xliff1File()
    with pytest.raises(ParseError, match="unit extraction limit"):
        build_store(BytesIO(xml), store, state, budget=ExtractionBudget(max_units=5))
    assert len(store.units) == 5


def test_odf_element_limit_is_cumulative_across_members() -> None:
    budget = ExtractionBudget(max_elements=9)
    store = Xliff1File()
    build_store(
        BytesIO(_odf_xml(3)),
        store,
        ParseState(no_translate_content_elements, inline_elements),
        budget=budget,
    )
    with pytest.raises(ParseError, match="element extraction limit"):
        build_store(
            BytesIO(_odf_xml(3)),
            store,
            ParseState(no_translate_content_elements, inline_elements),
            budget=budget,
        )


def test_idml_xml_size_limit_is_cumulative(tmp_path) -> None:
    archive = tmp_path / "large.idml"
    with ZipFile(archive, "w", ZIP_DEFLATED) as output:
        output.writestr("Stories/Story_1.xml", b"<Story/>")
        output.writestr("Stories/Story_2.xml", b"<Story/>")
    with pytest.raises(ParseError, match="byte extraction limit"):
        open_idml(archive, budget=ExtractionBudget(max_xml_bytes=15))


def test_idml_unit_limit() -> None:
    archive = Path(__file__).parents[1] / "convert" / "test.idml"
    budget = ExtractionBudget(max_units=1)
    store = po.pofile()
    id_maker = IdMaker()

    def extract_stories() -> None:
        for filename, data in open_idml(archive, budget=budget).items():
            build_idml_store(
                BytesIO(data),
                store,
                ParseState(NO_TRANSLATE_ELEMENTS, INLINE_ELEMENTS),
                store_adder=make_postore_adder(store, id_maker, filename),
                budget=budget,
            )

    with pytest.raises(ParseError, match="unit extraction limit"):
        extract_stories()


@pytest.mark.parametrize(
    ("suffix", "compress"), [("gz", gzip.compress), ("bz2", bz2.compress)]
)
def test_factory_compressed_limits(tmp_path, suffix, compress) -> None:
    path = tmp_path / f"many.po.{suffix}"
    content = b"".join(
        f'msgid "string {i}"\nmsgstr "translation {i}"\n\n'.encode() for i in range(10)
    )
    path.write_bytes(compress(content))

    with pytest.raises(ParseError, match="byte extraction limit"):
        factory.getobject(str(path), max_decompressed_bytes=len(content) - 1)
    with pytest.raises(ParseError, match="unit extraction limit"):
        factory.getobject(str(path), max_units=5)
    assert len(factory.getobject(str(path), max_units=10).units) == 10
