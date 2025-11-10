"""Tests for XLIFF 2.0 with real-world files."""

import pytest

from translate.storage import xliff2


class TestXLIFF2RealWorld:
    """Test XLIFF 2.0 with patterns from real-world repositories."""

    def test_locize_github_integration_pattern(self):
        """
        Test pattern from Locize GitHub Integration repository.

        This tests escaped inline tags like &lt;1&gt;text&lt;/1&gt; in content.
        """
        xliff_content = b"""<?xml version="1.0" encoding="UTF-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:2.0" version="2.0" srcLang="en" trgLang="en">
  <file id="translation">
    <unit id="description.part1">
      <segment>
        <source>To get started, edit &lt;1&gt;src/App.js&lt;/1&gt; and save to reload.</source>
        <target>To get started, edit &lt;1&gt;src/App.js&lt;/1&gt; and save to reload.</target>
      </segment>
    </unit>
  </file>
</xliff>"""

        store = xliff2.xliff2file.parsestring(xliff_content)
        assert len(store.units) == 1
        assert store.units[0].getid() == "description.part1"
        assert "src/App.js" in store.units[0].source
        assert "<1>" in store.units[0].source  # Escaped tags become part of text

        # Test modification and serialization
        store.units[0].target = "Modified text"
        serialized = bytes(store)

        # Verify modification preserved
        store2 = xliff2.xliff2file.parsestring(serialized)
        assert store2.units[0].target == "Modified text"

    def test_gists_pattern(self):
        """
        Test pattern from academic-resources/gists repository.

        This tests simple source/target pairs.
        """
        xliff_content = b"""<?xml version="1.0" encoding="UTF-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:2.0" version="2.0" srcLang="en-US" trgLang="fr">
  <file id="f1">
    <unit id="1">
      <segment>
        <source>Hello my friend</source>
        <target>Bonjour, mon ami</target>
      </segment>
    </unit>
  </file>
</xliff>"""

        store = xliff2.xliff2file.parsestring(xliff_content)
        assert len(store.units) == 1
        assert store.units[0].source == "Hello my friend"
        assert store.units[0].target == "Bonjour, mon ami"

        # Test round-trip
        serialized = bytes(store)
        store2 = xliff2.xliff2file.parsestring(serialized)
        assert store2.units[0].source == "Hello my friend"
        assert store2.units[0].target == "Bonjour, mon ami"

    def test_malformed_xml_declaration(self):
        """
        Test that malformed XML declarations are handled correctly.

        Some repositories (e.g., intl_translation_format_experiments) have
        malformed XML declarations with missing quotes or spaces.
        This should fail gracefully with a clear error.
        """
        # Missing closing quote on version attribute
        malformed_content = b"""<?xml version="1.0 encoding="UTF-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:2.0" version="2.0" srcLang="en">
  <file>
    <unit id="test">
      <segment>
        <source>Test</source>
      </segment>
    </unit>
  </file>
</xliff>"""

        # This should raise an XML parsing error
        with pytest.raises(Exception) as exc_info:
            xliff2.xliff2file.parsestring(malformed_content)

        # The error should be about XML syntax
        assert "XML" in str(exc_info.value) or "String" in str(exc_info.value)

    def test_inline_elements_with_ids(self):
        """
        Test inline elements with id attributes.

        Pattern from intl_translation_format_experiments after fixing XML.
        """
        xliff_content = b"""<?xml version="1.0" encoding="UTF-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:2.0" version="2.0" srcLang="en">
  <file>
    <unit id="variable" name="variable">
      <segment>
        <source>Hello {variable}</source>
      </segment>
    </unit>
  </file>
</xliff>"""

        store = xliff2.xliff2file.parsestring(xliff_content)
        assert len(store.units) == 1
        assert store.units[0].getid() == "variable"
        assert "{variable}" in store.units[0].source

        # Test serialization
        serialized = bytes(store)
        store2 = xliff2.xliff2file.parsestring(serialized)
        assert "{variable}" in store2.units[0].source
