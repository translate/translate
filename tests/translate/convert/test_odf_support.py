import copy
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile

from lxml import etree

from translate.convert import odf2po, odf2xliff, po2odf, xliff2odf
from translate.misc.xml_helpers import parse_xml
from translate.storage import po

XLIFF_NS = "urn:oasis:names:tc:xliff:document:1.1"
OFFICE_NS = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
TEXT_NS = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"


def _create_odf(
    path,
    members,
    mimetype="application/vnd.oasis.opendocument.text",
    mimetype_compression=ZIP_STORED,
):
    with ZipFile(path, "w") as archive:
        archive.writestr("mimetype", mimetype, compress_type=mimetype_compression)
        for filename, data in members.items():
            archive.writestr(filename, data)


def _extract(template, xliff_path):
    with template.open("rb") as input_file, xliff_path.open("wb") as output_file:
        odf2xliff.convertodf(input_file, output_file, None)


def _add_targets(xliff_path, translations):
    tree = etree.parse(xliff_path)
    namespace = f"{{{XLIFF_NS}}}"
    for file_node in tree.getroot().iterchildren(f"{namespace}file"):
        original = file_node.get("original")
        for unit in file_node.iterdescendants(f"{namespace}trans-unit"):
            source = unit.find(f"{namespace}source")
            assert source is not None
            target = etree.Element(f"{namespace}target")
            target.text = source.text
            target.extend(copy.deepcopy(child) for child in source)
            for node in target.iter():
                if node.text in translations.get(original, {}):
                    node.text = translations[original][node.text]
            unit.insert(unit.index(source) + 1, target)
    tree.write(xliff_path, encoding="UTF-8", xml_declaration=True)


def _reconstruct(template, xliff_path, output):
    with (
        template.open("rb") as template_file,
        xliff_path.open("rb") as input_file,
        output.open("wb") as output_file,
    ):
        xliff2odf.convertxliff(input_file, output_file, template_file)


def test_embedded_odf_inline_paragraph_roundtrip(tmp_path) -> None:
    template = tmp_path / "embedded.odt"
    xliff_path = tmp_path / "embedded.xlf"
    output = tmp_path / "translated.odt"
    content = f"""<office:document-content
        xmlns:office="{OFFICE_NS}" xmlns:text="{TEXT_NS}"
        xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
        xmlns:xlink="http://www.w3.org/1999/xlink">
      <office:body><office:text>
        <text:p><text:span><text:span>Main text</text:span></text:span></text:p>
        <draw:object xlink:href="./Object 1"/>
      </office:text></office:body>
    </office:document-content>"""
    embedded = f"""<office:document-content
        xmlns:office="{OFFICE_NS}" xmlns:text="{TEXT_NS}">
      <office:body><office:text><text:p>Embedded text</text:p></office:text></office:body>
    </office:document-content>"""
    manifest = """<manifest:manifest
        xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0">
      <manifest:file-entry manifest:full-path="/"
        manifest:media-type="application/vnd.oasis.opendocument.text"/>
      <manifest:file-entry manifest:full-path="Object 1/"
        manifest:media-type="application/vnd.oasis.opendocument.chart"/>
    </manifest:manifest>"""
    _create_odf(
        template,
        {
            "content.xml": content,
            "META-INF/manifest.xml": manifest,
            "Object 1/content.xml": embedded,
        },
        mimetype_compression=ZIP_DEFLATED,
    )

    _extract(template, xliff_path)

    xliff_root = etree.parse(xliff_path).getroot()
    namespace = f"{{{XLIFF_NS}}}"
    files = list(xliff_root.iterchildren(f"{namespace}file"))
    assert [node.get("original") for node in files] == [
        "content.xml",
        "Object 1/content.xml",
    ]
    main_unit = next(files[0].iterdescendants(f"{namespace}trans-unit"))
    unit_id = main_unit.get("id")
    assert unit_id is not None
    assert unit_id.endswith("/text:p[0]")
    source = main_unit.find(f"{namespace}source")
    assert source is not None
    assert etree.QName(source[0]).localname == "g"
    assert etree.QName(source[0][0]).localname == "g"

    _add_targets(
        xliff_path,
        {
            "content.xml": {"Main text": "Main translation"},
            "Object 1/content.xml": {"Embedded text": "Embedded translation"},
        },
    )
    _reconstruct(template, xliff_path, output)

    with ZipFile(output) as archive:
        infos = archive.infolist()
        assert infos[0].filename == "mimetype"
        assert infos[0].compress_type == ZIP_STORED
        assert infos[0].extra == b""
        assert "Main translation" in "".join(
            parse_xml(archive.read("content.xml"), collect_ids=False).itertext()
        )
        assert "Embedded translation" in "".join(
            parse_xml(
                archive.read("Object 1/content.xml"), collect_ids=False
            ).itertext()
        )


def test_numeric_xml_id_is_accepted(tmp_path) -> None:
    template = tmp_path / "numeric-id.odt"
    xliff_path = tmp_path / "numeric-id.xlf"
    content = f"""<office:document-content
        xmlns:office="{OFFICE_NS}" xmlns:text="{TEXT_NS}"
        xmlns:xml="http://www.w3.org/XML/1998/namespace">
      <office:body><office:text><text:p xml:id="123">Text</text:p></office:text></office:body>
    </office:document-content>"""
    _create_odf(template, {"content.xml": content})

    _extract(template, xliff_path)

    assert b"Text" in xliff_path.read_bytes()


