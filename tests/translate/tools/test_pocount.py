import subprocess
import sys
from io import BytesIO

from pytest import CaptureFixture, mark, param

from translate.storage import po
from translate.tools import pocount

# For now test files left in the old places, but it's better to move
# them somewhere like tests/data.
_po_csv, _po_file, _po_fuzzy = test_files = [
    "tests/cli/data/test_pocount_po_csv/one.po",
    "tests/cli/data/test_pocount_po_file/one.po",
    "tests/cli/data/test_pocount_po_fuzzy/one.po",
]
_xliff_states_yes = "tests/cli/data/test_pocount_xliff_states_yes/states.xlf"
_xliff_states_no = "tests/cli/data/test_pocount_xliff_states_no/states.xlf"


class TestCount:
    @staticmethod
    def count(source, expectedsource, target=None, expectedtarget=None) -> None:
        """Simple helper to check the respective word counts."""
        poelement = po.pounit(source)
        if target is not None:
            poelement.target = target
        wordssource, wordstarget = pocount.wordsinunit(poelement)
        print(f'Source (expected={expectedsource}; actual={wordssource}): "{source}"')
        assert wordssource == expectedsource
        if target is not None:
            print(
                f'Target (expected={expectedtarget}; actual={wordstarget}): "{target}"'
            )
            assert wordstarget == expectedtarget

    def test_simple_count_zero(self) -> None:
        """No content."""
        self.count("", 0)

    def test_simple_count_one(self) -> None:
        """Simplest one word count."""
        self.count("One", 1)

    def test_simple_count_two(self) -> None:
        """Simplest one word count."""
        self.count("One two", 2)

    def test_punctuation_divides_words(self) -> None:
        """Test that we break words when there is punctuation."""
        self.count("One. Two", 2)
        self.count("One.Two", 2)

    def test_xml_tags(self) -> None:
        """Test that we do not count XML tags as words."""
        # <br> is a word break
        self.count("A word<br>Another word", 4)
        self.count("A word<br/>Another word", 4)
        self.count("A word<br />Another word", 4)
        # \n is a word break
        self.count("<p>A word</p>\n<p>Another word</p>", 4)
        # Not really an XML tag
        self.count("<no label>", 2)

    def test_newlines(self) -> None:
        """Test to see that newlines divide words."""
        # newlines break words
        self.count("A word.\nAnother word", 4)
        self.count(r"A word.\\n\nAnother word", 5)

    def test_variables_are_words(self) -> None:
        """Test that we count variables as words."""
        self.count("%PROGRAMNAME %PROGRAM% %s $file $1", 5)

    def test_plurals(self) -> None:
        """Test that we can handle plural PO elements."""
        # #: gdk-pixbuf/gdk-pixdata.c:430
        # #, c-format
        # msgid "failed to allocate image buffer of %u byte"
        # msgid_plural "failed to allocate image buffer of %u bytes"
        # msgstr[0] "e paletšwe go hwetša sešireletši sa seswantšho sa paete ya %u"
        # msgstr[1] "e paletšwe go hwetša sešireletši sa seswantšho sa dipaete tša %u"

    @mark.xfail(reason="Support commented out pending removal")
    def test_plurals_kde(self) -> None:
        """Test that we correctly count old style KDE plurals."""
        self.count("_n: Singular\\n\nPlural", 2, "Een\\n\ntwee\\n\ndrie", 3)

    def test_msgid_blank(self) -> None:
        """Counts a message id."""
        self.count("   ", 0)

    # Counting strings
    #  We need to check how we count strings also and if we call it translated or untranslated
    # ie an all spaces msgid should be translated if there are spaces in the msgstr

    # Make sure we don't count obsolete messages

    # Do we correctly identify a translated yet blank message?

    # Need to test that we can differentiate between fuzzy, translated and untranslated


