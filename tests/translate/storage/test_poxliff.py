from lxml import etree

from translate.misc.multistring import multistring
from translate.storage import poxliff

from . import test_xliff


class TestPOXLIFFUnit(test_xliff.TestXLIFFUnit):
    UnitClass = poxliff.PoXliffUnit

    def test_plurals(self) -> None:
        """Tests that plurals are handled correctly."""
        unit = self.UnitClass(multistring(["Cow", "Cows"]))
        print(type(unit.source))
        print(repr(unit.source))
        assert isinstance(unit.source, multistring)
        assert unit.source.strings == ["Cow", "Cows"]
        assert unit.source == "Cow"

        unit.target = ["Koei", "Koeie"]
        assert isinstance(unit.target, multistring)
        assert unit.target.strings == ["Koei", "Koeie"]
        assert unit.target == "Koei"

        unit.target = ["Sk\u00ear", "Sk\u00eare"]
        assert isinstance(unit.target, multistring)
        assert unit.target.strings == ["Sk\u00ear", "Sk\u00eare"]
        assert unit.target.strings == ["Sk\u00ear", "Sk\u00eare"]
        assert unit.target == "Sk\u00ear"

    def test_ids(self) -> None:
        """Tests that ids are assigned correctly, especially for plurals."""
        unit = self.UnitClass("gras")
        assert not unit.getid()
        unit.setid("4")
        assert unit.getid() == "4"

        unit = self.UnitClass(multistring(["shoe", "shoes"]))
        assert not unit.getid()
        unit.setid("20")
        assert unit.getid() == "20"
        assert unit.units[1].getid() == "20[1]"

        unit.target = ["utshani", "uutshani", "uuutshani"]
        assert unit.getid() == "20"
        assert unit.units[1].getid() == "20[1]"

    def test_setsource_preserves_child_ids(self) -> None:
        """Tests that setsource propagates group ID to new child trans-units."""
        unit = self.UnitClass(multistring(["cow", "cows"]))
        unit.setid("L_PLU.TEST")
        assert unit.units[0].xmlelement.get("id") == "L_PLU.TEST[0]"
        assert unit.units[1].xmlelement.get("id") == "L_PLU.TEST[1]"

        # Resetting source should propagate IDs to new children
        unit.source = multistring(["cow", "cows", "cows"])
        assert unit.xmlelement.get("id") == "L_PLU.TEST"
        assert unit.units[0].xmlelement.get("id") == "L_PLU.TEST[0]"
        assert unit.units[1].xmlelement.get("id") == "L_PLU.TEST[1]"
        assert unit.units[2].xmlelement.get("id") == "L_PLU.TEST[2]"

    def test_setsource_singular_to_plural_rebuilds_group(self) -> None:
        """Tests that switching from singular to plural rebuilds the XML node."""
        unit = self.UnitClass("cow")
        unit.setid("L_PLU.TEST")
        unit.target = "vache"
        unit.addnote("translator note")

        unit.source = multistring(["cow", "cows"])

        assert unit.hasplural()
        assert unit.xmlelement.tag == unit.namespaced("group")
        assert unit.xmlelement.get("restype") == "x-gettext-plurals"
        assert len(unit.units) == 2
        assert [child.tag for child in unit.xmlelement] == [
            unit.namespaced("note"),
            unit.namespaced("trans-unit"),
            unit.namespaced("trans-unit"),
        ]
        assert unit.units[0].xmlelement.get("id") == "L_PLU.TEST[0]"
        assert unit.units[1].xmlelement.get("id") == "L_PLU.TEST[1]"
        assert unit.target.strings == ["vache", ""]

    def test_setsource_nonplural_on_plural_group(self) -> None:
        """
        Tests that setting a non-plural source on a plural group doesn't
        add <source> to the group element.
        """
        unit = self.UnitClass(multistring(["cow", "cows"]))
        unit.setid("L_PLU.TEST")

        # Setting a single string source should update child units, not group
        unit.source = "updated"
        assert unit.hasplural()
        # Should NOT have <source> directly on the group
        ns = unit.namespaced("source")
        group_sources = [c for c in unit.xmlelement if c.tag == ns]
        assert len(group_sources) == 0
        # Child units should have the updated source
        assert unit.units[0].source == "updated"
        assert unit.units[1].source == "updated"

    def test_setsource_nonplural_removes_stale_group_source(self) -> None:
        """
        Tests that setting a non-plural source on a plural group also
        removes any stale <source> element on the group.
        """
        unit = self.UnitClass(multistring(["cow", "cows"]))
        unit.setid("L_PLU.TEST")
        # Manually inject a stale <source> on the group (simulating old buggy data)
        stale_source = etree.SubElement(unit.xmlelement, unit.namespaced("source"))
        stale_source.text = "stale"
        ns = unit.namespaced("source")
        assert len([c for c in unit.xmlelement if c.tag == ns]) == 1

        # Setting non-plural source should clean up the stale <source>
        unit.source = "updated"
        group_sources = [c for c in unit.xmlelement if c.tag == ns]
        assert len(group_sources) == 0
        assert unit.units[0].source == "updated"
        assert unit.units[1].source == "updated"

    def test_settarget_none_on_plural(self) -> None:
        """
        Tests that setting target to None on a plural unit doesn't create
        empty target elements.
        """
        unit = self.UnitClass(multistring(["cow", "cows"]))
        unit.setid("L_PLU.TEST")
        unit.target = multistring(["vache", "vaches"])
        assert unit.target.strings == ["vache", "vaches"]

        # Setting target to None should clear targets
        unit.target = None
        for child_unit in unit.units:
            assert child_unit.target is None

    def test_construction_no_empty_targets(self) -> None:
        """
        Tests that constructing a plural unit doesn't add empty <target>
        elements to child trans-units.
        """
        unit = self.UnitClass(multistring(["cow", "cows"]))
        ns = unit.namespaced("target")
        for child_unit in unit.units:
            targets = list(child_unit.xmlelement.iterchildren(ns))
            assert len(targets) == 0

    def test_setsource_plural_without_targets_keeps_target_nodes_absent(self) -> None:
        """Tests that resetting plural source doesn't create empty targets."""
        unit = self.UnitClass(multistring(["cow", "cows"]))
        unit.setid("L_PLU.TEST")

        unit.source = multistring(["cow", "cows", "calves"])

        ns = unit.namespaced("target")
        for child_unit in unit.units:
            targets = list(child_unit.xmlelement.iterchildren(ns))
            assert len(targets) == 0


