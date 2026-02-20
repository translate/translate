"""Tests for converting WiX Localization (.wxl) files to/from Gettext PO."""

from io import BytesIO

from lxml import etree

from translate.convert import po2wxl, wxl2po


class TestWxl2PO:
    WXL_V4 = b"""<?xml version="1.0" encoding="utf-8"?>
<WixLocalization xmlns="http://wixtoolset.org/schemas/v4/wxl" Culture="de-de" Codepage="1252">
  <String Id="WixUIBack" Overridable="yes" Value="Zurueck" />
  <String Id="WixUICancel" Overridable="yes" Value="Abbrechen" />
</WixLocalization>
"""

    WXL_V3 = b"""<?xml version="1.0" encoding="utf-8"?>
<WixLocalization xmlns="http://schemas.microsoft.com/wix/2006/localization" Culture="pt-br" Codepage="1252">
  <String Id="WixUIBack">Voltar</String>
  <String Id="WixUICancel">Cancelar</String>
</WixLocalization>
"""

    WXL_EN = b"""<?xml version="1.0" encoding="utf-8"?>
<WixLocalization xmlns="http://wixtoolset.org/schemas/v4/wxl" Culture="en-us">
  <String Id="WixUIBack" Value="Back" />
  <String Id="WixUICancel" Value="Cancel" />
  <String Id="WixUINext" Value="Next" />
</WixLocalization>
"""

    @staticmethod
    def _convert(input_bytes):
        inputfile = BytesIO(input_bytes)
        outputfile = BytesIO()
        converter = wxl2po.wxl2po(inputfile, outputfile)
        result = converter.run()
        return result, converter.target_store, outputfile

    @staticmethod
    def _convert_with_template(input_bytes, template_bytes):
        inputfile = BytesIO(input_bytes)
        outputfile = BytesIO()
        templatefile = BytesIO(template_bytes)
        converter = wxl2po.wxl2po(inputfile, outputfile, templatefile)
        result = converter.run()
        return result, converter.target_store, outputfile

    def test_convert_v4_value_attribute(self) -> None:
        """WiX v4 Value-attribute strings are converted to PO units."""
        result, store, _ = self._convert(self.WXL_V4)
        assert result == 1
        # skip header
        units = [u for u in store.units if not u.isheader()]
        assert len(units) == 2
        assert store.findunit("WixUIBack") is not None
        assert store.findunit("WixUIBack").target == "Zurueck"

    def test_convert_v3_text_content(self) -> None:
        """WiX v3 text-content strings are converted to PO units."""
        result, store, _ = self._convert(self.WXL_V3)
        assert result == 1
        units = [u for u in store.units if not u.isheader()]
        assert len(units) == 2
        assert store.findunit("WixUIBack").target == "Voltar"
        assert store.findunit("WixUICancel").target == "Cancelar"

    def test_empty_file_returns_zero(self) -> None:
        """An empty WXL file yields a return code of 0."""
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<WixLocalization xmlns="http://wixtoolset.org/schemas/v4/wxl" Culture="de-de" />
"""
        result, _, _ = self._convert(content)
        assert result == 0

    def test_output_contains_po_header(self) -> None:
        """Converted PO output contains the standard PO header."""
        _, _, outputfile = self._convert(self.WXL_V4)
        output = outputfile.getvalue().decode("utf-8")
        assert "Project-Id-Version" in output
        assert 'msgid "WixUIBack"' in output

    def test_merge_with_template(self) -> None:
        """With a template, msgid comes from template and msgstr from input."""
        wxl_de = b"""<?xml version="1.0" encoding="utf-8"?>
<WixLocalization xmlns="http://wixtoolset.org/schemas/v4/wxl" Culture="de-de">
  <String Id="WixUIBack" Value="Zurueck" />
  <String Id="WixUICancel" Value="Abbrechen" />
</WixLocalization>
"""
        result, store, _ = self._convert_with_template(wxl_de, self.WXL_EN)
        assert result == 1
        units = [u for u in store.units if not u.isheader()]
        # All template keys appear in output
        assert len(units) == 3
        back_unit = store.findunit("WixUIBack")
        assert back_unit is not None
        assert back_unit.target == "Zurueck"
        cancel_unit = store.findunit("WixUICancel")
        assert cancel_unit is not None
        assert cancel_unit.target == "Abbrechen"

    def test_merge_template_missing_translation(self) -> None:
        """Keys in template but absent in input appear with empty msgstr."""
        wxl_de = b"""<?xml version="1.0" encoding="utf-8"?>
