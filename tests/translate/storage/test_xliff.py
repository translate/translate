from lxml import etree

from translate.misc.xml_helpers import setXMLspace
from translate.storage import xliff
from translate.storage.placeables import StringElem
from translate.storage.placeables.xliff import G, X

from . import test_base


class TestXLIFFUnit(test_base.TestTranslationUnit):
    UnitClass = xliff.xliffunit

    def test_markreview(self):
        """Tests if we can mark the unit to need review."""
        unit = self.unit
        # We have to explicitly set the target to nothing, otherwise xliff
        # tests will fail.
        # Can we make it default behavior for the UnitClass?
        unit.target = ""

        unit.addnote("Test note 1", origin="translator")
        unit.addnote("Test note 2", origin="translator")
        original_notes = unit.getnotes(origin="translator")

        assert not unit.isreview()
        unit.markreviewneeded()
        assert unit.isreview()
        unit.markreviewneeded(False)
        assert not unit.isreview()
        assert unit.getnotes(origin="translator") == original_notes
        unit.markreviewneeded(explanation="Double check spelling.")
        assert unit.isreview()
        notes = unit.getnotes(origin="translator")
        assert notes.count("Double check spelling.") == 1

    def test_errors(self):
        """Tests that we can add and retrieve error messages for a unit."""
        unit = self.unit

        assert len(unit.geterrors()) == 0
        unit.adderror(errorname="test1", errortext="Test error message 1.")
        unit.adderror(errorname="test2", errortext="Test error message 2.")
        unit.adderror(errorname="test3", errortext="Test error message 3.")
        assert len(unit.geterrors()) == 3
        assert unit.geterrors()["test1"] == "Test error message 1."
        assert unit.geterrors()["test2"] == "Test error message 2."
        assert unit.geterrors()["test3"] == "Test error message 3."
        unit.adderror(errorname="test1", errortext="New error 1.")
        assert unit.geterrors()["test1"] == "New error 1."

    def test_accepted_control_chars(self):
        """
        Tests we can assign the accepted control chars.

        Source: :wp:`Valid_characters_in_XML#XML_1.0`
        """
        # Unicode Character 'CHARACTER TABULATION' (U+0009)
        self.unit.target = "Een\t"
        assert self.unit.target == "Een\t"
        # Unicode Character 'LINE FEED (LF)' (U+000A)
        self.unit.target = "Een\n"
        assert self.unit.target == "Een\n"
        # Unicode Character 'CARRIAGE RETURN (CR)' (U+000D)
        self.unit.target = "Een\r"
        assert self.unit.target == "Een\r"

    def test_unaccepted_control_chars(self):
        """
        Tests we cannot assign the unaccepted control chars without escaping.

        Source: :wp:`Valid_characters_in_XML#XML_1.0`
        """
        self.unit.target = "Een\x00"
        assert self.unit.target == "Een"