def test_formula_root_roundtrip(tmp_path) -> None:
    template = tmp_path / "formula.odf"
    xliff_path = tmp_path / "formula.xlf"
    output = tmp_path / "translated.odf"
    math_ns = "http://www.w3.org/1998/Math/MathML"
    content = f'<math xmlns="{math_ns}"><mtext>Formula text</mtext></math>'
    _create_odf(
        template,
        {"content.xml": content},
        mimetype="application/vnd.oasis.opendocument.formula",
    )

    _extract(template, xliff_path)
    _add_targets(xliff_path, {"content.xml": {"Formula text": "Formula translation"}})
    _reconstruct(template, xliff_path, output)

    with ZipFile(output) as archive:
        assert "Formula translation" in "".join(
            parse_xml(archive.read("content.xml"), collect_ids=False).itertext()
        )


def test_explicit_default_named_prefix_roundtrip(tmp_path) -> None:
    template = tmp_path / "named-default.odt"
    xliff_path = tmp_path / "named-default.xlf"
    output = tmp_path / "translated.odt"
    content = f"""<office:document-content
        xmlns:office="{OFFICE_NS}" xmlns:_default="{TEXT_NS}">
      <office:body><office:text><_default:p>Prefix source</_default:p></office:text></office:body>
    </office:document-content>"""
    _create_odf(template, {"content.xml": content})

    _extract(template, xliff_path)
    _add_targets(xliff_path, {"content.xml": {"Prefix source": "Prefix translation"}})
    _reconstruct(template, xliff_path, output)

    with ZipFile(output) as archive:
        assert "Prefix translation" in "".join(
            parse_xml(archive.read("content.xml"), collect_ids=False).itertext()
        )


def test_placeable_only_xliff_target_is_applied(tmp_path) -> None:
    template = tmp_path / "placeable-only.odt"
    xliff_path = tmp_path / "placeable-only.xlf"
    output = tmp_path / "translated.odt"
    content = f"""<office:document-content
        xmlns:office="{OFFICE_NS}" xmlns:text="{TEXT_NS}">
      <office:body><office:text>
        <text:p><text:span>Remove this text</text:span></text:p>
      </office:text></office:body>
    </office:document-content>"""
    _create_odf(template, {"content.xml": content})
    _extract(template, xliff_path)

    tree = etree.parse(xliff_path)
    namespace = f"{{{XLIFF_NS}}}"
    unit = next(tree.iter(f"{namespace}trans-unit"))
    source = unit.find(f"{namespace}source")
    assert source is not None
    placeable_id = source[0].get("id")
    assert placeable_id is not None
    target = etree.Element(f"{namespace}target")
    etree.SubElement(target, f"{namespace}g", id=placeable_id)
    unit.insert(unit.index(source) + 1, target)
    tree.write(xliff_path, encoding="UTF-8", xml_declaration=True)

    _reconstruct(template, xliff_path, output)

    with ZipFile(output) as archive:
        root = parse_xml(archive.read("content.xml"), collect_ids=False)
        paragraph = root.find(f".//{{{TEXT_NS}}}p")
        assert paragraph is not None
        assert list(paragraph.itertext()) == []
        assert paragraph.find(f"{{{TEXT_NS}}}span") is not None


def test_legacy_single_file_xliff_is_supported(tmp_path) -> None:
    template = tmp_path / "legacy.odt"
    xliff_path = tmp_path / "legacy.xlf"
    output = tmp_path / "translated.odt"
    content = f"""<office:document-content
        xmlns:office="{OFFICE_NS}" xmlns:text="{TEXT_NS}">
      <office:body><office:text>
        <text:p>Legacy source</text:p><text:p>Keep source</text:p>
      </office:text></office:body>
    </office:document-content>"""
    _create_odf(template, {"content.xml": content})
    xliff_path.write_text(
        f"""<xliff xmlns="{XLIFF_NS}" version="1.1">
          <file original="legacy.odt" datatype="plaintext"><body>
            <trans-unit id="office:document-content[0]/office:body[0]/office:text[0]/text:p[0]">
              <source>Legacy source</source><target>Legacy translation</target>
            </trans-unit>
            <trans-unit id="office:document-content[0]/office:body[0]/office:text[0]/text:p[1]">
              <source>Keep source</source><target/>
            </trans-unit>
          </body></file>
        </xliff>""",
        encoding="utf-8",
    )

    _reconstruct(template, xliff_path, output)

    with ZipFile(output) as archive:
        text = "".join(
            parse_xml(archive.read("content.xml"), collect_ids=False).itertext()
        )
        assert "Legacy translation" in text
        assert "Keep source" in text


def test_duplicate_po_messages_roundtrip(tmp_path) -> None:
    template = tmp_path / "duplicates.odt"
    po_path = tmp_path / "duplicates.po"
    output = tmp_path / "translated.odt"
    content = f"""<office:document-content
        xmlns:office="{OFFICE_NS}" xmlns:text="{TEXT_NS}">
      <office:body><office:text>
        <text:p>Repeated text</text:p><text:p>Repeated text</text:p>
      </office:text></office:body>
    </office:document-content>"""
    _create_odf(template, {"content.xml": content})
    with template.open("rb") as input_file, po_path.open("wb") as output_file:
        odf2po.convertodf(input_file, output_file, None)

    with po_path.open("rb") as po_file:
        store = po.pofile(po_file)
    units = [unit for unit in store.units if unit.source == "Repeated text"]
    assert len(units) == 2
    assert len({unit.getcontext() for unit in units}) == 2
    for unit in units:
        assert len(unit.getlocations()) == 2
        unit.target = "Repeated translation"
    store.save()

    with (
        po_path.open("rb") as input_file,
        output.open("wb") as output_file,
        template.open("rb") as template_file,
    ):
        po2odf.convertpo(input_file, output_file, template_file)

    with ZipFile(output) as archive:
        text = "".join(
            parse_xml(archive.read("content.xml"), collect_ids=False).itertext()
        )
        assert text.count("Repeated translation") == 2
