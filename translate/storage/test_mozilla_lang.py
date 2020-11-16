import io

import pytest

from translate.storage import mozilla_lang, test_base


@pytest.mark.parametrize(
    "orig, stripped",
    [
        ("", ""),
        ("String", "String"),  # No {ok}
        ("String {ok}", "String"),  # correct form
        ("String {OK}", "String"),  # capitals
        ("Şŧřīƞɠ {ok}", "Şŧřīƞɠ"),  # Unicode
        ("String{ok}", "String"),  # No leading space
        ("String{OK}", "String"),  # Caps no leading space
        ("String  {ok}", "String"),  # multispace leading
        ("String {ok} ", "String"),  # trailing space
    ],
)
def test_strip_ok(orig, stripped):
    """Test various permutations of {ok} stripping"""
    assert mozilla_lang.strip_ok(orig) == stripped


class TestMozLangUnit(test_base.TestTranslationUnit):
    UnitClass = mozilla_lang.LangUnit

    def test_translate_but_same(self):
        """
        Mozilla allows {ok} to indicate a line that is the
        same in source and target on purpose
        """
        unit = self.UnitClass("Open")
        unit.target = "Open"
        assert unit.target == "Open"
        assert str(unit).endswith(" {ok}")

    def test_untranslated(self):
        """
        The target is always written to files and is never blank. If it is
        truly untranslated then it won't end with '{ok}.
        """
        unit = self.UnitClass("Open")
        assert unit.target is None
        assert str(unit).find("Open") == 1
        assert str(unit).find("Open", 2) == 6
        assert not str(unit).endswith(" {ok}")

        unit = self.UnitClass("Closed")
        unit.target = ""
        assert unit.target == ""
        assert str(unit).find("Closed") == 1
        assert str(unit).find("Closed", 2) == 8
        assert not str(unit).endswith(" {ok}")

    def test_comments(self):
        """Comments start with #, tags start with ## TAG:."""
        unit = self.UnitClass("One")
        unit.addnote("Hello")
        assert str(unit).find("Hello") == 2
        assert str(unit).find("# Hello") == 0
        unit.addnote("# TAG: goodbye")
        assert "# TAG: goodbye" in unit.getnotes(origin="developer").split("\n")

    def test_copy_target(self):
        """Validate that self.rawtarget does not break a valid translation.

        self.rawtarget is used to preserve strange format anomalies related to
        {ok}.  But when units got translated it sometimes caused issues, in
        that the unit was correctly translated but when serialised it used
        self.rawtarget and thus output an untranslated unit.  This checks that
        translation actually results in rawformat being ignored.
        """
        unit = self.UnitClass("Device")
        unit.target == ""
        unit.rawtarget = "Device"
        assert not unit.istranslated()
        assert str(unit) == ";Device\nDevice"

        other = self.UnitClass("Device")
        other.target = "Device"
        assert other.istranslated()
        assert str(other) == ";Device\nDevice {ok}"

        unit.target = other.target
        assert unit.istranslated()
        assert unit.target == "Device"
        assert str(unit) == ";Device\nDevice {ok}"


