#
# Copyright 2025 Translate Authors
#
# This file is part of translate.
#
# translate is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# translate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""Tests for WiX Localization (.wxl) storage."""

from io import BytesIO

from lxml import etree

from translate.storage import wxl

from . import test_monolingual


class TestWxlUnit(test_monolingual.TestMonolingualUnit):
    UnitClass = wxl.WxlUnit


class TestWxlFile(test_monolingual.TestMonolingualStore):
    StoreClass = wxl.WxlFile

    @staticmethod
    def _store_to_string(store):
        out = BytesIO()
        store.serialize(out)
        return out.getvalue().decode("utf-8")

    @staticmethod
    def _parse(content: bytes) -> wxl.WxlFile:
        return wxl.WxlFile(BytesIO(content))

    # ------------------------------------------------------------------
    # Parsing tests

    def test_parse_v4_value_attribute(self) -> None:
        """Parse WiX v4 String elements using the Value attribute."""
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<WixLocalization xmlns="http://wixtoolset.org/schemas/v4/wxl" Culture="de-de" Codepage="1252">
  <String Id="WixUIBack" Overridable="yes" Value="Zurueck" />
  <String Id="WixUICancel" Value="Abbrechen" />
</WixLocalization>
"""
        store = self._parse(content)
        assert len(store.units) == 2
        unit = store.findid("WixUIBack")
        assert unit is not None
        assert unit.target == "Zurueck"
        assert unit.getid() == "WixUIBack"

    def test_parse_v3_text_content(self) -> None:
        """Parse WiX v3 String elements using text content."""
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<WixLocalization xmlns="http://schemas.microsoft.com/wix/2006/localization" Culture="pt-br" Codepage="1252">
  <String Id="WixUIBack" Overridable="yes">Voltar</String>
  <String Id="WixUICancel">Cancelar</String>
</WixLocalization>
"""
        store = self._parse(content)
        assert len(store.units) == 2
        assert store.findid("WixUIBack").target == "Voltar"
        assert store.findid("WixUICancel").target == "Cancelar"

    def test_parse_ui_element_with_text(self) -> None:
        """UI elements with a Text attribute are exposed as translatable units."""
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<WixLocalization xmlns="http://wixtoolset.org/schemas/v4/wxl" Culture="de-de">
  <String Id="Caption" Value="Ueberschrift" />
  <UI Id="WelcomeDlg_Cancel" Text="Abbrechen" />
</WixLocalization>
"""
        store = self._parse(content)
        assert len(store.units) == 2
        ui_unit = store.findid("WelcomeDlg_Cancel")
        assert ui_unit is not None
        assert ui_unit.target == "Abbrechen"

    def test_parse_ui_element_without_text_preserved(self) -> None:
        """UI elements without a Text attribute are preserved but not exposed as units."""
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<WixLocalization xmlns="http://wixtoolset.org/schemas/v4/wxl" Culture="pt-br" Codepage="1252">
  <UI Dialog="ErrorDlg" Control="R" Width="80" />
  <String Id="WixUIBack" Overridable="yes">Voltar</String>
</WixLocalization>
"""
        store = self._parse(content)
        assert len(store.units) == 1
        assert store.findid("WixUIBack") is not None
        # Non-translatable UI element must not be exposed as a unit
        assert store.findid("") is None

        # But it must be serialised in the output
        serialized = self._store_to_string(store)
        assert "ErrorDlg" in serialized
        assert 'Width="80"' in serialized

    def test_culture_attribute(self) -> None:
        """Culture is read from and written to the root element."""
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<WixLocalization xmlns="http://wixtoolset.org/schemas/v4/wxl" Culture="cs-cz">
  <String Id="Key">Value</String>
