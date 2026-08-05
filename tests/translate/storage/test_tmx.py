from io import BytesIO

from translate.storage import tmx

from . import test_base


class TestTMXUnit(test_base.TestTranslationUnit):
    UnitClass = tmx.tmxunit


class TestTMXUnitFromParsedString(TestTMXUnit):
    tmxsource = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE tmx
  SYSTEM 'tmx14.dtd'>
<tmx version="1.4">
        <header adminlang="en" creationtool="Translate Toolkit" creationtoolversion="1.0beta" datatype="PlainText" o-tmf="UTF-8" segtype="sentence" srclang="en"/>
        <body>
                <tu>
                        <tuv xml:lang="en">
                                <seg>Test String</seg>
                        </tuv>
                </tu>
        </body>
</tmx>"""

    def setup_method(self, method) -> None:
        store = tmx.tmxfile.parsestring(self.tmxsource)
        self.unit = store.units[0]

    def test_context(self) -> None:
        tmxunit = self.UnitClass("Sample source")
        assert tmxunit.getcontext() == ""
        tmxunit.setcontext("context info")
        assert tmxunit.getcontext() == "context info"


class TestTMXfile(test_base.TestTranslationStore):
    StoreClass = tmx.tmxfile

    @staticmethod
    def language_selection_tmx(tus: str, srclang: str = "en") -> str:
        return f"""<?xml version="1.0" encoding="utf-8"?>
<tmx version="1.4">
    <header creationtool="test" creationtoolversion="1" datatype="unknown"
            segtype="sentence" adminlang="en" srclang="{srclang}" o-tmf="TMX"/>
    <body>
{tus}
    </body>