class TestMozLangFile(test_base.TestTranslationStore):
    StoreClass = mozilla_lang.LangStore

    def test_nonascii(self):
        # FIXME investigate why this doesn't pass or why we even do this
        # text with UTF-8 encoded strings
        pass

    def test_format_layout(self):
        """General test of layout of the format"""
        lang = "# Comment\n" ";Source\n" "Target\n" "\n\n"
        store = self.StoreClass.parsestring(lang)
        store.mark_active = False
        unit = store.units[0]
        assert unit.source == "Source"
        assert unit.target == "Target"
        assert "Comment" in unit.getnotes()
        assert bytes(store).decode("utf-8") == lang

    def test_crlf(self):
        r"""While \n is preferred \r\n is allowed"""
        lang = "# Comment\r\n" ";Source\r\n" "Target\r\n" "\r\n\r\n"
        store = self.StoreClass.parsestring(lang)
        store.mark_active = False
        unit = store.units[0]
        assert unit.source == "Source"
        assert unit.target == "Target"
        assert "Comment" in unit.getnotes()
        assert bytes(store).decode("utf-8") == lang

    def test_active_flag(self):
        """Test the ## active ## flag"""
        lang = "## active ##\n" ";Source\n" "Target\n" "\n\n"
        store = self.StoreClass.parsestring(lang)
        assert store.is_active
        assert bytes(store).decode("utf-8") == lang

    def test_multiline_comments(self):
        """Ensure we can handle and preserve miltiline comments"""
        lang = (
            "## active ##\n"
            "# First comment\n"
            "# Second comment\n"
            "# Third comment\n"
            ";Source\n"
            "Target\n"
            "\n\n"
        )
        store = self.StoreClass.parsestring(lang)
        assert bytes(store).decode("utf-8") == lang

    def test_template(self):
        """A template should have source == target, though it could be blank"""
        lang = ";Source\n" "Source\n" "\n\n"
        store = self.StoreClass.parsestring(lang)
        unit = store.units[0]
        assert unit.source == "Source"
        assert unit.target == ""
        assert bytes(store).decode("utf-8") == lang
        lang2 = ";Source\n" "\n\n" ";Source2\n" "\n\n"
        store2 = self.StoreClass.parsestring(lang2)
        assert store2.units[0].source == "Source"
        assert store2.units[0].target == ""
        assert store2.units[1].source == "Source2"
        assert store2.units[1].target == ""

    @pytest.mark.parametrize(
        "ok, target, istranslated",
        [
            ("", "", False),  # Untranslated, no {ok}
            (" ", "Source ", True),  # Excess whitespace, translated
            (" {ok}", "Source", True),  # Valid {ok}
            (" {ok} ", "Source", True),  # {ok} trailing WS
            ("{ok}", "Source", True),  # {ok} no WS
        ],
    )
    def test_ok_translations(self, ok, target, istranslated):
        """Various renderings of {ok} to ensure that we parse it correctly"""
        lang = ";Source\n" "Source%s\n"
        store = self.StoreClass.parsestring(lang % ok)
        unit = store.units[0]
        assert unit.source == "Source"
        assert unit.target == target
        assert unit.istranslated() == istranslated

    def test_headers(self):
        """Ensure we can handle and preserve file headers"""
        lang = (
            "## active ##\n"
            "## some_tag ##\n"
            "## another_tag ##\n"
            "## NOTE: foo\n"
            "\n\n"
            ";Source\n"
            "Target\n"
            "\n\n"
        )
        store = self.StoreClass.parsestring(lang)
        assert store.getlangheaders() == [
            "## some_tag ##",
            "## another_tag ##",
            "## NOTE: foo",
            "",
            "",
        ]
        out = io.BytesIO()
        store.serialize(out)
        out.seek(0)
        assert out.read() == str(
            "## active ##\n"
            "## some_tag ##\n"
            "## another_tag ##\n"
            "## NOTE: foo\n"
            "\n\n"
            ";Source\n"
            "Target\n"
            "\n\n"
        ).encode("utf-8")

    def test_not_headers(self):
        """Ensure we dont treat a tag immediately after headers as header"""
        lang = (
            "## active ##\n"
            "## some_tag ##\n"
            "## another_tag ##\n"
            "## NOTE: foo\n"
            "## TAG: fooled_you ##\n"
            ";Source\n"
            "Target\n"
            "\n\n"
        )
        store = self.StoreClass.parsestring(lang)
        assert "## TAG: fooled_you ##" not in store.getlangheaders()

    @pytest.mark.parametrize("nl", [0, 1, 2, 3])
    def test_header_blanklines(self, nl):
        """Ensure that blank lines following a header are recorded"""
        lang_header = "## active ##\n" "## some_tag ##\n"
        lang_unit1 = "# Comment\n" ";Source\n" "Target\n" "\n\n"
        lang = lang_header + "\n" * nl + lang_unit1
        store = self.StoreClass.parsestring(lang)
        assert bytes(store).decode("utf-8") == lang

    def test_tag_comments(self):
        """Ensure we can handle comments and distinguish from headers"""
        lang = (
            "## active ##\n"
            "# First comment\n"
            "## TAG: important_tag\n"
            "# Second comment\n"
            "# Third comment\n"
            "## TAG: another_important_tag\n"
            ";Source\n"
            "Target\n"
            "\n\n"
        )
        store = self.StoreClass.parsestring(lang)
        assert not store.getlangheaders()
        assert bytes(store).decode("utf-8") == lang
        assert "# TAG: important_tag" in store.units[0].getnotes(
            origin="developer"
        ).split("\n")
        lang = (
            "## active ##\n"
            "# First comment\n"
            "## TAG: important_tag\n"
            "# Second comment\n"
            "# Third comment\n"
            "## TAG: another_important_tag\n"
            "# Another comment\n"
            ";Source\n"
            "Target\n"
            "\n\n"
        )
        store = self.StoreClass.parsestring(lang)
        assert not store.getlangheaders()
        assert "First comment" in store.units[0].getnotes(origin="developer").split(
            "\n"
        )
        assert "Second comment" in store.units[0].getnotes(origin="developer").split(
            "\n"
        )
        assert "Another comment" in store.units[0].getnotes(origin="developer").split(
            "\n"
        )
        assert "# TAG: another_important_tag" in store.units[0].getnotes(
            origin="developer"
        ).split("\n")

    def test_maxlength(self):
        """Ensure we can handle MAX_LENGTH meta data"""
        lang = "## MAX_LENGTH: 80\n" "# Comment\n" ";Source\n" "Target\n" "\n\n"
        store = self.StoreClass.parsestring(lang)
        assert not store.getlangheaders()
        assert bytes(store).decode("utf-8") == lang
        assert "# MAX_LENGTH: 80" in store.units[0].getnotes(origin="developer").split(
            "\n"
        )
