"""Tests for preserving file and group structure when adding units."""

from translate.storage import xliff


class TestMultipleFilesAndGroups:
    """Test preservation of file and group structure."""

    def test_preserve_groups_when_adding_units(self):
        """Test that groups are preserved when adding units from one store to another."""
        source_xliff = b"""<?xml version="1.0" encoding="utf-8"?>
<xliff version="1.1" xmlns="urn:oasis:names:tc:xliff:document:1.1">
    <file original="file1.txt" source-language="en" datatype="plaintext">
        <body>
            <group id="group1" restype="x-gettext-domain">
                <trans-unit id="hello">
                    <source>Hello</source>
                </trans-unit>
            </group>
            <group id="group2">
                <trans-unit id="world">
                    <source>World</source>
                </trans-unit>
            </group>
        </body>
    </file>
</xliff>"""

        source = xliff.xlifffile.parsestring(source_xliff)
        assert len(source.units) == 2

        # Add units to a new translation store
        translation = xliff.xlifffile()
        translation.sourcelanguage = "en"
        translation.targetlanguage = "fr"

        for unit in source.units:
            translation.addunit(unit)

        # Verify groups are preserved
        serialized = bytes(translation)
        assert b"<group" in serialized
        assert b'id="group1"' in serialized
        assert b'id="group2"' in serialized
        assert b'restype="x-gettext-domain"' in serialized

    def test_preserve_multiple_files_and_groups(self):
        """Test that both files and groups are preserved."""
        source_xliff = b"""<?xml version="1.0" encoding="utf-8"?>
<xliff version="1.1" xmlns="urn:oasis:names:tc:xliff:document:1.1">
    <file original="file1.txt" source-language="en" datatype="plaintext">
        <body>
            <group id="group1">
                <trans-unit id="hello">
                    <source>Hello</source>
                </trans-unit>
            </group>
        </body>
    </file>
    <file original="file2.txt" source-language="en" datatype="plaintext">
        <body>
            <group id="group2">
                <trans-unit id="foo">
                    <source>Foo</source>
                </trans-unit>
            </group>
        </body>
    </file>
</xliff>"""

        source = xliff.xlifffile.parsestring(source_xliff)
        assert len(source.units) == 2

        # Add units to a new translation store
        translation = xliff.xlifffile()
        translation.sourcelanguage = "en"
        translation.targetlanguage = "fr"

        for unit in source.units:
            translation.addunit(unit)

        # Verify both files and groups are preserved
        assert translation.getfilenames() == ["file1.txt", "file2.txt"]
        serialized = bytes(translation)
        assert b"<group" in serialized
        assert b'id="group1"' in serialized
        assert b'id="group2"' in serialized

    def test_add_unit_to_existing_group(self):
        """Test that new units are added to existing groups when appropriate."""
        # Start with translation that has one group
        translation_xliff = b"""<?xml version="1.0" encoding="utf-8"?>
<xliff version="1.1" xmlns="urn:oasis:names:tc:xliff:document:1.1">
    <file original="file1.txt" source-language="en" datatype="plaintext" target-language="fr">
        <body>
            <group id="group1">
                <trans-unit id="hello">
                    <source>Hello</source>
                    <target>Bonjour</target>
                </trans-unit>
            </group>
        </body>
    </file>
</xliff>"""

        translation = xliff.xlifffile.parsestring(translation_xliff)

        # Add a new unit from a source that has the same group
        source_xliff = b"""<?xml version="1.0" encoding="utf-8"?>
<xliff version="1.1" xmlns="urn:oasis:names:tc:xliff:document:1.1">
    <file original="file1.txt" source-language="en" datatype="plaintext">
        <body>
            <group id="group1">
                <trans-unit id="world">
                    <source>World</source>
                </trans-unit>
            </group>
        </body>
    </file>
</xliff>"""

        source = xliff.xlifffile.parsestring(source_xliff)
        new_unit = source.units[0]

        # Add the new unit
        translation.addunit(new_unit)

        # Verify the new unit is in the same group
        assert len(translation.units) == 2
        serialized = bytes(translation)

        # Both units should be in group1
        translation_check = xliff.xlifffile.parsestring(serialized)
        for unit in translation_check.units:
            parent = unit.xmlelement.getparent()
            assert "group" in parent.tag
            assert parent.get("id") == "group1"

    def test_preserve_group_attributes(self):
        """Test that all group attributes are preserved."""
        source_xliff = b"""<?xml version="1.0" encoding="utf-8"?>
<xliff version="1.1" xmlns="urn:oasis:names:tc:xliff:document:1.1">
    <file original="file1.txt" source-language="en" datatype="plaintext">
        <body>
            <group id="mygroup" restype="x-gettext-domain" resname="mydomain">
                <trans-unit id="hello">
                    <source>Hello</source>
                </trans-unit>
            </group>
        </body>
    </file>
</xliff>"""

        source = xliff.xlifffile.parsestring(source_xliff)
        translation = xliff.xlifffile()
        translation.sourcelanguage = "en"
        translation.targetlanguage = "fr"

        translation.addunit(source.units[0])

        serialized = bytes(translation)
        assert b'id="mygroup"' in serialized
        assert b'restype="x-gettext-domain"' in serialized
        assert b'resname="mydomain"' in serialized

    def test_units_without_groups_added_to_body(self):
        """Test that units without groups are added directly to body."""
        source_xliff = b"""<?xml version="1.0" encoding="utf-8"?>
<xliff version="1.1" xmlns="urn:oasis:names:tc:xliff:document:1.1">
    <file original="file1.txt" source-language="en" datatype="plaintext">
        <body>
            <trans-unit id="hello">
                <source>Hello</source>
            </trans-unit>
        </body>
    </file>
</xliff>"""

        source = xliff.xlifffile.parsestring(source_xliff)
        translation = xliff.xlifffile()
        translation.sourcelanguage = "en"
        translation.targetlanguage = "fr"

        translation.addunit(source.units[0])

        # Verify unit is directly in body, not in a group
        translation_check = xliff.xlifffile.parsestring(bytes(translation))
        unit = translation_check.units[0]
        parent = unit.xmlelement.getparent()
        assert "body" in parent.tag
        assert "group" not in parent.tag

    def test_mixed_groups_and_body(self):
        """Test files with both grouped and non-grouped units."""
        source_xliff = b"""<?xml version="1.0" encoding="utf-8"?>
<xliff version="1.1" xmlns="urn:oasis:names:tc:xliff:document:1.1">
    <file original="file1.txt" source-language="en" datatype="plaintext">
        <body>
            <group id="group1">
                <trans-unit id="hello">
                    <source>Hello</source>
                </trans-unit>
            </group>
            <trans-unit id="world">
                <source>World</source>
            </trans-unit>
        </body>
    </file>
</xliff>"""

        source = xliff.xlifffile.parsestring(source_xliff)
        translation = xliff.xlifffile()
        translation.sourcelanguage = "en"
        translation.targetlanguage = "fr"

        for unit in source.units:
            translation.addunit(unit)

        # Verify structure is preserved
        translation_check = xliff.xlifffile.parsestring(bytes(translation))
        assert len(translation_check.units) == 2

        # First unit should be in group
        parent1 = translation_check.units[0].xmlelement.getparent()
        assert "group" in parent1.tag

        # Second unit should be directly in body
        parent2 = translation_check.units[1].xmlelement.getparent()
        assert "body" in parent2.tag
