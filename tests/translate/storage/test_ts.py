from io import BytesIO, StringIO

from translate.storage import ts


class TestTS:
    def test_construct(self) -> None:
        tsfile = ts.QtTsParser()
        tsfile.addtranslation("ryan", "Bread", "Brood", "Wit", createifmissing=True)

    def test_rejects_entity_expansion(self) -> None:
        parser_input = BytesIO(
            b"""<!DOCTYPE TS [
<!ENTITY a0 "ha">
<!ENTITY a1 "&a0;&a0;&a0;&a0;&a0;&a0;&a0;&a0;&a0;&a0;">
<!ENTITY a2 "&a1;&a1;&a1;&a1;&a1;&a1;&a1;&a1;&a1;&a1;">
]>
<TS>
  <context>
    <name>ctx</name>
    <message>
      <source>&a2;</source>
      <translation>done</translation>
    </message>
  </context>
</TS>"""
        )

        # libxml2 may either preserve the unresolved entity node or reject the
        # nested entity definitions as a loop, depending on the build/version.
        # Both outcomes are acceptable here because neither expands the entity.
        try:
            tsfile = ts.QtTsParser(parser_input)
        except ts.etree.XMLSyntaxError:
            return

        message = tsfile.getmessagenodes("ctx")[0]
        source_node = message.find("source")

        assert tsfile.getmessagesource(message) == ""
        assert source_node is not None
        assert len(source_node) == 1
        assert source_node[0].tag is ts.etree.Entity

    def test_preserves_doctype(self) -> None:
        tsfile = ts.QtTsParser()

        assert "<!DOCTYPE TS>" in tsfile.getxml()

    def test_roundtrip_without_doctype_does_not_add_one(self) -> None:
        tsfile = ts.QtTsParser(
            """<TS>
  <context>
    <name>ctx</name>
    <message>
      <source>Hello</source>
      <translation>Hi</translation>
    </message>
  </context>
</TS>"""
        )

        assert "<!DOCTYPE TS>" not in tsfile.getxml()

    def test_supports_path_input(self, tmp_path) -> None:
        ts_path = tmp_path / "sample.ts"
        ts_path.write_text(
            """<!DOCTYPE TS>
<TS>
  <context>
    <name>ctx</name>
    <message>
      <source>Hello</source>
      <translation>Hi</translation>
    </message>
  </context>
</TS>""",
            encoding="utf-8",
        )

        tsfile = ts.QtTsParser(str(ts_path))

        assert tsfile.filename == str(ts_path)
        assert tsfile.getmessagesource(tsfile.getmessagenodes("ctx")[0]) == "Hello"

    def test_supports_text_stream_input_with_encoding_declaration(self) -> None:
        parser_input = StringIO(
            """<?xml version="1.0" encoding="ISO-8859-1"?>
<!DOCTYPE TS>
<TS>
  <context>
    <name>ctx</name>
    <message>
      <source>é</source>
      <translation>é</translation>
    </message>
  </context>
</TS>"""
        )

        tsfile = ts.QtTsParser(parser_input)

        assert tsfile.getmessagesource(tsfile.getmessagenodes("ctx")[0]) == "é"

    def test_normalize_text_input_strips_tab_heavy_encoding_declaration(self) -> None:
        content = (
            '<?xml\tversion="1.0"\t\t\tencoding="ISO-8859-1"\tstandalone="yes"?><TS/>'
        )

        normalized = ts.QtTsParser._normalize_text_input(content)

        assert 'encoding="ISO-8859-1"' not in normalized
        assert normalized == '<?xml\tversion="1.0"\tstandalone="yes"?><TS/>'

    def test_normalize_text_input_ignores_repeated_encoding_like_text(self) -> None:
        content = '<?xml version="1.0"?>' + ('\tencoding="' * 64)

        normalized = ts.QtTsParser._normalize_text_input(content)

        assert normalized == content

    def test_normalize_text_input_preserves_other_xml_attributes(self) -> None:
        content = (
            "<?xml   version='1.0'\n"
            "\tencoding = 'ISO-8859-1'\n"
            ' standalone = "yes"?>\n<TS/>'
        )

        normalized = ts.QtTsParser._normalize_text_input(content)

        assert normalized == "<?xml   version='1.0'\n standalone = \"yes\"?>\n<TS/>"
