from translate.convert import po2xliff
from translate.misc.xml_helpers import XML_NS, getText
from translate.storage import po, poxliff


class TestPO2XLIFF:
    @staticmethod
    def po2xliff(posource, sourcelanguage="en", targetlanguage=None):
        """Helper that converts po source to xliff source without requiring files."""
        postore = po.pofile(posource.encode("utf-8"))
        convertor = po2xliff.po2xliff()
        outputxliff = convertor.convertstore(
            postore, None, sourcelanguage=sourcelanguage, targetlanguage=targetlanguage
        )
        return poxliff.PoXliffFile(outputxliff)

    @staticmethod
    def getnode(xliff):
        """Retrieves the trans-unit node from the dom."""
        assert len(xliff.units) == 1
        return xliff.units[0]

    def test_minimal(self) -> None:
        minipo = """msgid "red"\nmsgstr "rooi"\n"""
        xliff = self.po2xliff(minipo)
        print("The generated xml:")
        print(bytes(xliff))
        assert len(xliff.units) == 1
        assert xliff.translate("red") == "rooi"
        assert xliff.translate("bla") is None

    def test_basic(self) -> None:
        minipo = r"""# Afrikaans translation of program ABC
#
msgid ""
msgstr ""
"Project-Id-Version: program 2.1-branch\n"
"Report-Msgid-Bugs-To: \n"
"POT-Creation-Date: 2006-01-09 07:15+0100\n"
"PO-Revision-Date: 2004-03-30 17:02+0200\n"
"Last-Translator: Zuza Software Foundation <xxx@translate.org.za>\n"
"Language-Team: Afrikaans <translate-discuss-xxx@lists.sourceforge.net>\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"

# Please remember to do something
#: ../dir/file.xml.in.h:1 ../dir/file2.xml.in.h:4
msgid "Applications"
msgstr "Toepassings"
"""
        xliff = self.po2xliff(minipo)
        print("The generated xml:")
        print(bytes(xliff))
        assert xliff.translate("Applications") == "Toepassings"
        assert xliff.translate("bla") is None
        xmltext = bytes(xliff).decode("utf-8")
        assert xmltext.index("<xliff ") >= 0
        assert xmltext.index(' version="1.1"') >= 0
        assert xmltext.index("<file")
        assert xmltext.index("source-language")
        assert xmltext.index("datatype")

    def test_multiline(self) -> None:
        """Test multiline po entry."""
        minipo = r'''msgid "First part "
"and extra"
msgstr "Eerste deel "
"en ekstra"'''
        xliff = self.po2xliff(minipo)
        print("The generated xml:")
        print(bytes(xliff))
        assert xliff.translate("First part and extra") == "Eerste deel en ekstra"

    def test_escapednewlines(self) -> None:
        """Test the escaping of newlines."""
        minipo = r"""msgid "First line\nSecond line"
msgstr "Eerste lyn\nTweede lyn"
"""
        xliff = self.po2xliff(minipo)
        print("The generated xml:")
        xmltext = bytes(xliff).decode("utf-8")
        print(xmltext)
        assert xliff.translate("First line\nSecond line") == "Eerste lyn\nTweede lyn"
        assert xliff.translate("First line\\nSecond line") is None
        assert xmltext.find("line\\nSecond") == -1
        assert xmltext.find("lyn\\nTweede") == -1
        assert xmltext.find("line\nSecond") > 0
        assert xmltext.find("lyn\nTweede") > 0

    def test_escapedtabs(self) -> None:
        """Test the escaping of tabs."""
        minipo = r"""msgid "First column\tSecond column"
msgstr "Eerste kolom\tTweede kolom"
"""
        xliff = self.po2xliff(minipo)
        print("The generated xml:")
        xmltext = bytes(xliff).decode("utf-8")
        print(xmltext)
        assert (
            xliff.translate("First column\tSecond column")
            == "Eerste kolom\tTweede kolom"
        )
        assert xliff.translate("First column\\tSecond column") is None
        assert xmltext.find("column\\tSecond") == -1
        assert xmltext.find("kolom\\tTweede") == -1
        assert xmltext.find("column\tSecond") > 0
        assert xmltext.find("kolom\tTweede") > 0

    def test_escapedquotes(self) -> None:
        """Test the escaping of quotes (and slash)."""
        minipo = r"""msgid "Hello \"Everyone\""
msgstr "Good day \"All\""

msgid "Use \\\"."
msgstr "Gebruik \\\"."
"""
        xliff = self.po2xliff(minipo)
        print("The generated xml:")
        xmltext = bytes(xliff).decode("utf-8")
        print(xmltext)
        assert xliff.translate('Hello "Everyone"') == 'Good day "All"'
        assert xliff.translate(r"Use \".") == r"Gebruik \"."
        assert xmltext.find(r"\&quot;") > 0 or xmltext.find(r"\"") > 0
        assert xmltext.find(r"\\") == -1

    @staticmethod
    def getcontexttuples(node, namespace):
        """
        Returns all the information in the context nodes as a list of tuples
        of (type, text).
        """
        contexts = node.findall(f".//{{{namespace}}}context")
        return [(context.get("context-type"), getText(context)) for context in contexts]

    def test_locationcomments(self) -> None:
        minipo = r"""#: file.c:123 asdf.c
msgid "one"
msgstr "kunye"
"""
        xliff = self.po2xliff(minipo)
        print("The generated xml:")
        xmltext = bytes(xliff).decode("utf-8")
        print(xmltext)
        assert xliff.translate("one") == "kunye"
        assert len(xliff.units) == 1
        node = xliff.units[0].xmlelement
        contextgroups = node.findall(f".//{xliff.namespaced('context-group')}")
        assert len(contextgroups) == 2
        for group in contextgroups:
            assert group.get("name") == "po-reference"
            assert group.get("purpose") == "location"
        tuples = self.getcontexttuples(node, xliff.namespace)
        assert tuples == [
            ("sourcefile", "file.c"),
            ("linenumber", "123"),
            ("sourcefile", "asdf.c"),
        ]

    def test_othercomments(self) -> None:
        minipo = r"""# Translate?
# How?
msgid "one"
msgstr "kunye"
"""
        xliff = self.po2xliff(minipo)
        print("The generated xml:")
        xmltext = bytes(xliff)
        print(xmltext)
        assert xliff.translate("one") == "kunye"
        assert len(xliff.units) == 1
        node = xliff.units[0].xmlelement
        contextgroups = node.findall(f".//{xliff.namespaced('context-group')}")
        assert len(contextgroups) == 1
        for group in contextgroups:
            assert group.get("name") == "po-entry"
            assert group.get("purpose") == "information"
        tuples = self.getcontexttuples(node, xliff.namespace)
        assert tuples == [("x-po-trancomment", "Translate?\nHow?")]

        assert xliff.units[0].getnotes("translator") == "Translate?\nHow?"

    def test_automaticcomments(self) -> None:
        minipo = r"""#. Don't translate.
#. Please
msgid "one"
msgstr "kunye"
"""
        xliff = self.po2xliff(minipo)
        print("The generated xml:")
        xmltext = bytes(xliff)
        print(xmltext)
        assert xliff.translate("one") == "kunye"
        assert len(xliff.units) == 1
        node = xliff.units[0].xmlelement
        contextgroups = node.findall(f".//{xliff.namespaced('context-group')}")
        assert len(contextgroups) == 1
        for group in contextgroups:
            assert group.get("name") == "po-entry"
            assert group.get("purpose") == "information"
        tuples = self.getcontexttuples(node, xliff.namespace)
        assert tuples == [("x-po-autocomment", "Don't translate.\nPlease")]

    def test_header(self) -> None:
        minipo = r"""# Pulana  Translation for bla
# Hallo Ma!
#, fuzzy
msgid ""
msgstr ""
"Content-Type: text/plain; charset=UTF-8\n"
"""
        xliff = self.po2xliff(minipo)
        print("The generated xml:")
        xmltext = bytes(xliff)
        print(xmltext)
        assert len(xliff.units) == 1
        unit = xliff.units[0]
        assert unit.source == unit.target == "Content-Type: text/plain; charset=UTF-8\n"
        assert unit.xmlelement.get("restype") == "x-gettext-domain-header"
        assert unit.xmlelement.get("approved") != "yes"
        assert unit.xmlelement.get(f"{{{XML_NS}}}space") == "preserve"
        assert (
            unit.getnotes("po-translator") == "Pulana  Translation for bla\nHallo Ma!"
        )

    def test_fuzzy(self) -> None:
        minipo = r"""#, fuzzy
msgid "two"
msgstr "pedi"

msgid "three"
msgstr "raro"
"""
        xliff = self.po2xliff(minipo)
        print("The generated xml:")
        xmltext = bytes(xliff)
        print(xmltext)
        assert len(xliff.units) == 2
        assert xliff.units[0].isfuzzy()
        assert not xliff.units[1].isfuzzy()

    def test_previous_msgid_becomes_alttrans(self) -> None:
        minipo = r"""#, fuzzy
#| msgctxt "old button"
#| msgid "too many arguments"
msgctxt "button"
msgid "too few arguments"
msgstr "trop d arguments"
"""
        xliff = self.po2xliff(minipo)
        alternatives = xliff.units[0].getalttrans()
        assert len(alternatives) == 1
        assert alternatives[0].source == "too many arguments"
        assert alternatives[0].target == "trop d arguments"
        assert alternatives[0].getcontext() == "old button"

    def test_previous_plural_msgid_becomes_alttrans(self) -> None:
        minipo = r"""#, fuzzy
#| msgctxt "animal"
#| msgid "cow"
#| msgid_plural "cows"
msgctxt "young animal"
msgid "calf"
msgid_plural "calves"
msgstr[0] "inkonyane"
msgstr[1] "amankonyane"
"""
        xliff = self.po2xliff(minipo)
        assert len(xliff.units) == 1
        unit = xliff.units[0]
        assert unit.hasplural()

        alternatives = unit.getalttrans()
        assert len(alternatives) == 1
        assert alternatives[0].source.strings == ["cow", "cows"]
        assert alternatives[0].target.strings == ["inkonyane", "amankonyane"]
        assert alternatives[0].getcontext() == "animal"

        singular_alternatives = unit.units[0].getalttrans()
        assert len(singular_alternatives) == 1
        assert singular_alternatives[0].source == "cow"
        assert singular_alternatives[0].target == "inkonyane"
        assert singular_alternatives[0].getcontext() == "animal"

        plural_alternatives = unit.units[1].getalttrans()
        assert len(plural_alternatives) == 1
        assert plural_alternatives[0].source == "cows"
        assert plural_alternatives[0].target == "amankonyane"
        assert plural_alternatives[0].getcontext() == "animal"

    def test_previous_singular_msgid_on_plural_unit_becomes_single_alttrans(
        self,
    ) -> None:
        minipo = r"""#, fuzzy
#| msgid "cow"
msgid "calf"
msgid_plural "calves"
msgstr[0] "inkonyane"
msgstr[1] "amankonyane"
"""
        xliff = self.po2xliff(minipo)
        assert len(xliff.units) == 1
        unit = xliff.units[0]
        assert unit.hasplural()

        alternatives = unit.getalttrans()
        assert len(alternatives) == 1
        assert alternatives[0].source == "cow"
        assert alternatives[0].target == "inkonyane"

        singular_alternatives = unit.units[0].getalttrans()
        assert len(singular_alternatives) == 1
        assert singular_alternatives[0].source == "cow"
        assert singular_alternatives[0].target == "inkonyane"

        assert unit.units[1].getalttrans() == []

    def test_previous_plural_msgid_on_singular_unit_preserves_alttrans(
        self,
    ) -> None:
        minipo = r"""#, fuzzy
#| msgid "cow"
#| msgid_plural "cows"
msgid "calf"
msgstr "inkonyane"
"""
        xliff = self.po2xliff(minipo)
        assert len(xliff.units) == 1
        unit = xliff.units[0]
        assert not unit.hasplural()

        alternatives = unit.getalttrans()
        assert len(alternatives) == 2
        assert [alternative.source for alternative in alternatives] == ["cow", "cows"]
        assert [alternative.target for alternative in alternatives] == [
            "inkonyane",
            "inkonyane",
        ]

    def test_germanic_plurals(self) -> None:
        minipo = r"""msgid "cow"
msgid_plural "cows"
msgstr[0] "inkomo"
msgstr[1] "iinkomo"
"""
        xliff = self.po2xliff(minipo)
        print("The generated xml:")
        xmltext = bytes(xliff)
        print(xmltext)
        assert len(xliff.units) == 1
        assert xliff.translate("cow") == "inkomo"

    def test_funny_plurals(self) -> None:
        minipo = r"""msgid "cow"
msgid_plural "cows"
msgstr[0] "inkomo"
msgstr[1] "iinkomo"
msgstr[2] "iiinkomo"
"""
        xliff = self.po2xliff(minipo)
        print("The generated xml:")
        xmltext = bytes(xliff)
        print(xmltext)
        assert len(xliff.units) == 1
        assert xliff.translate("cow") == "inkomo"

    def test_language_tags(self) -> None:
        minipo = r"""msgid "Een"
msgstr "Uno"
"""
        xliff = self.po2xliff(minipo, "af", "es")
        assert xliff.sourcelanguage == "af"
        assert xliff.targetlanguage == "es"

    def test_variables(self) -> None:
        minipo = r'''msgid "%s%s%s%s has made %s his or her buddy%s%s"
msgstr "%s%s%s%s het %s sy/haar vriend/vriendin gemaak%s%s"'''
        xliff = self.po2xliff(minipo)
        print(xliff.units[0].source)
        assert xliff.units[0].source == "%s%s%s%s has made %s his or her buddy%s%s"

    def test_approved(self) -> None:
        minipo = r"""#, fuzzy
msgid "two"
msgstr "pedi"

msgid "three"
msgstr "raro"

msgid "four"
msgstr ""
"""
        xliff = self.po2xliff(minipo)
        print("The generated xml:")
        xmltext = bytes(xliff)
        print(xmltext)
        assert len(xliff.units) == 3
        assert xliff.units[0].xmlelement.get("approved") != "yes"
        assert not xliff.units[0].isapproved()
        assert xliff.units[1].xmlelement.get("approved") == "yes"
        assert xliff.units[1].isapproved()
        assert xliff.units[2].xmlelement.get("approved") != "yes"
        assert not xliff.units[2].isapproved()