class TestXLIFFfile(test_base.TestTranslationStore):
    StoreClass = xliff.xlifffile
    skeleton = """<?xml version="1.0" encoding="utf-8"?>
<xliff version="1.1" xmlns="urn:oasis:names:tc:xliff:document:1.1">
        <file original="doc.txt" source-language="en-US">
                <body>
                        %s
                </body>
        </file>
</xliff>"""

    def test_basic(self):
        xlifffile = xliff.xlifffile()
        assert xlifffile.units == []
        xlifffile.addsourceunit("Bla")
        assert len(xlifffile.units) == 1
        newfile = xliff.xlifffile.parsestring(bytes(xlifffile))
        print(bytes(xlifffile))
        assert len(newfile.units) == 1
        assert newfile.units[0].source == "Bla"
        assert newfile.findunit("Bla").source == "Bla"
        assert newfile.findunit("dit") is None

    def test_namespace(self):
        """Check that we handle namespaces other than the default correctly."""
        xlfsource = """<?xml version="1.0" encoding="utf-8"?>
<xliff:xliff version="1.2" xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2">
    <xliff:file original="doc.txt" source-language="en-US">
        <xliff:body>
            <xliff:trans-unit id="1">
                <xliff:source>File 1</xliff:source>
            </xliff:trans-unit>
        </xliff:body>
    </xliff:file>
</xliff:xliff>"""
        xlifffile = xliff.xlifffile.parsestring(xlfsource)
        print(bytes(xlifffile))
        assert xlifffile.units[0].source == "File 1"

    def test_rich_source(self):
        xlifffile = xliff.xlifffile()
        xliffunit = xlifffile.addsourceunit("")

        # Test 1
        xliffunit.rich_source = [StringElem(["foo", X(id="bar"), "baz"])]
        source_dom_node = xliffunit.getlanguageNode(None, 0)
        x_placeable = source_dom_node[0]

        assert source_dom_node.text == "foo"

        assert x_placeable.tag == "x"
        assert x_placeable.attrib["id"] == "bar"
        assert x_placeable.tail == "baz"

        xliffunit.rich_source[0].print_tree(2)
        print(xliffunit.rich_source)
        assert xliffunit.rich_source == [
            StringElem([StringElem("foo"), X(id="bar"), StringElem("baz")])
        ]

        # Test 2
        xliffunit.rich_source = [
            StringElem(
                ["foo", "baz", G(id="oof", sub=[G(id="zab", sub=["bar", "rab"])])]
            )
        ]
        source_dom_node = xliffunit.getlanguageNode(None, 0)
        g_placeable = source_dom_node[0]
        nested_g_placeable = g_placeable[0]

        assert source_dom_node.text == "foobaz"

        assert g_placeable.tag == "g"
        assert g_placeable.text is None
        assert g_placeable.attrib["id"] == "oof"
        assert g_placeable.tail is None

        assert nested_g_placeable.tag == "g"
        assert nested_g_placeable.text == "barrab"
        assert nested_g_placeable.attrib["id"] == "zab"
        assert nested_g_placeable.tail is None

        rich_source = xliffunit.rich_source
        rich_source[0].print_tree(2)
        assert rich_source == [
            StringElem(["foobaz", G(id="oof", sub=[G(id="zab", sub=["barrab"])])])
        ]

    def test_rich_target(self):
        xlifffile = xliff.xlifffile()
        xliffunit = xlifffile.addsourceunit("")

        # Test 1
        xliffunit.set_rich_target([StringElem(["foo", X(id="bar"), "baz"])], "fr")
        target_dom_node = xliffunit.getlanguageNode(None, 1)
        x_placeable = target_dom_node[0]

        assert target_dom_node.text == "foo"
        assert x_placeable.tag == "x"
        assert x_placeable.attrib["id"] == "bar"
        assert x_placeable.tail == "baz"

        # Test 2
        xliffunit.target = "test plain target"
        xliffunit.set_rich_target(
            [StringElem(["foo", G(id="eek", sub=[G(id="ook", sub=["bar", "rab"])])])],
            "fr",
        )
        xliffunit.set_rich_target(
            [
                StringElem(
                    ["foo", "baz", G(id="oof", sub=[G(id="zab", sub=["bar", "rab"])])]
                )
            ],
            "fr",
        )
        target_dom_node = xliffunit.getlanguageNode(None, 1)
        g_placeable = target_dom_node[0]
        nested_g_placeable = g_placeable[0]

        assert target_dom_node.text == "foobaz"

        assert g_placeable.tag == "g"
        print(f"g_placeable.text: {g_placeable.text} ({type(g_placeable.text)})")
        assert g_placeable.text is None
        assert g_placeable.attrib["id"] == "oof"
        assert g_placeable.tail is None

        assert nested_g_placeable.tag == "g"
        assert nested_g_placeable.text == "barrab"
        assert nested_g_placeable.attrib["id"] == "zab"
        assert nested_g_placeable.tail is None

        xliffunit.rich_target[0].print_tree(2)
        assert xliffunit.rich_target == [
            StringElem(["foobaz", G(id="oof", sub=[G(id="zab", sub=["barrab"])])])
        ]
        print(bytes(xlifffile).decode())
        assert (
            bytes(xlifffile).decode()
            == """<?xml version="1.0" encoding="UTF-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:1.1" version="1.1">
  <file original="NoName" source-language="en" datatype="plaintext">
    <body>
      <trans-unit xml:space="preserve" id="2" approved="yes">
        <source></source>
        <target state="translated">foobaz<g id="oof"><g id="zab">barrab</g></g></target>
      </trans-unit>
    </body>
  </file>
</xliff>
"""
        )

    def test_source(self):
        xlifffile = xliff.xlifffile()
        xliffunit = xlifffile.addsourceunit("Concept")
        xliffunit.source = "Term"
        newfile = xliff.xlifffile.parsestring(bytes(xlifffile))
        print(bytes(xlifffile))
        assert newfile.findunit("Concept") is None
        assert newfile.findunit("Term") is not None

    def test_target(self):
        xlifffile = xliff.xlifffile()
        xliffunit = xlifffile.addsourceunit("Concept")
        xliffunit.target = "Konsep"
        newfile = xliff.xlifffile.parsestring(bytes(xlifffile))
        print(bytes(xlifffile))
        assert newfile.findunit("Concept").target == "Konsep"

    def test_sourcelanguage(self):
        xlifffile = xliff.xlifffile(sourcelanguage="xh")
        xmltext = bytes(xlifffile).decode("utf-8")
        print(xmltext)
        assert xmltext.find('source-language="xh"') > 0
        # TODO: test that it also works for new files.

    def test_targetlanguage(self):
        xlifffile = xliff.xlifffile(sourcelanguage="zu", targetlanguage="af")
        xmltext = bytes(xlifffile).decode("utf-8")
        print(xmltext)
        assert xmltext.find('source-language="zu"') > 0
        assert xmltext.find('target-language="af"') > 0

    def test_targetlanguage_multi(self):
        xlfsource = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE foo [ <!ELEMENT foo ANY > <!ENTITY xxe SYSTEM "file:///etc/passwd" >]>
<xliff version="1.1" xmlns="urn:oasis:names:tc:xliff:document:1.1">
        <file original="doc.txt" source-language="en-US">
        </file>
        <file original="doc.txt" source-language="en-US">
        </file>