<WixLocalization xmlns="http://wixtoolset.org/schemas/v4/wxl" Culture="de-de">
  <String Id="WixUIBack" Value="Zurueck" />
</WixLocalization>
"""
        result, store, _ = self._convert_with_template(wxl_de, self.WXL_EN)
        assert result == 1
        units = [u for u in store.units if not u.isheader()]
        # All three template keys appear
        assert len(units) == 3
        # WixUINext has no translation in input → empty msgstr
        next_unit = store.findunit("WixUINext")
        assert next_unit is not None
        assert next_unit.target == ""

    def test_merge_v3_template(self) -> None:
        """Template handling works with WiX v3 text-content format."""
        wxl_en_v3 = b"""<?xml version="1.0" encoding="utf-8"?>
<WixLocalization xmlns="http://schemas.microsoft.com/wix/2006/localization" Culture="en-us">
  <String Id="WixUIBack">Back</String>
  <String Id="WixUICancel">Cancel</String>
</WixLocalization>
"""
        result, store, _ = self._convert_with_template(self.WXL_V3, wxl_en_v3)
        assert result == 1
        back_unit = store.findunit("WixUIBack")
        assert back_unit is not None
        assert back_unit.target == "Voltar"
        cancel_unit = store.findunit("WixUICancel")
        assert cancel_unit is not None
        assert cancel_unit.target == "Cancelar"


class TestPO2WXL:
    PO_SOURCE = b"""
msgid "WixUIBack"
msgstr "Voltar"

msgid "WixUICancel"
msgstr "Cancelar"
"""

    @staticmethod
    def _convert(po_bytes, template_bytes=None):
        inputfile = BytesIO(po_bytes)
        outputfile = BytesIO()
        templatefile = BytesIO(template_bytes) if template_bytes else None
        converter = po2wxl.po2wxl(inputfile, outputfile, templatefile)
        result = converter.run()
        return result, converter.target_store, outputfile

    def _convert_to_string(self, po_bytes, template_bytes=None):
        _, _, outputfile = self._convert(po_bytes, template_bytes)
        return outputfile.getvalue().decode("utf-8")

    def test_basic_conversion(self) -> None:
        """PO units are written as WXL String elements."""
        output = self._convert_to_string(self.PO_SOURCE)
        assert "WixUIBack" in output
        assert "Voltar" in output
        assert "WixUICancel" in output
        assert "Cancelar" in output

    def test_output_is_valid_xml(self) -> None:
        """po2wxl output is valid XML."""
        output_bytes = BytesIO(self.PO_SOURCE)
        out = BytesIO()
        po2wxl.po2wxl(output_bytes, out).run()
        # Should not raise
        etree.fromstring(out.getvalue())

    def test_with_template(self) -> None:
        """When a template is provided, extra attributes are preserved."""
        template = b"""<?xml version="1.0" encoding="utf-8"?>
<WixLocalization xmlns="http://wixtoolset.org/schemas/v4/wxl" Culture="de-de" Codepage="1252">
  <String Id="WixUIBack" Overridable="yes" Value="" />
  <String Id="WixUICancel" Overridable="yes" Value="" />
</WixLocalization>
"""
        po = b"""
msgid "WixUIBack"
msgstr "Zurueck"

msgid "WixUICancel"
msgstr "Abbrechen"
"""
        output = self._convert_to_string(po, template)
        assert 'Overridable="yes"' in output
        assert "Zurueck" in output
        assert "Abbrechen" in output

    def test_culture_from_template(self) -> None:
        """Culture attribute is preserved from the template."""
        template = b"""<?xml version="1.0" encoding="utf-8"?>
<WixLocalization xmlns="http://wixtoolset.org/schemas/v4/wxl" Culture="cs-cz">
  <String Id="Key" Value="" />
</WixLocalization>
"""
        po = b"""
msgid "Key"
msgstr "Hodnota"
"""
        output = self._convert_to_string(po, template)
        assert 'Culture="cs-cz"' in output

    def test_empty_po_returns_zero(self) -> None:
        """An empty PO file yields a return code of 0."""
        result, _, _ = self._convert(b"")
        assert result == 0