class TestPOXLIFFfile(test_xliff.TestXLIFFfile):
    StoreClass = poxliff.PoXliffFile
    xliffskeleton = """<?xml version="1.0" ?>
<xliff version="1.1" xmlns="urn:oasis:names:tc:xliff:document:1.1">
  <file original="filename.po" source-language="en-US" datatype="po">
    <body>
        %s
    </body>
  </file>
</xliff>"""

    def test_parse(self) -> None:
        minixlf = (
            self.xliffskeleton
            % """<group restype="x-gettext-plurals">
        <trans-unit id="1[0]" xml:space="preserve">
            <source>cow</source>
            <target>inkomo</target>
        </trans-unit>
        <trans-unit id="1[1]" xml:space="preserve">
            <source>cows</source>
            <target>iinkomo</target>
        </trans-unit>
</group>"""
        )
        xlifffile = self.StoreClass.parsestring(minixlf)
        assert len(xlifffile.units) == 1
        assert xlifffile.units[0].hasplural()
        assert xlifffile.translate("cow") == "inkomo"
        assert xlifffile.units[0].source == "cow"
        assert xlifffile.units[0].source.strings == ["cow", "cows"]
        assert xlifffile.units[0].target.strings == ["inkomo", "iinkomo"]

    def test_parse_plural_alpha_id(self) -> None:
        minixlf = (
            self.xliffskeleton
            % """<group restype="x-gettext-plurals">
        <trans-unit id="test[0]" xml:space="preserve">
            <source>cow</source>
            <target>inkomo</target>
        </trans-unit>
        <trans-unit id="test[1]" xml:space="preserve">
            <source>cows</source>
            <target>iinkomo</target>
        </trans-unit>
</group>"""
        )
        xlifffile = self.StoreClass.parsestring(minixlf)
        assert len(xlifffile.units) == 1
        assert xlifffile.units[0].hasplural()
        assert xlifffile.translate("cow") == "inkomo"
        assert xlifffile.units[0].source == "cow"
        assert xlifffile.units[0].source.strings == ["cow", "cows"]
        assert xlifffile.units[0].target.strings == ["inkomo", "iinkomo"]

    def test_notes(self) -> None:
        minixlf = (
            self.xliffskeleton
            % """<group restype="x-gettext-plurals">
        <trans-unit id="1[0]" xml:space="preserve">
            <source>cow</source>
            <target>inkomo</target>
<note from="po-translator">Zulu translation of program ABC</note>
<note from="developer">azoozoo come back!</note>
        </trans-unit>
        <trans-unit id="1[1]" xml:space="preserve">
            <source>cows</source>
            <target>iinkomo</target>
<note from="po-translator">Zulu translation of program ABC</note>
<note from="developer">azoozoo come back!</note>
        </trans-unit>
</group>"""
        )
        xlifffile = self.StoreClass.parsestring(minixlf)
        assert (
            xlifffile.units[0].getnotes()
            == "Zulu translation of program ABC\nazoozoo come back!"
        )
        assert xlifffile.units[0].getnotes("developer") == "azoozoo come back!"
        assert (
            xlifffile.units[0].getnotes("po-translator")
            == "Zulu translation of program ABC"
        )

    def test_plural(self) -> None:
        minixlf = (
            self.xliffskeleton
            % """
        <group id="1238108068" restype="x-gettext-plurals">
                <trans-unit id="1238108068[0]" xml:space="preserve">
                        <source>This field must contain at least {0,number} character</source>
                </trans-unit>
                <trans-unit id="1238108068[1]" xml:space="preserve">
                        <source>This field must contain at least {0,number} characters</source>
                </trans-unit>
        </group>
            """
        )
        xlifffile = self.StoreClass.parsestring(minixlf)
        assert len(xlifffile.units) == 1
        unit = xlifffile.units[0]
        assert unit.source.strings == [
            "This field must contain at least {0,number} character",
            "This field must contain at least {0,number} characters",
        ]
        assert unit.target == ["", ""]

    def test_parse_plural_many_forms(self) -> None:
        """Tests parsing plural groups with more than 6 forms (e.g. Arabic)."""
        forms = [
            f'<trans-unit id="ar[{i}]" xml:space="preserve">'
            f"<source>form{i}</source>"
            f"<target>target{i}</target>"
            f"</trans-unit>"
            for i in range(7)
        ]
        minixlf = self.xliffskeleton % (
            '<group id="ar" restype="x-gettext-plurals">'
            + "\n".join(forms)
            + "</group>"
        )
        xlifffile = self.StoreClass.parsestring(minixlf)
        assert len(xlifffile.units) == 1
        unit = xlifffile.units[0]
        assert unit.hasplural()
        assert len(unit.units) == 7
        assert unit.source.strings == [f"form{i}" for i in range(7)]

    def test_parse_nonplural_bracketed_numeric_id(self) -> None:
        """Tests that standalone units with bracketed numeric IDs are kept."""
        minixlf = (
            self.xliffskeleton
            % """<trans-unit id="menu[12]" xml:space="preserve">
        <source>Menu item</source>
        <target>Polozka menu</target>
      </trans-unit>"""
        )
        xlifffile = self.StoreClass.parsestring(minixlf)
        assert len(xlifffile.units) == 1
        unit = xlifffile.units[0]
        assert not unit.hasplural()
        assert unit.xmlelement.get("id") == "menu[12]"
        assert unit.source == "Menu item"
        assert unit.target == "Polozka menu"

    def test_expanding_plural_targets_keeps_local_xliff_ids(self) -> None:
        """Tests that plural growth doesn't leak file-qualified IDs to XML."""
        minixlf = (
            self.xliffskeleton
            % """<group restype="x-gettext-plurals" id="5" approved="no">
        <trans-unit id="5[0]" xml:space="preserve" approved="yes">
            <source>This is one</source>
            <target state="translated">nl one</target>
        </trans-unit>
        <trans-unit id="5[1]" xml:space="preserve" approved="yes">
            <source>These are many</source>
            <target state="translated">nl many</target>
        </trans-unit>
</group>"""
        )
        xlifffile = self.StoreClass.parsestring(minixlf)
        unit = xlifffile.units[0]

        unit.target = multistring(["pl one", "pl few", "pl many"])

        assert unit.getid() == "filename.po\x045"
        assert unit.xmlelement.get("id") == "5"
        assert [child.xmlelement.get("id") for child in unit.units] == [
            "5[0]",
            "5[1]",
            "5[2]",
        ]
        serialized = bytes(xlifffile).decode("utf-8")
        assert 'id="5"' in serialized
        assert 'id="5[2]"' in serialized
        assert "__%04__" not in serialized

    def test_expanding_plural_targets_without_group_id_preserves_anonymous_group(
        self,
    ) -> None:
        """Tests that plural growth keeps anonymous groups anonymous."""
        minixlf = (
            self.xliffskeleton
            % """<group restype="x-gettext-plurals" approved="no">
        <trans-unit id="test[0]" xml:space="preserve" approved="yes">
            <source>This is one</source>
            <target state="translated">nl one</target>
        </trans-unit>
        <trans-unit id="test[1]" xml:space="preserve" approved="yes">
            <source>These are many</source>
            <target state="translated">nl many</target>
        </trans-unit>
</group>"""
        )
        xlifffile = self.StoreClass.parsestring(minixlf)
        unit = xlifffile.units[0]

        unit.target = multistring(["pl one", "pl few", "pl many"])

        assert unit.xmlelement.get("id") is None
        assert [child.xmlelement.get("id") for child in unit.units] == [
            "test[0]",
            "test[1]",
            "test[2]",
        ]
        serialized = bytes(xlifffile).decode("utf-8")
        assert 'id="test[2]"' in serialized
        assert '<group restype="x-gettext-plurals" approved="no">' in serialized
        assert 'id=""' not in serialized
        assert 'id="[0]"' not in serialized

    def test_expanding_anonymous_plural_targets_does_not_collide_with_existing_id(
        self,
    ) -> None:
        """Tests that anonymous plural growth does not synthesize a colliding group ID."""
        minixlf = (
            self.xliffskeleton
            % """<trans-unit id="test" xml:space="preserve">
        <source>Standalone</source>
        <target>Standalone target</target>
      </trans-unit>
      <group restype="x-gettext-plurals" approved="no">
        <trans-unit id="test[0]" xml:space="preserve" approved="yes">
            <source>This is one</source>
            <target state="translated">nl one</target>
        </trans-unit>
        <trans-unit id="test[1]" xml:space="preserve" approved="yes">
            <source>These are many</source>
            <target state="translated">nl many</target>
        </trans-unit>
</group>"""
        )
        xlifffile = self.StoreClass.parsestring(minixlf)
        singular = xlifffile.units[0]
        plural = xlifffile.units[1]

        plural.target = multistring(["pl one", "pl few", "pl many"])

        assert singular.getid() == "filename.po\x04test"
        assert plural.getid() == "filename.po\x04"
        assert xlifffile.findid("filename.po\x04test") is singular
        assert plural.xmlelement.get("id") is None
        assert [child.xmlelement.get("id") for child in plural.units] == [
            "test[0]",
            "test[1]",
            "test[2]",
        ]

    def test_detached_plural_with_file_qualified_id_adds_to_matching_file(self) -> None:
        """Tests that detached plural units still route to the right file."""
        xlifffile = self.StoreClass()
        unit = self.StoreClass.UnitClass(multistring(["cow", "cows"]))

        unit.setid("other.po\x04msg")
        xlifffile.addunit(unit)

        assert xlifffile.getfilenames() == ["other.po"]
        assert unit.getid() == "other.po\x04msg"
        assert unit.xmlelement.get("id") == "msg"
        assert [child.xmlelement.get("id") for child in unit.units] == [
            "msg[0]",
            "msg[1]",
        ]

    def test_detached_anonymous_plural_routed_by_filename_normalizes_child_ids(
        self,
    ) -> None:
        """Tests that anonymous plural filename routing doesn't leak filename into child IDs."""
        xlifffile = self.StoreClass()
        unit = self.StoreClass.UnitClass(multistring(["cow", "cows"]))

        unit.setid("")
        unit.setpendingfilename("other.po")
        xlifffile.addunit(unit)

        assert xlifffile.getfilenames() == ["other.po"]
        assert unit.getid() == "other.po\x04"
        assert unit.xmlelement.get("id") is None
        assert [child.xmlelement.get("id") for child in unit.units] == [
            "[0]",
            "[1]",
        ]
        serialized = bytes(xlifffile).decode("utf-8")
        assert "other.po__%04__" not in serialized

    def test_expanding_plural_targets_preserves_contextual_id(self) -> None:
        """Tests that plural growth preserves local contextual IDs."""
        minixlf = (
            self.xliffskeleton
            % """<group restype="x-gettext-plurals" id="context__%04__message">
        <trans-unit id="context__%04__message[0]" xml:space="preserve">
            <source>a</source>
            <target>x</target>
        </trans-unit>
        <trans-unit id="context__%04__message[1]" xml:space="preserve">
            <source>b</source>
            <target>y</target>
        </trans-unit>
</group>"""
        )
        xlifffile = self.StoreClass.parsestring(minixlf)
        unit = xlifffile.units[0]

        unit.target = multistring(["pl one", "pl few", "pl many"])

        assert unit.getid() == "filename.po\x04context\x04message"
        assert unit.xmlelement.get("id") == "context__%04__message"
        assert [child.xmlelement.get("id") for child in unit.units] == [
            "context__%04__message[0]",
            "context__%04__message[1]",
            "context__%04__message[2]",
        ]

    def test_expanding_detached_plural_targets_preserves_file_qualified_id(
        self,
    ) -> None:
        """Tests that detached plural growth keeps file-qualified IDs for addunit."""
        xlifffile = self.StoreClass()
        unit = self.StoreClass.UnitClass(multistring(["cow", "cows"]))

        unit.setid("message")
        unit.setpendingfilename("other.po")
        unit.target = multistring(["one", "few", "many"])
        xlifffile.addunit(unit)

        assert xlifffile.getfilenames() == ["other.po"]
        assert unit.getid() == "other.po\x04message"
        assert unit.xmlelement.get("id") == "message"
        assert [child.xmlelement.get("id") for child in unit.units] == [
            "message[0]",
            "message[1]",
            "message[2]",
        ]

    def test_expanding_detached_anonymous_plural_targets_keeps_bracket_ids(
        self,
    ) -> None:
        """Tests detached anonymous plural growth preserves bracket-only child IDs."""
        xlifffile = self.StoreClass()
        unit = self.StoreClass.UnitClass(multistring(["cow", "cows"]))
        unit.setid("")
        unit.setpendingfilename("other.po")
        xlifffile.addunit(unit)

        assert [child.xmlelement.get("id") for child in unit.units] == [
            "[0]",
            "[1]",
        ]

        unit.target = multistring(["one", "few", "many"])

        assert unit.xmlelement.get("id") is None
        assert [child.xmlelement.get("id") for child in unit.units] == [
            "[0]",
            "[1]",
            "[2]",
        ]
