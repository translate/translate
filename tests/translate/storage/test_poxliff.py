from translate.misc.multistring import multistring
from translate.storage import poxliff

from . import test_xliff


class TestPOXLIFFUnit(test_xliff.TestXLIFFUnit):
    UnitClass = poxliff.PoXliffUnit

    def test_plurals(self):
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

    def test_ids(self):
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

    def test_parse(self):
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
        assert xlifffile.translate("cow") == "inkomo"
        assert xlifffile.units[0].source == "cow"
        assert xlifffile.units[0].source == multistring(["cow", "cows"])

    def test_parse_plural_alpha_id(self):
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
        assert xlifffile.translate("cow") == "inkomo"
        assert xlifffile.units[0].source == "cow"
        assert xlifffile.units[0].source == multistring(["cow", "cows"])

    def test_notes(self):
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

    def test_plural(self):
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
