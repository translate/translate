import subprocess
import sys
from io import BytesIO

from pytest import CaptureFixture, mark, param

from translate.storage import po
from translate.tools import pocount

# For now test files left in the old places, but it's better to move
# them somwhere like tests/data.
_po_csv, _po_file, _po_fuzzy = test_files = [
    "tests/cli/data/test_pocount_po_csv/one.po",
    "tests/cli/data/test_pocount_po_file/one.po",
    "tests/cli/data/test_pocount_po_fuzzy/one.po",
]
_xliff_states_yes = "tests/cli/data/test_pocount_xliff_states_yes/states.xlf"
_xliff_states_no = "tests/cli/data/test_pocount_xliff_states_no/states.xlf"


class TestCount:
    @staticmethod
    def count(source, expectedsource, target=None, expectedtarget=None):
        """Simple helper to check the respective word counts."""
        poelement = po.pounit(source)
        if target is not None:
            poelement.target = target
        wordssource, wordstarget = pocount.wordsinunit(poelement)
        print(
            'Source (expected=%d; actual=%d): "%s"'
            % (expectedsource, wordssource, source)
        )
        assert wordssource == expectedsource
        if target is not None:
            print(
                'Target (expected=%d; actual=%d): "%s"'
                % (expectedtarget, wordstarget, target)
            )
            assert wordstarget == expectedtarget

    def test_simple_count_zero(self):
        """No content."""
        self.count("", 0)

    def test_simple_count_one(self):
        """Simplest one word count."""
        self.count("One", 1)

    def test_simple_count_two(self):
        """Simplest one word count."""
        self.count("One two", 2)

    def test_punctuation_divides_words(self):
        """Test that we break words when there is punctuation."""
        self.count("One. Two", 2)
        self.count("One.Two", 2)

    def test_xml_tags(self):
        """Test that we do not count XML tags as words."""
        # <br> is a word break
        self.count("A word<br>Another word", 4)
        self.count("A word<br/>Another word", 4)
        self.count("A word<br />Another word", 4)
        # \n is a word break
        self.count("<p>A word</p>\n<p>Another word</p>", 4)
        # Not really an XML tag
        self.count("<no label>", 2)

    def test_newlines(self):
        """Test to see that newlines divide words."""
        # newlines break words
        self.count("A word.\nAnother word", 4)
        self.count(r"A word.\\n\nAnother word", 4)

    def test_variables_are_words(self):
        """Test that we count variables as words."""
        self.count("%PROGRAMNAME %PROGRAM% %s $file $1", 5)

    def test_plurals(self):
        """Test that we can handle plural PO elements."""
        # #: gdk-pixbuf/gdk-pixdata.c:430
        # #, c-format
        # msgid "failed to allocate image buffer of %u byte"
        # msgid_plural "failed to allocate image buffer of %u bytes"
        # msgstr[0] "e paletšwe go hwetša sešireletši sa seswantšho sa paete ya %u"
        # msgstr[1] "e paletšwe go hwetša sešireletši sa seswantšho sa dipaete tša %u"

    @mark.xfail(reason="Support commented out pending removal")
    def test_plurals_kde(self):
        """Test that we correcly count old style KDE plurals."""
        self.count("_n: Singular\\n\nPlural", 2, "Een\\n\ntwee\\n\ndrie", 3)

    def test_msgid_blank(self):
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

    def test_translated(self):
        pofile = BytesIO(self.inputdata)
        stats = pocount.calcstats(pofile)
        assert stats["translated"] == 1

    def test_fuzzy(self):
        pofile = BytesIO(self.inputdata)
        stats = pocount.calcstats(pofile)
        assert stats["fuzzy"] == 1

    def test_untranslated(self):
        pofile = BytesIO(self.inputdata)
        stats = pocount.calcstats(pofile)
        assert stats["untranslated"] == 1

    def test_total(self):
        pofile = BytesIO(self.inputdata)
        stats = pocount.calcstats(pofile)
        assert stats["total"] == 3

    def test_translatedsourcewords(self):
        pofile = BytesIO(self.inputdata)
        stats = pocount.calcstats(pofile)
        assert stats["translatedsourcewords"] == 2

    def test_fuzzysourcewords(self):
        pofile = BytesIO(self.inputdata)
        stats = pocount.calcstats(pofile)
        assert stats["fuzzysourcewords"] == 2

    def test_untranslatedsourcewords(self):
        pofile = BytesIO(self.inputdata)
        stats = pocount.calcstats(pofile)
        assert stats["untranslatedsourcewords"] == 2

    def test_totalsourcewords(self):
        pofile = BytesIO(self.inputdata)
        stats = pocount.calcstats(pofile)
        assert stats["totalsourcewords"] == 6


@mark.parametrize("style", ["csv", "full", "short-strings", "short-words"])
@mark.parametrize("incomplete", [True, False], ids=lambda v: f"incomplete={v}")
@mark.parametrize("no_color", [True, False], ids=lambda v: f"no-color={v}")
def test_output(style, incomplete, no_color, capsys: CaptureFixture[str], snapshot):
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
def test_cases(opts, capsys: CaptureFixture[str], snapshot):
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
def test_error_cases(opts, expected):
    # We're using special case for this, to produce correct output.
    # Also, using partial matching instead of snapshots, becouse mac-os argparse
    # output is slightly different.
    result = subprocess.run(
        [sys.executable, pocount.__file__, *opts],
        capture_output=True,
        text=True,
    )

    assert expected in result.stderr