</tmx>"""

    @classmethod
    def multilingual_tmx(cls) -> str:
        return cls.language_selection_tmx(
            """        <tu tuid="test1">
            <tuv xml:lang="ar"><seg>test1_ar</seg></tuv>
            <tuv xml:lang="de"><seg>test1_de</seg></tuv>
            <tuv xml:lang="en"><seg>test1_en</seg></tuv>
        </tu>
        <tu tuid="test2">
            <tuv xml:lang="en"><seg>test2_en</seg></tuv>
            <tuv xml:lang="de"><seg>test2_de</seg></tuv>
            <tuv xml:lang="ar"><seg>test2_ar</seg></tuv>
        </tu>"""
        )

    @staticmethod
    def tmxparse(tmxsource):
        """Helper that parses tmx source without requiring files."""
        dummyfile = BytesIO(tmxsource)
        print(tmxsource)
        return tmx.tmxfile(dummyfile)

    def test_translate(self) -> None:
        tmxfile = tmx.tmxfile()
        assert tmxfile.translate("Anything") is None
        tmxfile.addtranslation(
            "A string of characters", "en", "'n String karakters", "af"
        )
        assert tmxfile.translate("A string of characters") == "'n String karakters"

    def test_multilingual_configured_language_selection(self) -> None:
        store = tmx.tmxfile(
            BytesIO(self.multilingual_tmx().encode()),
            sourcelanguage="de",
            targetlanguage="en",
        )

        assert store.sourcelanguage == "de"
        assert store.targetlanguage == "en"
        assert [(unit.source, unit.target) for unit in store.units] == [
            ("test1_de", "test1_en"),
            ("test2_de", "test2_en"),
        ]
        assert store.translate("test1_de") == "test1_en"
        assert store.translate("test1_ar", sourcelang="ar", targetlang="de") == (
            "test1_de"
        )
        assert store.translate("test1", sourcelang="de", targetlang="en") is None
        assert store.findid("test1").gettarget("en") == "test1_en"

    def test_multilingual_parsestring_language_selection(self) -> None:
        store = tmx.tmxfile.parsestring(
            self.multilingual_tmx(), sourcelanguage="de", targetlanguage="ar"
        )

        assert store.units[0].source == "test1_de"
        assert store.units[0].target == "test1_ar"

    def test_multilingual_header_language_and_target_fallback(self) -> None:
        store = tmx.tmxfile.parsestring(self.multilingual_tmx())

        assert store.sourcelanguage == "en"
        assert store.targetlanguage is None
        assert [(unit.source, unit.target) for unit in store.units] == [
            ("test1_en", "test1_de"),
            ("test2_en", "test2_de"),
        ]
        assert store.translate("test1_en") == "test1_de"

    def test_translation_unit_source_language_precedence(self) -> None:
        source = self.language_selection_tmx(
            """        <tu tuid="test" srclang="ar">
            <tuv xml:lang="en"><seg>English</seg></tuv>
            <tuv xml:lang="de"><seg>Deutsch</seg></tuv>
            <tuv xml:lang="ar"><seg>Arabic</seg></tuv>
        </tu>"""
        )

        store = tmx.tmxfile.parsestring(source)
        assert store.units[0].source == "Arabic"
        assert store.units[0].target == "Deutsch"

        store = tmx.tmxfile.parsestring(
            source, sourcelanguage="de", targetlanguage="en"
        )
        assert store.units[0].source == "Deutsch"
        assert store.units[0].target == "English"

    def test_all_source_languages_use_order_fallback(self) -> None:
        source = self.language_selection_tmx(
            """        <tu tuid="test" srclang="*all*">
            <tuv xml:lang="ar"><seg>Arabic</seg></tuv>
            <tuv xml:lang="de"><seg>Deutsch</seg></tuv>
            <tuv xml:lang="en"><seg>English</seg></tuv>
        </tu>"""
        )

        unit = tmx.tmxfile.parsestring(source).units[0]
        assert unit.source == "Arabic"
        assert unit.target == "Deutsch"

    def test_language_matching_normalizes_case_and_separator(self) -> None:
        source = self.language_selection_tmx(
            """        <tu tuid="test">
            <tuv xml:lang="de-DE"><seg>Farbe</seg></tuv>
            <tuv xml:lang="EN-us"><seg>color</seg></tuv>
        </tu>""",
            srclang="de-DE",
        )

        store = tmx.tmxfile.parsestring(
            source, sourcelanguage="de_de", targetlanguage="en_US"
        )
        assert store.units[0].source == "Farbe"
        assert store.units[0].target == "color"
        assert store.translate("Farbe", sourcelang="DE-de", targetlang="en_us") == (
            "color"
        )

        store = tmx.tmxfile.parsestring(source, sourcelanguage="de")
        assert store.units[0].source is None

    def test_missing_configured_language_does_not_fallback(self) -> None:
        store = tmx.tmxfile.parsestring(
            self.multilingual_tmx(), sourcelanguage="fr", targetlanguage="es"
        )

        assert store.units[0].source is None
        assert store.units[0].target is None
        assert store.translate("test1_en", sourcelang="en", targetlang="es") is None

    def test_multilingual_setters_preserve_other_languages(self) -> None:
        store = tmx.tmxfile.parsestring(
            self.multilingual_tmx(), sourcelanguage="en", targetlanguage="ar"
        )
        unit = store.units[0]

        unit.source = "updated English"
        unit.target = "updated Arabic"

        assert unit.gettarget("en") == "updated English"
        assert unit.gettarget("ar") == "updated Arabic"
        assert unit.gettarget("de") == "test1_de"

    def test_language_change_invalidates_indexes(self) -> None:
        store = tmx.tmxfile.parsestring(
            self.multilingual_tmx(), sourcelanguage="en", targetlanguage="de"
        )
        assert store.translate("test1_en") == "test1_de"

        store.setsourcelanguage("ar")
        store.settargetlanguage("en")

        assert store.translate("test1_ar") == "test1_en"

    def test_addtranslation_non_english_source_is_selectable(self) -> None:
        tmxfile = tmx.tmxfile()

        tmxfile.addtranslation("bonjour", "fr", "hallo", "de")

        assert tmxfile.sourcelanguage == "en"
        assert tmxfile.translate("bonjour") == "hallo"

    def test_addtranslation_with_explicit_store_languages_keeps_text_order(
        self,
    ) -> None:
        tmxfile = tmx.tmxfile(sourcelanguage="en", targetlanguage="de")

        tmxfile.addtranslation("bonjour", "fr", "hallo", "de")

        unit = tmxfile.units[0]
        assert unit.gettarget("fr") == "bonjour"
        assert unit.gettarget("de") == "hallo"

    def test_addtranslation_target_language_matching_source_is_preserved(
        self,
    ) -> None:
        tmxfile = tmx.tmxfile(sourcelanguage="en", targetlanguage="de")

        tmxfile.addtranslation("hallo", "de", "bonjour", "fr")

        unit = tmxfile.units[0]
        assert unit.gettarget("de") == "hallo"
        assert unit.gettarget("fr") == "bonjour"

    def test_addtranslation_keeps_existing_implicit_source_selection(self) -> None:
        store = tmx.tmxfile.parsestring(self.multilingual_tmx())

        store.addtranslation("bonjour", "fr", "hallo", "de")

        assert store.sourcelanguage == "en"
        assert store.units[0].source == "test1_en"
        assert store.translate("bonjour", sourcelang="fr", targetlang="de") == "hallo"

    def test_unit_source_setter_preserves_unit_source_language(self) -> None:
        source = self.language_selection_tmx(
            """        <tu tuid="test" srclang="ar">
            <tuv xml:lang="en"><seg>English</seg></tuv>
            <tuv xml:lang="ar"><seg>Arabic</seg></tuv>
        </tu>"""
        )
        store = tmx.tmxfile.parsestring(source)
        unit = store.units[0]

        unit.source = "Updated Arabic"

        assert unit.gettarget("ar") == "Updated Arabic"
        assert unit.source == "Updated Arabic"
        assert unit.gettarget("en") == "English"

    def test_language_index_is_invalidated_when_variant_text_changes(self) -> None:
        store = tmx.tmxfile.parsestring(
            self.multilingual_tmx(), sourcelanguage="en", targetlanguage="de"
        )
        assert store.translate("test1_de", sourcelang="de", targetlang="en") == (
            "test1_en"
        )

        store.units[0].settarget("Guten Tag", "de")

        assert store.translate("Guten Tag", sourcelang="de", targetlang="en") == (
            "test1_en"
        )
        assert store.translate("test1_de", sourcelang="de", targetlang="en") is None

    def test_new_target_is_inserted_after_tu_metadata(self) -> None:
        source = self.language_selection_tmx(
            """        <tu tuid="test">
            <note>Note</note>
            <prop type="x-context">Context</prop>
            <tuv xml:lang="en"><seg>English</seg></tuv>
        </tu>""",
            srclang="fr",
        )
        store = tmx.tmxfile.parsestring(
            source, sourcelanguage="ar", targetlanguage="de"
        )

        store.units[0].target = "Deutsch"

        assert [
            child.tag.rsplit("}", 1)[-1] for child in store.units[0].xmlelement
        ] == [
            "note",
            "prop",
            "tuv",
            "tuv",
        ]
        assert store.units[0].gettarget("de") == "Deutsch"

    def test_missing_source_target_preserves_order_fallback(self) -> None:
        source = self.language_selection_tmx(
            """        <tu tuid="test">
            <tuv xml:lang="de"><seg>Farbe</seg></tuv>
        </tu>""",
            srclang="*all*",
        )
        store = tmx.tmxfile.parsestring(
            source, sourcelanguage="en", targetlanguage="fr"
        )
        unit = store.units[0]

        assert unit.source is None
        unit.target = "couleur"

        reparsed = tmx.tmxfile.parsestring(bytes(store))
        assert reparsed.units[0].source == "Farbe"
        assert reparsed.units[0].target == "couleur"

    def test_translate_fallback_excludes_per_call_source_language(self) -> None:
        source = self.language_selection_tmx(
            """        <tu tuid="test">
            <tuv xml:lang="ar"><seg>Arabic</seg></tuv>
            <tuv xml:lang="en"><seg>English</seg></tuv>
        </tu>"""
        )
        store = tmx.tmxfile.parsestring(source)

        assert store.translate("Arabic", sourcelang="ar") == "English"

    def test_addtranslation(self) -> None:
        """Tests that addtranslation() stores strings correctly."""
        tmxfile = tmx.tmxfile()
        tmxfile.addtranslation(
            "A string of characters", "en", "'n String karakters", "af"
        )
        newfile = self.tmxparse(bytes(tmxfile))
        print(bytes(tmxfile))
        assert newfile.translate("A string of characters") == "'n String karakters"

    def test_withcomment(self) -> None:
        """Tests that addtranslation() stores string's comments correctly."""
        tmxfile = tmx.tmxfile()
        tmxfile.addtranslation(
            "A string of chars", "en", "'n String karakters", "af", "comment"
        )
        newfile = self.tmxparse(bytes(tmxfile))
        print(bytes(tmxfile))
        assert newfile.findunit("A string of chars").getnotes() == "comment"

    def test_withnewlines(self) -> None:
        """Test addtranslation() with newlines."""
        tmxfile = tmx.tmxfile()
        tmxfile.addtranslation(
            "First line\nSecond line", "en", "Eerste lyn\nTweede lyn", "af"
        )
        newfile = self.tmxparse(bytes(tmxfile))
        print(bytes(tmxfile))
        assert newfile.translate("First line\nSecond line") == "Eerste lyn\nTweede lyn"

    def test_xmlentities(self) -> None:
        """Test that the xml entities '&' and '<'  are escaped correctly."""
        tmxfile = tmx.tmxfile()
        tmxfile.addtranslation("Mail & News", "en", "Nuus & pos", "af")
        tmxfile.addtranslation("Five < ten", "en", "Vyf < tien", "af")
        xmltext = bytes(tmxfile).decode("utf-8")
        print("The generated xml:")
        print(xmltext)
        assert tmxfile.translate("Mail & News") == "Nuus & pos"
        assert xmltext.index("Mail &amp; News")
        assert xmltext.find("Mail & News") == -1
        assert tmxfile.translate("Five < ten") == "Vyf < tien"
        assert xmltext.index("Five &lt; ten")
        assert xmltext.find("Five < ten") == -1

    def test_controls_cleaning(self) -> None:
        """Test addtranslation() with control chars."""
        tmxfile = tmx.tmxfile()
        tmxfile.addtranslation("Client Version:\x0314 %s", "en", "test one", "ar")
        tmxfile.addtranslation("Client Version:\n%s", "en", "test two", "ar")
        newfile = self.tmxparse(bytes(tmxfile))
        print(bytes(tmxfile))
        assert newfile.translate("Client Version:14 %s") == "test one"
        assert newfile.translate("Client Version:\n%s") == "test two"

    def test_context(self) -> None:
        store = self.StoreClass()
        unit = store.addsourceunit("Source text")
        unit.target = "Target text"
        unit.setcontext("Context text")
        store.addunit(unit)
        assert b"Context text" in (bytes(store))

        newsource = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE tmx
  SYSTEM 'tmx14.dtd'>