class TestPOCount:
    """This only tests the old (memory-based) pocount method."""

    inputdata = rb"""
msgid "translated unit"
msgstr "translated unit"

#, fuzzy
msgid "fuzzy unit"
msgstr "fuzzy unit"

# untranslated
msgid "untranslated unit"
msgstr ""

# obsolete
#~ msgid "obsolete translated unit"
#~ msgstr "obsolete translated unit"

#, fuzzy
#~ msgid "obsolete fuzzy unit"
#~ msgstr "obsolete fuzzy unit"

# untranslated
#~ msgid "obsolete untranslated unit"
#~ msgstr ""
"""

    def test_translated(self) -> None:
        pofile = BytesIO(self.inputdata)
        stats = pocount.calcstats(pofile)
        assert stats["translated"] == 1

    def test_fuzzy(self) -> None:
        pofile = BytesIO(self.inputdata)
        stats = pocount.calcstats(pofile)
        assert stats["fuzzy"] == 1

    def test_untranslated(self) -> None:
        pofile = BytesIO(self.inputdata)
        stats = pocount.calcstats(pofile)
        assert stats["untranslated"] == 1

    def test_total(self) -> None:
        pofile = BytesIO(self.inputdata)
        stats = pocount.calcstats(pofile)
        assert stats["total"] == 3

    def test_translatedsourcewords(self) -> None:
        pofile = BytesIO(self.inputdata)
        stats = pocount.calcstats(pofile)
        assert stats["translatedsourcewords"] == 2

    def test_fuzzysourcewords(self) -> None:
        pofile = BytesIO(self.inputdata)
        stats = pocount.calcstats(pofile)
        assert stats["fuzzysourcewords"] == 2

    def test_untranslatedsourcewords(self) -> None:
        pofile = BytesIO(self.inputdata)
        stats = pocount.calcstats(pofile)
        assert stats["untranslatedsourcewords"] == 2

    def test_totalsourcewords(self) -> None:
        pofile = BytesIO(self.inputdata)
        stats = pocount.calcstats(pofile)
        assert stats["totalsourcewords"] == 6


@mark.parametrize("style", ["csv", "full", "short-strings", "short-words"])
@mark.parametrize("incomplete", [True, False], ids=lambda v: f"incomplete={v}")
@mark.parametrize("no_color", [True, False], ids=lambda v: f"no-color={v}")
def test_output(
    style, incomplete, no_color, capsys: CaptureFixture[str], snapshot
) -> None:
    opts = [f"--{style}"]
    if incomplete:
        opts.append("--incomplete")
    if no_color:
        opts.append("--no-color")

    pocount.main([*opts, *test_files])
    stdout = capsys.readouterr()[0]

    assert stdout == snapshot


@mark.parametrize(
    "opts",
    [
        param([_po_file, "--no-color"], id="po-file"),
        param([_po_fuzzy, "--no-color"], id="po-file-fuzzy"),
        param([_po_csv, "--no-color", "--csv"], id="po-file-csv"),
        param([_xliff_states_yes, "--no-color"], id="xliff-states-yes"),
        param([_xliff_states_no, "--no-color"], id="xliff-states-no"),
    ],
)
def test_cases(opts, capsys: CaptureFixture[str], snapshot) -> None:
    pocount.main(opts)

    result = capsys.readouterr()

    assert result == snapshot


@mark.parametrize(
    ("opts", "expected"),
    [
        param(
            ["--csv", "--short"],
            "argument --short: not allowed with argument --csv",
            id="mutually-exclusive",
        ),
        param(
            ["missing.po"],
            "cannot process missing.po: does not exist",
            id="missing-file",
        ),
        param([], "the following arguments are required: files", id="no-args"),
    ],
)
def test_error_cases(opts, expected) -> None:
    # We're using special case for this, to produce correct output.
    # Also, using partial matching instead of snapshots, because mac-os argparse
    # output is slightly different.
    result = subprocess.run(
        [sys.executable, pocount.__file__, *opts],
        capture_output=True,
        text=True,
        check=False,
    )  # ty:ignore[no-matching-overload]

    assert expected in result.stderr


