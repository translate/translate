"""Tests for XLIFF 2.0 with various content patterns."""

import pytest

from translate.storage import xliff2


class TestXLIFF2Patterns:
    """Test XLIFF 2.0 with various content patterns."""

    def test_escaped_inline_tags(self):
        """
        Test escaped inline tags in content.

        This tests escaped inline tags like &lt;1&gt;text&lt;/1&gt; in content.
        """
        xliff_content = b"""<?xml version="1.0" encoding="UTF-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:2.0" version="2.0" srcLang="en" trgLang="en">
  <file id="translation">
    <unit id="unit1">
      <segment>
        <source>Click &lt;1&gt;here&lt;/1&gt; to continue.</source>
        <target>Click &lt;1&gt;here&lt;/1&gt; to continue.</target>
      </segment>
    </unit>
  </file>
</xliff>"""

        store = xliff2.xliff2file.parsestring(xliff_content)
        assert len(store.units) == 1
        assert store.units[0].getid() == "unit1"
        assert "here" in store.units[0].source
        assert "<1>" in store.units[0].source  # Escaped tags become part of text

        # Test modification and serialization
        store.units[0].target = "Modified text"
        serialized = bytes(store)

        # Verify modification preserved
        store2 = xliff2.xliff2file.parsestring(serialized)
        assert store2.units[0].target == "Modified text"

    def test_simple_source_target_pairs(self):
        """
        Test simple source/target pairs.

        This tests basic source and target text with language codes.
        """
        xliff_content = b"""<?xml version="1.0" encoding="UTF-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:2.0" version="2.0" srcLang="en-US" trgLang="fr">
  <file id="f1">
    <unit id="1">
      <segment>
        <source>Welcome</source>
        <target>Bienvenue</target>
      </segment>
    </unit>
  </file>
</xliff>"""

        store = xliff2.xliff2file.parsestring(xliff_content)
        assert len(store.units) == 1
        assert store.units[0].source == "Welcome"
        assert store.units[0].target == "Bienvenue"

        # Test round-trip
        serialized = bytes(store)
        store2 = xliff2.xliff2file.parsestring(serialized)
        assert store2.units[0].source == "Welcome"
        assert store2.units[0].target == "Bienvenue"

    def test_malformed_xml_declaration(self):
        """
        Test that malformed XML declarations are handled correctly.

        Tests that files with malformed XML declarations (missing quotes or
        spaces) fail gracefully with a clear error.
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

    def test_variable_placeholders(self):
        """
        Test variable placeholders in content.

        Tests that variable placeholders like {variable} are preserved.
        """
        xliff_content = b"""<?xml version="1.0" encoding="UTF-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:2.0" version="2.0" srcLang="en">
  <file>
    <unit id="greeting" name="greeting">
      <segment>
        <source>Hello {name}</source>
      </segment>
    </unit>
  </file>
</xliff>"""

        store = xliff2.xliff2file.parsestring(xliff_content)
        assert len(store.units) == 1
        assert store.units[0].getid() == "greeting"
        assert "{name}" in store.units[0].source

        # Test serialization
        serialized = bytes(store)
        store2 = xliff2.xliff2file.parsestring(serialized)
        assert "{name}" in store2.units[0].source