</xliff>"""
        xlifffile = xliff.xlifffile.parsestring(xlfsource)
        xlifffile.settargetlanguage("cs")
        xlifffile.setsourcelanguage("de")
        xmltext = bytes(xlifffile).decode()
        print(xmltext)
        assert xmltext.count('source-language="de"') == 2
        assert xmltext.count('target-language="cs"') == 2

    def test_notes(self):
        xlifffile = xliff.xlifffile()
        unit = xlifffile.addsourceunit("Concept")
        # We don't want to add unnecessary notes
        assert "note" not in bytes(xlifffile).decode("utf-8")
        unit.addnote(None)
        assert "note" not in bytes(xlifffile).decode("utf-8")
        unit.addnote("")
        assert "note" not in bytes(xlifffile).decode("utf-8")

        unit.addnote("Please buy bread")
        assert unit.getnotes() == "Please buy bread"
        notenodes = unit.xmlelement.findall(".//{}".format(unit.namespaced("note")))
        assert len(notenodes) == 1

        unit.addnote("Please buy milk", origin="Mom")
        notenodes = unit.xmlelement.findall(".//{}".format(unit.namespaced("note")))
        assert len(notenodes) == 2
        assert "from" not in notenodes[0].attrib
        assert notenodes[1].get("from") == "Mom"
        assert unit.getnotes(origin="Mom") == "Please buy milk"

        unit.addnote("Don't forget the beer", origin="Dad")
        notenodes = unit.xmlelement.findall(".//{}".format(unit.namespaced("note")))
        assert len(notenodes) == 3
        assert notenodes[1].get("from") == "Mom"
        assert notenodes[2].get("from") == "Dad"
        assert unit.getnotes(origin="Dad") == "Don't forget the beer"

        assert (
            unit.getnotes(origin="Bob")
            != "Please buy bread\nPlease buy milk\nDon't forget the beer"
        )
        assert notenodes[2].get("from") != "Mom"
        assert "from" not in notenodes[0].attrib
        assert (
            unit.getnotes()
            == "Please buy bread\nPlease buy milk\nDon't forget the beer"
        )
        assert unit.correctorigin(notenodes[2], "ad")
        assert not unit.correctorigin(notenodes[2], "om")

    def test_alttrans(self):
        """Test xliff <alt-trans> accessors."""
        xlifffile = xliff.xlifffile()
        unit = xlifffile.addsourceunit("Testing")

        unit.addalttrans("ginmi")
        unit.addalttrans("shikenki")
        alternatives = unit.getalttrans()
        assert alternatives[0].source == "Testing"
        assert alternatives[0].target == "ginmi"
        assert alternatives[1].target == "shikenki"

        assert not unit.target

        unit.addalttrans("Tasting", origin="bob", lang="eng")
        alternatives = unit.getalttrans()
        assert alternatives[2].target == "Tasting"

        alternatives = unit.getalttrans(origin="bob")
        assert alternatives[0].target == "Tasting"

        unit.delalttrans(alternatives[0])
        assert len(unit.getalttrans(origin="bob")) == 0
        alternatives = unit.getalttrans()
        assert len(alternatives) == 2
        assert alternatives[0].target == "ginmi"
        assert alternatives[1].target == "shikenki"

        # clean up:
        alternatives = unit.getalttrans()
        for alt in alternatives:
            unit.delalttrans(alt)
        unit.addalttrans("targetx", sourcetxt="sourcex")
        # test that the source node is before the target node:
        alt = unit.getalttrans()[0]
        altformat = etree.tostring(alt.xmlelement, encoding="unicode")
        print(altformat)
        assert altformat.find("<source") < altformat.find("<target")

        # test that a new target is still before alt-trans (bug 1098)
        unit.target = "newester target"
        unitformat = str(unit)
        print(unitformat)
        assert (
            unitformat.find("<source")
            < unitformat.find("<target")
            < unitformat.find("<alt-trans")
        )

    def test_fuzzy(self):
        xlifffile = xliff.xlifffile()
        unit = xlifffile.addsourceunit("Concept")
        unit.markfuzzy()
        assert not unit.isfuzzy()  # untranslated
        unit.target = "Konsep"
        assert not unit.isfuzzy()  # translated
        unit.markfuzzy()
        assert unit.isfuzzy()
        unit.markfuzzy(False)
        assert not unit.isfuzzy()
        unit.markfuzzy(True)
        assert unit.isfuzzy()

        # If there is no target, we can't really indicate fuzzyness, so we set
        # approved to "no". If we want isfuzzy() to reflect that, the line can
        # be uncommented
        unit.target = None
        assert unit.target is None
        print(unit)
        unit.markfuzzy(True)
        assert 'approved="no"' in str(unit)
        # assert unit.isfuzzy()

    def test_xml_space(self):
        """Test for the correct handling of xml:space attributes."""
        xlfsource = self.skeleton % (
            """<trans-unit id="1" xml:space="preserve">
                   <source> File  1 </source>
               </trans-unit>"""
        )
        xlifffile = xliff.xlifffile.parsestring(xlfsource)
        assert xlifffile.units[0].source == " File  1 "
        root_node = xlifffile.document.getroot()
        setXMLspace(root_node, "preserve")
        assert xlifffile.units[0].source == " File  1 "
        setXMLspace(root_node, "default")
        assert xlifffile.units[0].source == " File  1 "

        xlfsource = self.skeleton % (
            """<trans-unit id="1" xml:space="default">
                   <source> File  1 </source>
               </trans-unit>"""
        )
        xlifffile = xliff.xlifffile.parsestring(xlfsource)
        assert xlifffile.units[0].source == "File 1"
        root_node = xlifffile.document.getroot()
        setXMLspace(root_node, "preserve")
        assert xlifffile.units[0].source == "File 1"
        setXMLspace(root_node, "default")
        assert xlifffile.units[0].source == "File 1"

        xlfsource = self.skeleton % (
            """<trans-unit id="1">
                   <source> File  1 </source>
               </trans-unit>"""
        )
        # we currently always normalize as default behaviour for xliff
        xlifffile = xliff.xlifffile.parsestring(xlfsource)
        assert xlifffile.units[0].source == "File 1"
        root_node = xlifffile.document.getroot()
        setXMLspace(root_node, "preserve")
        assert xlifffile.units[0].source == "File 1"
        setXMLspace(root_node, "default")
        assert xlifffile.units[0].source == "File 1"

        xlfsource = self.skeleton % (
            """<trans-unit id="1">
                   <source> File  1
