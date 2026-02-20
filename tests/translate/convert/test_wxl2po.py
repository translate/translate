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

    def test_merge_non_translatable_ui_excluded(self) -> None:
        """Non-translatable UI elements (no Text attr) are excluded from PO output."""
        template = b"""<?xml version="1.0" encoding="utf-8"?>
<WixLocalization xmlns="http://wixtoolset.org/schemas/v4/wxl" Culture="en-us">
  <String Id="WixUIBack" Value="Back" />
  <UI Id="WixUI_Mondo" />
  <String Id="WixUINext" Value="Next" />
</WixLocalization>
"""
        wxl_de = b"""<?xml version="1.0" encoding="utf-8"?>
<WixLocalization xmlns="http://wixtoolset.org/schemas/v4/wxl" Culture="de-de">
  <String Id="WixUIBack" Value="Zurueck" />
  <String Id="WixUINext" Value="Weiter" />
</WixLocalization>
"""
        result, store, outputfile = self._convert_with_template(wxl_de, template)
        assert result == 1
        units = [u for u in store.units if not u.isheader()]
        # WixUI_Mondo (non-translatable) must not appear as a PO unit
        assert len(units) == 2
        po_text = outputfile.getvalue().decode("utf-8")
        assert "WixUI_Mondo" not in po_text
        assert 'msgid "WixUIBack"' in po_text
        assert 'msgstr "Zurueck"' in po_text

    def test_merge_xml_comments_excluded(self) -> None:
        """XML comments in the WXL template are excluded from PO output."""
        template = b"""<?xml version="1.0" encoding="utf-8"?>
<WixLocalization xmlns="http://wixtoolset.org/schemas/v4/wxl" Culture="en-us">
  <!-- Buttons -->
  <String Id="WixUIBack" Value="Back" />
  <!-- Navigation -->
  <String Id="WixUINext" Value="Next" />
</WixLocalization>
"""
        wxl_de = b"""<?xml version="1.0" encoding="utf-8"?>
<WixLocalization xmlns="http://wixtoolset.org/schemas/v4/wxl" Culture="de-de">
  <String Id="WixUIBack" Value="Zurueck" />
  <String Id="WixUINext" Value="Weiter" />
</WixLocalization>
"""
        result, _store, outputfile = self._convert_with_template(wxl_de, template)
        assert result == 1
        po_text = outputfile.getvalue().decode("utf-8")
        assert "Buttons" not in po_text
        assert "Navigation" not in po_text
        assert 'msgid "WixUIBack"' in po_text
        assert 'msgstr "Zurueck"' in po_text
        assert 'msgid "WixUINext"' in po_text
        assert 'msgstr "Weiter"' in po_text

    def test_merge_translatable_ui_with_text_included(self) -> None:
        """UI elements with a Text attribute are treated as translatable."""
        template = b"""<?xml version="1.0" encoding="utf-8"?>
<WixLocalization xmlns="http://wixtoolset.org/schemas/v4/wxl" Culture="en-us">
  <UI Id="WixUIInstallTitle" Text="Installation" />
  <UI Id="WixUI_Mondo" />
</WixLocalization>
"""
        wxl_de = b"""<?xml version="1.0" encoding="utf-8"?>
<WixLocalization xmlns="http://wixtoolset.org/schemas/v4/wxl" Culture="de-de">
  <UI Id="WixUIInstallTitle" Text="Installation DE" />
</WixLocalization>
"""
        result, store, outputfile = self._convert_with_template(wxl_de, template)
        assert result == 1
        units = [u for u in store.units if not u.isheader()]
        # WixUI_Mondo has no Text → not translatable, so only 1 unit
        assert len(units) == 1
        po_text = outputfile.getvalue().decode("utf-8")
        assert 'msgid "WixUIInstallTitle"' in po_text
        assert 'msgstr "Installation DE"' in po_text
        assert "WixUI_Mondo" not in po_text

    def test_no_template_non_translatable_ui_excluded(self) -> None:
        """Without a template, non-translatable UI elements are excluded from PO."""
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<WixLocalization xmlns="http://wixtoolset.org/schemas/v4/wxl" Culture="de-de">
  <!-- A comment -->
  <String Id="WixUIBack" Value="Zurueck" />
  <UI Id="WixUI_Mondo" />
  <UI Id="WixUIInstallTitle" Text="Installation DE" />
</WixLocalization>
"""
        result, store, outputfile = self._convert(content)
        assert result == 1
        units = [u for u in store.units if not u.isheader()]
        assert len(units) == 2
        po_text = outputfile.getvalue().decode("utf-8")
        assert "WixUI_Mondo" not in po_text
        assert "A comment" not in po_text
        assert 'msgid "WixUIBack"' in po_text
        assert 'msgid "WixUIInstallTitle"' in po_text

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

    def test_template_preserves_xml_comments(self) -> None:
        """XML comments in the template are preserved in po2wxl WXL output."""
        template = b"""<?xml version="1.0" encoding="utf-8"?>
<WixLocalization xmlns="http://wixtoolset.org/schemas/v4/wxl" Culture="en-us">
  <!-- Navigation buttons -->
  <String Id="WixUIBack" Value="Back" />
  <!-- Footer -->
  <String Id="WixUINext" Value="Next" />
</WixLocalization>
"""
        po = b"""
msgid "WixUIBack"
msgstr "Zurueck"

msgid "WixUINext"
msgstr "Weiter"
"""
        output = self._convert_to_string(po, template)
        assert "<!-- Navigation buttons -->" in output
        assert "<!-- Footer -->" in output
        assert "Zurueck" in output
        assert "Weiter" in output

    def test_template_preserves_non_translatable_ui(self) -> None:
        """Non-translatable UI elements (no Text attr) are preserved in po2wxl WXL output."""
        template = b"""<?xml version="1.0" encoding="utf-8"?>
<WixLocalization xmlns="http://wixtoolset.org/schemas/v4/wxl" Culture="en-us">
  <String Id="WixUIBack" Value="Back" />
  <UI Id="WixUI_Mondo" />
  <String Id="WixUINext" Value="Next" />
</WixLocalization>
"""
        po = b"""
msgid "WixUIBack"
msgstr "Zurueck"

msgid "WixUINext"
msgstr "Weiter"
"""
        output = self._convert_to_string(po, template)
        assert 'Id="WixUI_Mondo"' in output
        assert "Zurueck" in output
        assert "Weiter" in output

    def test_template_output_matches_structure(self) -> None:
        """po2wxl output with template is structurally identical to template with changed values."""
        template = b"""<?xml version="1.0" encoding="utf-8"?>
<WixLocalization xmlns="http://wixtoolset.org/schemas/v4/wxl" Culture="en-us">
  <!-- Buttons -->
  <String Id="WixUIBack" Value="Back" />
  <UI Id="WixUI_Mondo" />
</WixLocalization>
"""
        po = b"""
msgid "WixUIBack"
msgstr "Zurueck"
"""
        output = self._convert_to_string(po, template)
        # Comment preserved
        assert "<!-- Buttons -->" in output
        # Non-translatable UI preserved
        assert 'Id="WixUI_Mondo"' in output
        # Translation applied
        assert 'Value="Zurueck"' in output
        # Source value replaced (not present)
        assert 'Value="Back"' not in output

    def test_empty_po_returns_zero(self) -> None:
        """An empty PO file yields a return code of 0."""
        result, _, _ = self._convert(b"")
        assert result == 0