<tmx version="1.4">
        <header adminlang="en" creationtool="Translate Toolkit" creationtoolversion="1.0beta" datatype="PlainText" o-tmf="UTF-8" segtype="sentence" srclang="en"/>
        <body>
                <tu>
                        <prop type="x-context">Context text</prop>
                        <tuv xml:lang="en">
                                <seg>Test String</seg>
                        </tuv>
                </tu>
        </body>
</tmx>"""

        newstore = self.StoreClass().parsestring(newsource)
        assert newstore.units[0].getcontext() == "Context text"

    def test_note_order(self) -> None:
        """Test that notes appear before tuv elements as per TMX DTD."""
        store = self.StoreClass()
        unit = store.addsourceunit("Test")
        unit.target = "Prueba"
        unit.addnote("Test note")

        # Get the order of elements
        element_tags = [
            child.tag.split("}")[1] if "}" in child.tag else child.tag
            for child in unit.xmlelement
        ]

        # Note should come before tuv elements
        assert "note" in element_tags
        assert "tuv" in element_tags
        note_index = element_tags.index("note")
        first_tuv_index = element_tags.index("tuv")
        assert note_index < first_tuv_index, (
            "note element should appear before tuv elements"
        )

    def test_prop_and_note_order(self) -> None:
        """Test that notes and props appear before tuv elements as per TMX DTD."""
        store = self.StoreClass()
        unit = store.addsourceunit("Test")
        unit.target = "Prueba"
        unit.addnote("Test note")
        unit.setcontext("test-context")

        # Get the order of elements
        element_tags = [
            child.tag.split("}")[1] if "}" in child.tag else child.tag
            for child in unit.xmlelement
        ]

        # Both note and prop should come before tuv elements
        assert "note" in element_tags
        assert "prop" in element_tags
        assert "tuv" in element_tags

        note_index = element_tags.index("note")
        prop_index = element_tags.index("prop")
        first_tuv_index = element_tags.index("tuv")

        assert note_index < first_tuv_index, (
            "note element should appear before tuv elements"
        )
        assert prop_index < first_tuv_index, (
            "prop element should appear before tuv elements"
        )