</WixLocalization>
"""
        store = self._parse(content)
        assert store.culture == "cs-cz"

        store.culture = "sk-sk"
        serialized = self._store_to_string(store)
        assert 'Culture="sk-sk"' in serialized

    def test_codepage_attribute(self) -> None:
        """Codepage is read from and written to the root element."""
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<WixLocalization xmlns="http://wixtoolset.org/schemas/v4/wxl" Codepage="1250">
  <String Id="Key">Value</String>
</WixLocalization>
"""
        store = self._parse(content)
        assert store.codepage == "1250"

    def test_encoding_detection_no_xml_declaration(self) -> None:
        """Files without an XML declaration default to windows-1252 parsing."""
        # U+00DF (LATIN SMALL LETTER SHARP S) is 0xDF in windows-1252
        content = (
            b"<WixLocalization"
            b' xmlns="http://wixtoolset.org/schemas/v4/wxl"'
            b' Culture="de-de" Codepage="1252">'
            b'<String Id="test">Stra\xdfe</String>'
            b"</WixLocalization>"
        )
        store = self._parse(content)
        assert len(store.units) == 1
        assert store.findid("test").target == "Straße"

    def test_codepage_utf8_variants(self) -> None:
        """Both '65001' and 'utf-8' are recognised as UTF-8."""
        assert wxl._codepage_to_encoding("65001") == "utf-8"
        assert wxl._codepage_to_encoding("utf-8") == "utf-8"
        assert wxl._codepage_to_encoding("utf8") == "utf-8"

    # ------------------------------------------------------------------
    # Serialisation tests

    def test_serialize_preserves_extra_attributes(self) -> None:
        """Extra attributes on String elements survive a round-trip."""
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<WixLocalization xmlns="http://wixtoolset.org/schemas/v4/wxl" Culture="de-de" Codepage="1252">
  <String Id="WixUIBack" Overridable="yes" Value="Zurueck" />
</WixLocalization>
"""
        store = self._parse(content)
        serialized = self._store_to_string(store)
        assert 'Overridable="yes"' in serialized

    def test_serialize_value_attribute_style(self) -> None:
        """Value-attribute style is preserved on round-trip."""
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<WixLocalization xmlns="http://wixtoolset.org/schemas/v4/wxl" Culture="de-de">
  <String Id="Caption" Value="Test" />
</WixLocalization>
"""
        store = self._parse(content)
        unit = store.findid("Caption")
        unit.target = "Ueberschrift"
        serialized = self._store_to_string(store)
        assert 'Value="Ueberschrift"' in serialized

    def test_serialize_text_content_style(self) -> None:
        """Text-content style is preserved on round-trip."""
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<WixLocalization xmlns="http://wixtoolset.org/schemas/v4/wxl" Culture="de-de">
  <String Id="Caption">Test</String>
</WixLocalization>
"""
        store = self._parse(content)
        unit = store.findid("Caption")
        unit.target = "Ueberschrift"
        serialized = self._store_to_string(store)
        assert '<String Id="Caption">Ueberschrift</String>' in serialized

    def test_new_empty_store(self) -> None:
        """A freshly created store serialises with the WiX v4 namespace."""
        store = wxl.WxlFile()
        store.culture = "cs-cz"
        unit = wxl.WxlUnit("TestKey")
        unit.target = "Test Value"
        store.addunit(unit)
        serialized = self._store_to_string(store)
        assert "http://wixtoolset.org/schemas/v4/wxl" in serialized
        assert 'Culture="cs-cz"' in serialized
        assert "TestKey" in serialized
        assert "Test Value" in serialized

    def test_comments_preserved(self) -> None:
        """XML comments are preserved on round-trip."""
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<!-- This is a comment -->
<WixLocalization xmlns="http://wixtoolset.org/schemas/v4/wxl" Culture="de-de">
  <String Id="Caption">Test</String>
</WixLocalization>
"""
        store = self._parse(content)
        serialized = self._store_to_string(store)
        assert "This is a comment" in serialized

    # ------------------------------------------------------------------
    # Unit tests

    def test_unit_getid_setid(self) -> None:
        unit = wxl.WxlUnit("MyKey")
        assert unit.getid() == "MyKey"
        unit.setid("NewKey")
        assert unit.getid() == "NewKey"

    def test_unit_target_text_content(self) -> None:
        unit = wxl.WxlUnit("Key")
        unit.target = "Hello"
        assert unit.target == "Hello"
        assert unit.xmlelement.text == "Hello"

    def test_unit_target_value_attribute(self) -> None:
        """Setting target on a Value-attribute element updates the attribute."""
        element = etree.fromstring(
            '<String Id="Key" Value="Old" xmlns="http://wixtoolset.org/schemas/v4/wxl"/>'
        )
        unit = wxl.WxlUnit.createfromxmlElement(element)
        unit.target = "New"
        assert unit.target == "New"
        assert unit.xmlelement.get("Value") == "New"

    def test_unit_source_equals_id(self) -> None:
        unit = wxl.WxlUnit("SomeId")
        assert unit.source == "SomeId"