def test_csv_line_terminator(capsys: CaptureFixture[str]) -> None:
    """Test that CSV output uses Unix line terminators without extra carriage returns."""
    pocount.main(["--csv", _po_csv])

    result = capsys.readouterr()
    stdout = result.out

    # Check that there are no carriage returns in the output
    # On Windows, csv.DictWriter with default lineterminator would add \r\n
    # which when redirected to a file becomes \r\r\n, causing empty lines
    assert "\r" not in stdout, "CSV output should not contain carriage returns"

    # Verify that lines end with just \n
    lines = stdout.split("\n")
    # Filter out the last empty line if present
    lines = [line for line in lines if line]

    # Should have at least header and one data row
    assert len(lines) >= 2, "CSV should have at least header and one data row"

    # Each line should not be empty
    for line in lines:
        assert line.strip(), "No line should be empty or whitespace-only"


class TestPOCountCategorization:
    """Test that units are categorized correctly."""

    def test_fuzzy_with_target(self) -> None:
        """Test that fuzzy units with targets are counted as fuzzy, not translated."""
        inputdata = rb"""
msgid "test"
msgstr ""

#, fuzzy
msgid "fuzzy unit"
msgstr "fuzzy translation"
"""
        pofile = BytesIO(inputdata)
        stats = pocount.calcstats(pofile)
        assert stats["fuzzy"] == 1
        assert stats["translated"] == 0
        assert stats["untranslated"] == 1

    def test_fuzzy_without_target(self) -> None:
        """Test that fuzzy units without targets are counted as untranslated."""
        inputdata = rb"""
#, fuzzy
msgid "fuzzy unit"
msgstr ""
"""
        pofile = BytesIO(inputdata)
        stats = pocount.calcstats(pofile)
        assert stats["fuzzy"] == 0
        assert stats["translated"] == 0
        assert stats["untranslated"] == 1

    def test_translated_not_fuzzy(self) -> None:
        """Test that translated units without fuzzy flag are counted as translated."""
        inputdata = rb"""
msgid "test"
msgstr "translation"
"""
        pofile = BytesIO(inputdata)
        stats = pocount.calcstats(pofile)
        assert stats["translated"] == 1
        assert stats["fuzzy"] == 0
        assert stats["untranslated"] == 0

    def test_untranslated_empty_target(self) -> None:
        """Test that units with empty targets are counted as untranslated."""
        inputdata = rb"""
msgid "test"
msgstr ""
"""
        pofile = BytesIO(inputdata)
        stats = pocount.calcstats(pofile)
        assert stats["translated"] == 0
        assert stats["fuzzy"] == 0
        assert stats["untranslated"] == 1

    def test_categorization_mutually_exclusive(self) -> None:
        """Test that each unit is counted in exactly one category."""
        inputdata = rb"""
msgid "translated"
msgstr "translation"

#, fuzzy
msgid "fuzzy"
msgstr "fuzzy translation"

msgid "untranslated"
msgstr ""
"""
        pofile = BytesIO(inputdata)
        stats = pocount.calcstats(pofile)
        # Each unit should be in exactly one category
        assert stats["translated"] == 1
        assert stats["fuzzy"] == 1
        assert stats["untranslated"] == 1
        # Total should equal the sum
        assert (
            stats["total"]
            == stats["translated"] + stats["fuzzy"] + stats["untranslated"]
        )


class TestPOCountLineEndings:
    """Test pocount handles files with unusual line endings."""

    def test_unusual_line_endings(self) -> None:
        r"""Test file with \r\r\n line endings."""
        # f43.tgif.fr.po has unusual \r\r\n line endings
        stats = pocount.calcstats(
            "tests/translate/tools/data/pocount_syntax_errors/f43.tgif.fr.po"
        )
        # Should parse successfully
        assert stats
        # File has 321 translated messages (verified with msgfmt)
        assert stats["total"] == 321
        assert stats["translated"] == 321