</source>
               </trans-unit>"""
        )
        # we currently always normalize as default behaviour for xliff
        xlifffile = xliff.xlifffile.parsestring(xlfsource)
        assert xlifffile.units[0].source == "File 1"
        root_node = xlifffile.document.getroot()
        setXMLspace(root_node, "preserve")
        assert xlifffile.units[0].source == "File 1"
        setXMLspace(root_node, "default")
        assert xlifffile.units[0].source == "File 1"

    def test_parsing(self):
        xlfsource = (
            self.skeleton
            % """<trans-unit id="1" xml:space="preserve">
                     <source>File</source>
                     <target/>
                 </trans-unit>"""
        )
        xlifffile = xliff.xlifffile.parsestring(xlfsource)
        assert xlifffile.units[0].istranslatable()

        xlfsource = (
            self.skeleton
            % """<trans-unit id="1" xml:space="preserve" translate="no">
                     <source>File</source>
                     <target/>
                 </trans-unit>"""
        )
        xlifffile = xliff.xlifffile.parsestring(xlfsource)
        assert not xlifffile.units[0].istranslatable()

        xlfsource = (
            self.skeleton
            % """<trans-unit id="1" xml:space="preserve" translate="yes">
                     <source>File</source>
                     <target/>
                 </trans-unit>"""
        )
        xlifffile = xliff.xlifffile.parsestring(xlfsource)
        assert xlifffile.units[0].istranslatable()

    def test_entities(self):
        xlfsource = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE foo [ <!ELEMENT foo ANY > <!ENTITY xxe SYSTEM "file:///etc/passwd" >]>
<xliff version="1.1" xmlns="urn:oasis:names:tc:xliff:document:1.1">
        <file original="doc.txt" source-language="en-US">
                <body>
                    <trans-unit id="1" xml:space="preserve" translate="yes">
                        <source>&xxe;</source>
                        <target/>
                    </trans-unit>
                    <trans-unit id="2" xml:space="preserve" translate="yes">
                        <source>&amp;</source>
                        <target/>
                    </trans-unit>
                </body>
        </file>
</xliff>"""
        xlifffile = xliff.xlifffile.parsestring(xlfsource)
        assert xlifffile.units[0].istranslatable()
        assert xlifffile.units[0].source == ""
        assert xlifffile.units[1].istranslatable()
        assert xlifffile.units[1].source == "&"

    def test_multiple_filenodes(self):
        xlfsource = """<?xml version="1.0" encoding="utf-8"?>
<xliff version="1.1" xmlns="urn:oasis:names:tc:xliff:document:1.1">
  <file original="file0" source-language="en" datatype="plaintext">
    <body>
      <trans-unit id="hello" approved="yes">
        <source>Hello</source>
      </trans-unit>
    </body>
  </file>
  <file original="file1" source-language="en" datatype="plaintext">
    <body>
      <trans-unit id="world" approved="yes">
        <source>World</source>
      </trans-unit>
    </body>
  </file>
</xliff>"""
        xfile = xliff.xlifffile.parsestring(xlfsource)
        assert len(xfile.units) == 2
        assert xfile.units[0].getid() == "file0\x04hello"
        assert xfile.units[1].getid() == "file1\x04world"
        xunit = xliff.xlifffile.UnitClass(source="goodbye")
        xunit.setid("file2\x04goodbye")
        xfile.addunit(xunit)
        assert xfile.units[2].getid() == "file2\x04goodbye"
        # if there is no file set it will use the active context
        xunit = xliff.xlifffile.UnitClass(source="lastfile")
        xunit.setid("lastfile")
        xfile.addunit(xunit)
        assert xfile.units[3].getid() == "file2\x04lastfile"
        newxfile = xliff.xlifffile()
        newxfile.addunit(xfile.units[0])
        newxfile.addunit(xfile.units[1])
        assert newxfile.units[0].getid() == "file0\x04hello"
        assert newxfile.units[1].getid() == "file1\x04world"
        assert newxfile.getfilenode("file0") is not None
        assert newxfile.getfilenode("file1") is not None
        assert not newxfile.getfilenode("foo")

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

        expected_output = b"""<?xml version="1.0" encoding="UTF-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:1.1" version="1.1">
  <file original="file1.txt" source-language="en" datatype="plaintext" target-language="fr">
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
</xliff>
"""

        source = xliff.xlifffile.parsestring(source_xliff)
        assert len(source.units) == 2

        # Add units to a new translation store
        translation = xliff.xlifffile()
        translation.sourcelanguage = "en"
        translation.targetlanguage = "fr"

        for unit in source.units:
            translation.addunit(unit)

        # Verify the structure matches expected
        serialized = bytes(translation)
        assert serialized == expected_output

        # Also verify by parsing and checking structure
        translation_reloaded = xliff.xlifffile.parsestring(serialized)
        assert len(translation_reloaded.units) == 2
        for unit in translation_reloaded.units:
            parent = unit.xmlelement.getparent()
            assert etree.QName(parent).localname == "group"

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
        translation_reloaded = xliff.xlifffile.parsestring(serialized)

        # Verify structure matches original
        assert translation_reloaded.getfilenames() == ["file1.txt", "file2.txt"]
        assert len(translation_reloaded.units) == 2

        # Check that each unit is in the correct file and group
        for i, unit in enumerate(translation_reloaded.units):
            parent = unit.xmlelement.getparent()
            assert etree.QName(parent).localname == "group"
            file_node = None
            for ancestor in unit.xmlelement.iterancestors():
                if ancestor.get("original"):
                    file_node = ancestor.get("original")
                    break
            if i == 0:
                assert file_node == "file1.txt"
                assert parent.get("id") == "group1"
            else:
                assert file_node == "file2.txt"
                assert parent.get("id") == "group2"

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
        translation_reloaded = xliff.xlifffile.parsestring(serialized)

        # Both units should be in group1
        for unit in translation_reloaded.units:
            parent = unit.xmlelement.getparent()
            assert etree.QName(parent).localname == "group"
            assert parent.get("id") == "group1"

    def test_add_unit_to_different_file(self):
        """Test adding units with different file than existing ones."""
        # Start with translation that has one file
        translation_xliff = b"""<?xml version="1.0" encoding="utf-8"?>
<xliff version="1.1" xmlns="urn:oasis:names:tc:xliff:document:1.1">
    <file original="file1.txt" source-language="en" datatype="plaintext" target-language="fr">
        <body>
            <trans-unit id="hello">
                <source>Hello</source>
                <target>Bonjour</target>
            </trans-unit>
        </body>
    </file>
</xliff>"""

        translation = xliff.xlifffile.parsestring(translation_xliff)
        assert translation.getfilenames() == ["file1.txt"]

        # Add a new unit from a different file
        source_xliff = b"""<?xml version="1.0" encoding="utf-8"?>
<xliff version="1.1" xmlns="urn:oasis:names:tc:xliff:document:1.1">
    <file original="file2.txt" source-language="en" datatype="plaintext">
        <body>
            <trans-unit id="world">
                <source>World</source>
            </trans-unit>
        </body>
    </file>
</xliff>"""

        source = xliff.xlifffile.parsestring(source_xliff)
        new_unit = source.units[0]

        # Add the new unit
        translation.addunit(new_unit)

        # Verify both files exist
        assert len(translation.units) == 2
        assert set(translation.getfilenames()) == {"file1.txt", "file2.txt"}

        # Verify structure is correct
        serialized = bytes(translation)
        translation_reloaded = xliff.xlifffile.parsestring(serialized)
        assert set(translation_reloaded.getfilenames()) == {"file1.txt", "file2.txt"}

        # Verify each unit is in the correct file
        for unit in translation_reloaded.units:
            unit_id = unit.getid()
            if "hello" in unit_id:
                assert unit_id.startswith("file1.txt")
            elif "world" in unit_id:
                assert unit_id.startswith("file2.txt")

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
        serialized = bytes(translation)
        translation_reloaded = xliff.xlifffile.parsestring(serialized)
        assert len(translation_reloaded.units) == 2

        # First unit should be in group
        parent1 = translation_reloaded.units[0].xmlelement.getparent()
        assert etree.QName(parent1).localname == "group"

        # Second unit should be directly in body
        parent2 = translation_reloaded.units[1].xmlelement.getparent()
        assert etree.QName(parent2).localname == "body"

    def test_addunit_with_new_false(self):
        """Test that addunit with new=False doesn't duplicate units."""
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
</xliff>"""

        source = xliff.xlifffile.parsestring(source_xliff)
        translation = xliff.xlifffile()
        translation.sourcelanguage = "en"
        translation.targetlanguage = "fr"

        unit = source.units[0]

        # Add unit with new=False - should not add to XML tree
        translation.addunit(unit, new=False)

        # Unit should be in units list but namespace should be set
        assert len(translation.units) == 1
        assert unit.namespace == translation.namespace

        # But xmlelement should not be in the body or any group
        serialized = bytes(translation)
        # Should not contain the trans-unit since new=False
        translation_reloaded = xliff.xlifffile.parsestring(serialized)
        assert len(translation_reloaded.units) == 0

    def test_namespace_preservation_across_versions(self):
        """Test that namespace is properly handled when copying between XLIFF versions."""
        # XLIFF 1.1 source
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
</xliff>"""

        source = xliff.xlifffile.parsestring(source_xliff)
        translation = xliff.xlifffile()
        translation.sourcelanguage = "en"
        translation.targetlanguage = "fr"

        # Add unit and verify namespace is set correctly
        unit = source.units[0]
        translation.addunit(unit)

        # Namespace should be updated to target's namespace
        assert unit.namespace == translation.namespace

        # Verify it serializes correctly
        serialized = bytes(translation)
        assert b'xmlns="urn:oasis:names:tc:xliff:document:1.1"' in serialized

    def test_add_units_between_different_files(self):
        """Test adding units from one file with multiple <file> tags to another, preserving file structure."""
        # Source with two files
        source_xliff = b"""<?xml version="1.0" encoding="utf-8"?>
<xliff version="1.1" xmlns="urn:oasis:names:tc:xliff:document:1.1">
    <file original="source_file1.txt" source-language="en" datatype="plaintext">
        <body>
            <trans-unit id="hello">
                <source>Hello</source>
            </trans-unit>
        </body>
    </file>
    <file original="source_file2.txt" source-language="en" datatype="plaintext">
        <body>
            <trans-unit id="world">
                <source>World</source>
            </trans-unit>
        </body>
    </file>
</xliff>"""

        # Target with one file
        target_xliff = b"""<?xml version="1.0" encoding="utf-8"?>
<xliff version="1.1" xmlns="urn:oasis:names:tc:xliff:document:1.1">
    <file original="target_file.txt" source-language="en" datatype="plaintext" target-language="fr">
        <body>
            <trans-unit id="existing">
                <source>Existing</source>
                <target>Existent</target>
            </trans-unit>
        </body>
    </file>
</xliff>"""

        source = xliff.xlifffile.parsestring(source_xliff)
        target = xliff.xlifffile.parsestring(target_xliff)

        # Add units from source to target
        for unit in source.units:
            target.addunit(unit)

        # Verify all three files are present
        serialized = bytes(target)
        target_reloaded = xliff.xlifffile.parsestring(serialized)

        filenames = target_reloaded.getfilenames()
        assert len(filenames) == 3
        assert "target_file.txt" in filenames
        assert "source_file1.txt" in filenames
        assert "source_file2.txt" in filenames

        # Verify units are in correct files
        assert len(target_reloaded.units) == 3
        for unit in target_reloaded.units:
            unit_id = unit.getid()
            if "existing" in unit_id:
                assert unit_id.startswith("target_file.txt")
            elif "hello" in unit_id:
                assert unit_id.startswith("source_file1.txt")
            elif "world" in unit_id:
                assert unit_id.startswith("source_file2.txt")

    def test_group_preservation_across_different_namespaces(self):
        """Test that group structure is preserved when adding units, using namespace-independent matching."""
        # Source with groups
        source_xliff = b"""<?xml version="1.0" encoding="utf-8"?>
<xliff version="1.1" xmlns="urn:oasis:names:tc:xliff:document:1.1">
    <file original="source.txt" source-language="en" datatype="plaintext">
        <body>
            <group id="mygroup" restype="x-gettext-domain">
                <trans-unit id="hello">
                    <source>Hello</source>
                </trans-unit>
            </group>
        </body>
    </file>
</xliff>"""

        # Target without groups (but same namespace)
        target_xliff = b"""<?xml version="1.0" encoding="utf-8"?>
<xliff version="1.1" xmlns="urn:oasis:names:tc:xliff:document:1.1">
    <file original="target.txt" source-language="en" datatype="plaintext" target-language="fr">
        <body>
            <trans-unit id="existing">
                <source>Existing</source>
                <target>Existent</target>
            </trans-unit>
        </body>
    </file>
</xliff>"""

        source = xliff.xlifffile.parsestring(source_xliff)
        target = xliff.xlifffile.parsestring(target_xliff)

        # Verify initial state
        assert len(source.units) == 1
        assert len(target.units) == 1

        # Add unit with group from source to target
        target.addunit(source.units[0])

        # Verify target now has 2 units
        assert len(target.units) == 2

        # Serialize and reload to verify structure
        serialized = bytes(target)
        target_reloaded = xliff.xlifffile.parsestring(serialized)

        # Should still have 2 units after round-trip
        assert len(target_reloaded.units) == 2

        # Find the newly added unit by source text
        new_unit = None
        existing_unit = None
        for unit in target_reloaded.units:
            if unit.source == "Hello":
                new_unit = unit
            elif unit.source == "Existing":
                existing_unit = unit

        assert new_unit is not None, "New unit with 'Hello' not found"
        assert existing_unit is not None, "Existing unit not found"

        # Verify the new unit is in a group (namespace-independent check)
        new_parent = new_unit.xmlelement.getparent()
        assert etree.QName(new_parent).localname == "group", (
            "New unit should be in a group"
        )
        assert new_parent.get("id") == "mygroup"
        assert new_parent.get("restype") == "x-gettext-domain"

        # Verify the existing unit is NOT in a group
        existing_parent = existing_unit.xmlelement.getparent()
        assert etree.QName(existing_parent).localname == "body", (
            "Existing unit should be in body"
        )

        # Verify unit's namespace is correctly set to target's namespace
        assert new_unit.namespace == target.namespace

    def test_cross_namespace_group_and_file_preservation(self):
        """Test that groups and files are preserved when adding units across different XLIFF namespaces."""
        # Source with XLIFF 1.2 namespace, with groups
        source_xliff = b"""<?xml version="1.0" encoding="utf-8"?>
<xliff version="1.2" xmlns="urn:oasis:names:tc:xliff:document:1.2">
    <file original="source_file1.txt" source-language="en" datatype="plaintext">
        <body>
            <group id="group1" restype="x-gettext-domain">
                <trans-unit id="hello">
                    <source>Hello</source>
                </trans-unit>
            </group>
        </body>
    </file>
    <file original="source_file2.txt" source-language="en" datatype="plaintext">
        <body>
            <trans-unit id="world">
                <source>World</source>
            </trans-unit>
        </body>
    </file>
</xliff>"""

        # Target with XLIFF 1.1 namespace (different from source)
        target_xliff = b"""<?xml version="1.0" encoding="utf-8"?>
<xliff version="1.1" xmlns="urn:oasis:names:tc:xliff:document:1.1">
    <file original="target_file.txt" source-language="en" datatype="plaintext" target-language="fr">
        <body>
            <trans-unit id="existing">
                <source>Existing</source>
                <target>Existent</target>
            </trans-unit>
        </body>
    </file>
</xliff>"""

        source = xliff.xlifffile.parsestring(source_xliff)
        target = xliff.xlifffile.parsestring(target_xliff)

        # Verify different namespaces
        assert source.namespace == "urn:oasis:names:tc:xliff:document:1.2"
        assert target.namespace == "urn:oasis:names:tc:xliff:document:1.1"

        # Add units from source (1.2) to target (1.1)
        for unit in source.units:
            target.addunit(unit)

        # Check that units were registered
        assert len(target.units) == 3, f"Expected 3 units, got {len(target.units)}"

        # Verify files are preserved - target should have original file plus two from source
        filenames = target.getfilenames()
        assert len(filenames) == 3, (
            f"Expected 3 files, got {len(filenames)}: {filenames}"
        )
        assert "target_file.txt" in filenames
        assert "source_file1.txt" in filenames
        assert "source_file2.txt" in filenames

        # Serialize and check structure
        serialized = bytes(target)

        # Parse with lxml to check namespace and structure
        from lxml import etree as lxml_etree

        tree = lxml_etree.fromstring(serialized)

        # Verify the document uses target's namespace (1.1)
        assert tree.nsmap[None] == "urn:oasis:names:tc:xliff:document:1.1"

        # Check for groups in target namespace
        groups = tree.xpath(
            "//ns:group", namespaces={"ns": "urn:oasis:names:tc:xliff:document:1.1"}
        )
        assert len(groups) >= 1, f"Expected at least 1 group, found {len(groups)}"

        # Verify group attributes are preserved
        group1 = None
        for g in groups:
            if g.get("id") == "group1":
                group1 = g
                break
        assert group1 is not None, "group1 not found"
        assert group1.get("restype") == "x-gettext-domain"

        # Verify all files are present in target namespace
        files = tree.xpath(
            "//ns:file", namespaces={"ns": "urn:oasis:names:tc:xliff:document:1.1"}
        )
        assert len(files) == 3, f"Expected 3 file elements, found {len(files)}"

        file_originals = [f.get("original") for f in files]
        assert "target_file.txt" in file_originals
        assert "source_file1.txt" in file_originals
        assert "source_file2.txt" in file_originals

    def test_indent(self):
        xlfsource = b"""<?xml version="1.0" encoding="UTF-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:1.1" version="1.1">
  <file original="doc.txt" source-language="en-US">
    <body>
      <trans-unit id="1" xml:space="preserve">
        <source>File</source>
        <target/>
      </trans-unit>
    </body>
  </file>
</xliff>
"""
        xlfsourcenote = b"""<?xml version="1.0" encoding="UTF-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:1.1" version="1.1">
  <file original="doc.txt" source-language="en-US">
    <body>
      <trans-unit id="1" xml:space="preserve">
        <source>File</source>
        <target/>
        <note>Test note</note>
      </trans-unit>
    </body>
  </file>
</xliff>
"""
        xfile = xliff.xlifffile.parsestring(xlfsource)
        assert bytes(xfile) == xlfsource
        xfile.units[0].addnote("Test note")
        assert bytes(xfile) == xlfsourcenote

    def test_add_target(self):
        xlfsource = """<?xml version="1.0" encoding="UTF-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:1.1" version="1.1">
  <file original="doc.txt" source-language="en-US">
    <body>
      <trans-unit id="1" xml:space="preserve">
      </trans-unit>
    </body>
  </file>
</xliff>
"""
        xlftarget = """<?xml version="1.0" encoding="UTF-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:1.1" version="1.1">
  <file original="doc.txt" source-language="en-US">
    <body>
      <trans-unit id="1" xml:space="preserve">
        <target>Soubor</target>
      </trans-unit>
    </body>
  </file>
</xliff>
"""
        xfile = xliff.xlifffile.parsestring(xlfsource)
        assert bytes(xfile).decode() == xlfsource
        xfile.units[0].rich_target = ["Soubor"]
        assert bytes(xfile).decode("ascii") == xlftarget

    def test_preserve(self):
        xlfsource = """<?xml version="1.0" encoding="UTF-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:1.1" version="1.1">
  <file original="doc.txt" source-language="en-US">
    <body>
      <trans-unit id="1" translate="yes">
        <source>Hello</source>
        <target/>
      </trans-unit>
    </body>
  </file>
</xliff>
"""
        xfile = xliff.xlifffile.parsestring(xlfsource)
        assert bytes(xfile).decode() == xlfsource
        xfile.units[0].target = "H  E"
        newfile = xliff.xlifffile.parsestring(bytes(xfile))
        assert newfile.units[0].target == "H  E"

    def test_closing_tags(self):
        xlfsource = """<?xml version="1.0" encoding="utf-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:1.2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1.2" xsi:schemaLocation="urn:oasis:names:tc:xliff:document:1.2 xliff-core-1.2-transitional.xsd">
  <file datatype="xml" source-language="en-US" target-language="en-US" original="Email - SMTP API">
    <body>
      <group id="body">
        <trans-unit id="Codeunit 270637162 - NamedType 3430817766" maxwidth="0" size-unit="char" translate="yes" xml:space="preserve">
          <source>Please connect to a server first.</source>
          <target state="translated">Please connect to a server first.</target>
          <note from="Developer" annotates="general" priority="2"></note>
          <note from="Xliff Generator" annotates="general" priority="3">Codeunit MailKit Client - NamedType ServerNotConnectedErr</note>
        </trans-unit>
      </group>
    </body>
  </file>
</xliff>
"""
        xlifffile = xliff.xlifffile.parsestring(xlfsource)
        xlifffile.XMLSelfClosingTags = False
        xlifffile.XMLuppercaseEncoding = False

        assert bytes(xlifffile).decode("utf-8") == xlfsource

    def test_context_groups(self):
        xlfsource = """<?xml version="1.0" encoding="utf-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:1.2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1.2" xsi:schemaLocation="urn:oasis:names:tc:xliff:document:1.2 xliff-core-1.2-transitional.xsd">
  <file datatype="xml" source-language="en-US" target-language="en-US" original="Email - SMTP API">
    <body>
      <group id="body">
        <trans-unit id="Codeunit 270637162 - NamedType 3430817766" maxwidth="0" size-unit="char" translate="yes" xml:space="preserve">
          <source>Please connect to a server first.</source>
          <target state="translated">Please connect to a server first.</target>
          <context-group purpose="location">
            <context context-type="sourcefile">some-directory/on-some-test/test.file</context>
            <context context-type="linenumber">222</context>
          </context-group>
        </trans-unit>
      </group>
    </body>
  </file>
</xliff>
"""
        xlifffile = xliff.xlifffile.parsestring(xlfsource)
        contextGroups = xlifffile.units[0].getcontextgroupsbyattribute(
            "purpose", "location"
        )

        assert contextGroups[0][0][0] == "sourcefile"
        assert contextGroups[0][0][1] == "some-directory/on-some-test/test.file"

        assert contextGroups[0][1][0] == "linenumber"
        assert contextGroups[0][1][1] == "222"

    def test_getlocations(self):
        xlfsource = """<?xml version="1.0" encoding="utf-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:1.2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1.2" xsi:schemaLocation="urn:oasis:names:tc:xliff:document:1.2 xliff-core-1.2-transitional.xsd">
  <file datatype="xml" source-language="en-US" target-language="en-US" original="Email - SMTP API">
    <body>
      <group id="body">
        <trans-unit id="Codeunit 270637162 - NamedType 3430817766" maxwidth="0" size-unit="char" translate="yes" xml:space="preserve">
          <source>Please connect to a server first.</source>
          <target state="translated">Please connect to a server first.</target>
          <context-group purpose="location">
            <context context-type="sourcefile">some-directory/on-some-test/test.file</context>
            <context context-type="linenumber">222</context>
          </context-group>
        </trans-unit>
      </group>
    </body>
  </file>
</xliff>
"""
        xlifffile = xliff.xlifffile.parsestring(xlfsource)
        locations = xlifffile.units[0].getlocations()

        assert locations == ["some-directory/on-some-test/test.file:222"]

    def test_addlocation(self):
        xlfsource = """<?xml version="1.0" encoding="utf-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:1.2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1.2" xsi:schemaLocation="urn:oasis:names:tc:xliff:document:1.2 xliff-core-1.2-transitional.xsd">
  <file datatype="xml" source-language="en-US" target-language="en-US" original="Email - SMTP API">
    <body>
      <group id="body">
        <trans-unit id="Codeunit 270637162 - NamedType 3430817766" maxwidth="0" size-unit="char" translate="yes" xml:space="preserve">
          <source>Please connect to a server first.</source>
          <target state="translated">Please connect to a server first.</target>
          <context-group purpose="location">
            <context context-type="sourcefile">some-directory/on-some-test/test.file</context>
            <context context-type="linenumber">222</context>
          </context-group>
        </trans-unit>
      </group>
    </body>
  </file>
</xliff>
"""
        xlifffile = xliff.xlifffile.parsestring(xlfsource)
        xlifffile.units[0].addlocation("some-directory/on-some-test/test.file2:333")
        xlifffile.units[0].addlocation("docs/config.md:block 1 (header)")
        xlifffile.units[0].addlocation("file.rst")
        locations = xlifffile.units[0].getlocations()
        assert locations == [
            "some-directory/on-some-test/test.file:222",
            "some-directory/on-some-test/test.file2:333",
            "docs/config.md:block 1 (header)",
            "file.rst",
        ]

    def test_huge(self):
        # This create approx 120MB Xliff file
        xlfsource = self.skeleton % (
            """<trans-unit id="1">
                     <source>text</source>
                     <target/>
                 </trans-unit>"""
            * 100_000
        )
        xlifffile = xliff.xlifffile.parsestring(xlfsource)
        assert len(xlifffile.units) == 100_000

    def test_preserve_add(self):
        # spellchecker:off
        target = """Por favor, ten a la mano los siguientes documentos para completar el proceso:
• INE (Credencial para votar) o pasaporte, vigentes
• Carátula del estado de cuenta bancario personal
• Cuenta CLABE Bancaria
• Constancia de Situación Fiscal con el Régimen de Sueldos y Salarios e Ingresos Asimilados a Salarios, con una vigencia no mayor a 90 días, completa, en FORMATO PDF"""
        # spellchecker:on
        xlfsource_template = """<?xml version="1.0" encoding="UTF-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:1.2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1.2" xsi:schemaLocation="urn:oasis:names:tc:xliff:document:1.2 xliff-core-1.2-transitional.xsd">
  <file datatype="xml" source-language="en-US" target-language="en-US" original="Email - SMTP API">
    <body>
      <group id="body">
        <trans-unit id="8864d0bd25f99594bbfb59780cb19a091946d8e6" datatype="html"{extra}>
          <source>Status</source>{target}
          <context-group purpose="location">
            <context context-type="sourcefile">src/app/settings/component/profile/example/example.component.html</context>
            <context context-type="linenumber">3</context>
          </context-group>
          <note priority="1" from="description">settings</note>
        </trans-unit>
      </group>
    </body>
  </file>
</xliff>
"""
        target_element = f"""
          <target state="translated">{target}</target>"""
        xlfsource_blank = xlfsource_template.format(target="", extra="")
        xlfsource_plain = xlfsource_template.format(target=target_element, extra="")
        xlfsource_preserve = xlfsource_template.format(
            target=target_element, extra=' xml:space="preserve"'
        )
        xlifffile = xliff.xlifffile.parsestring(xlfsource_plain)

        assert len(xlifffile.units) == 1
        unit = xlifffile.units[0]

        assert unit.target == target.replace("\n", " ")
        unit.target = target

        assert bytes(xlifffile).decode() == xlfsource_preserve

        xlifffile = xliff.xlifffile.parsestring(xlfsource_blank)

        assert len(xlifffile.units) == 1
        unit = xlifffile.units[0]

        assert unit.target is None
        unit.target = target

        assert bytes(xlifffile).decode() == xlfsource_template.format(
            target=target_element, extra=' xml:space="preserve" approved="yes"'
        )

        xlifffile = xliff.xlifffile.parsestring(xlfsource_preserve)

        assert len(xlifffile.units) == 1
        unit = xlifffile.units[0]

        assert unit.target == target

        assert bytes(xlifffile).decode() == xlfsource_preserve

        xlifffile = xliff.xlifffile.parsestring(xlfsource_plain)

        assert len(xlifffile.units) == 1
        unit = xlifffile.units[0]

        assert unit.target == target.replace("\n", " ")
        unit.rich_target = [target]

        assert bytes(xlifffile).decode() == xlfsource_preserve
