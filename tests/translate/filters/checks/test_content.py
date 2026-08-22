"""Tests for the checks comparing the content of source and target."""

from tests.translate.filters.checks.helpers import fails, passes
from translate.filters import checks


def test_untranslated() -> None:
    """Tests untranslated entries."""
    stdchecker = checks.StandardChecker()
    assert fails(stdchecker.untranslated, "I am untranslated", "")
    assert passes(stdchecker.untranslated, "I am translated", "Ek is vertaal")
    # KDE comments that make it into translations should not mask untranslated test
    assert fails(
        stdchecker.untranslated,
        "_: KDE comment\\n\nI am untranslated",
        "_: KDE comment\\n\n",
    )


def test_unchanged() -> None:
    """Tests unchanged entries."""
    stdchecker = checks.StandardChecker(checks.CheckerConfig(accelmarkers=["&"]))
    assert fails(stdchecker.unchanged, "Unchanged", "Unchanged")
    assert fails(stdchecker.unchanged, "&Unchanged", "Un&changed")
    assert passes(stdchecker.unchanged, "Unchanged", "Changed")
    assert passes(stdchecker.unchanged, "1234", "1234")
    assert passes(stdchecker.unchanged, "2×2", "2×2")  # bug 178, description item 14
    assert passes(stdchecker.unchanged, "I", "I")
    assert passes(stdchecker.unchanged, "   ", "   ")  # bug 178, description item 5
    assert passes(stdchecker.unchanged, "???", "???")  # bug 178, description item 15
    assert passes(
        stdchecker.unchanged, "&ACRONYM", "&ACRONYM"
    )  # bug 178, description item 7
    assert passes(stdchecker.unchanged, "F1", "F1")  # bug 178, description item 20
    assert fails(stdchecker.unchanged, "Two words", "Two words")
    # TODO: this still fails
    #    assert passes(stdchecker.unchanged, "NOMINAL", "NOMİNAL")
    gnomechecker = checks.GnomeChecker()
    assert fails(
        gnomechecker.unchanged,
        "Entity references, such as &amp; and &#169;",
        "Entity references, such as &amp; and &#169;",
    )
    # Variable only and variable plus punctuation messages should be ignored
    mozillachecker = checks.MozillaChecker()
    assert passes(mozillachecker.unchanged, "$ProgramName$", "$ProgramName$")
    assert passes(
        mozillachecker.unchanged, "$file$ : $dir$", "$file$ : $dir$"
    )  # bug 178, description item 13
    assert fails(mozillachecker.unchanged, "$file$ in $dir$", "$file$ in $dir$")
    assert passes(mozillachecker.unchanged, "&brandShortName;", "&brandShortName;")
    # Don't translate words should be ignored
    stdchecker = checks.StandardChecker(
        checks.CheckerConfig(notranslatewords=["Mozilla"])
    )
    assert passes(
        stdchecker.unchanged, "Mozilla", "Mozilla"
    )  # bug 178, description item 10
    # Don't fail unchanged if the entry is a dialogsize, quite plausible that you won't change it
    mozillachecker = checks.MozillaChecker()
    assert passes(mozillachecker.unchanged, "width: 12em;", "width: 12em;")
    assert fails(stdchecker.unchanged, "width: 12em;", "width: 12em;")
    assert passes(mozillachecker.unchanged, "7em", "7em")
    assert fails(stdchecker.unchanged, "7em", "7em")


def test_blank() -> None:
    """Tests blank."""
    stdchecker = checks.StandardChecker()
    assert fails(stdchecker.blank, "Save as", " ")
    assert fails(stdchecker.blank, "_: KDE comment\\n\nSimple string", "  ")


def test_short() -> None:
    """Tests short messages."""
    stdchecker = checks.StandardChecker()
    assert passes(stdchecker.short, "I am normal", "Ek is ook normaal")
    assert fails(stdchecker.short, "I am a very long sentence", "Ek")
    assert fails(stdchecker.short, "abcde", "c")


def test_long() -> None:
    """Tests long messages."""
    stdchecker = checks.StandardChecker()
    assert passes(stdchecker.long, "I am normal", "Ek is ook normaal")
    assert fails(
        stdchecker.long,
        "Short.",
        "Kort.......................................................................................",
    )
    assert fails(stdchecker.long, "a", "bc")


def test_compendiumconflicts() -> None:
    """Tests compendiumconflicts."""
    stdchecker = checks.StandardChecker()
    assert fails(
        stdchecker.compendiumconflicts,
        "File not saved",
        r"""#-#-#-#-# file1.po #-#-#-#-#\n
Leer nie gestoor gestoor nie\n
#-#-#-#-# file1.po #-#-#-#-#\n
Leer nie gestoor""",
    )


def test_kdecomments() -> None:
    """Tests kdecomments."""
    stdchecker = checks.StandardChecker()
    assert passes(
        stdchecker.kdecomments,
        r"""_: I am a comment\n
A string to translate""",
        "'n String om te vertaal",
    )
    assert fails(
        stdchecker.kdecomments,
        r"""_: I am a comment\n
A string to translate""",
        r"""_: Ek is 'n commment\n
'n String om te vertaal""",
    )
    assert fails(
        stdchecker.kdecomments,
        """_: I am a comment\\n\n""",
        """_: I am a comment\\n\n""",
    )


def test_credits() -> None:
    """Tests credits."""
    stdchecker = checks.StandardChecker()
    assert passes(stdchecker.credits, "File", "iFayile")
    assert passes(stdchecker.credits, "&File", "&Fayile")
    assert passes(stdchecker.credits, "translator-credits", "Ekke, ekke!")
    assert passes(stdchecker.credits, "Your names", "Ekke, ekke!")
    assert passes(stdchecker.credits, "ROLES_OF_TRANSLATORS", "Ekke, ekke!")
    kdechecker = checks.KdeChecker()
    assert passes(kdechecker.credits, "File", "iFayile")
    assert passes(kdechecker.credits, "&File", "&Fayile")
    assert passes(kdechecker.credits, "translator-credits", "Ekke, ekke!")
    assert fails(kdechecker.credits, "Your names", "Ekke, ekke!")
    assert fails(kdechecker.credits, "ROLES_OF_TRANSLATORS", "Ekke, ekke!")
    gnomechecker = checks.GnomeChecker()
    assert passes(gnomechecker.credits, "File", "iFayile")
    assert passes(gnomechecker.credits, "&File", "&Fayile")
    assert fails(gnomechecker.credits, "translator-credits", "Ekke, ekke!")
    assert passes(gnomechecker.credits, "Your names", "Ekke, ekke!")
    assert passes(gnomechecker.credits, "ROLES_OF_TRANSLATORS", "Ekke, ekke!")


def test_filepaths() -> None:
    """Tests filepaths."""
    stdchecker = checks.StandardChecker()
    assert passes(
        stdchecker.filepaths,
        "%s to the file /etc/hosts on your system.",
        "%s na die leer /etc/hosts op jou systeem.",
    )
    assert fails(
        stdchecker.filepaths,
        "%s to the file /etc/hosts on your system.",
        "%s na die leer /etc/gasheer op jou systeem.",
    )
    assert passes(
        stdchecker.filepaths, "Text with <br />line break", "Teks met <br /> lynbreuk"
    )


def test_functions() -> None:
    """Tests to see that funtions() are not translated."""
    stdchecker = checks.StandardChecker()
    assert fails(stdchecker.functions, "blah rgb() blah", "blee brg() blee")
    assert passes(stdchecker.functions, "blah rgb() blah", "blee rgb() blee")
    assert fails(stdchecker.functions, "percentage in rgb()", "phesenthe kha brg()")
    assert passes(stdchecker.functions, "percentage in rgb()", "phesenthe kha rgb()")
    assert fails(stdchecker.functions, "rgb() in percentage", "brg() kha phesenthe")
    assert passes(stdchecker.functions, "rgb() in percentage", "rgb() kha phesenthe")
    assert fails(
        stdchecker.functions, "blah string.rgb() blah", "blee bleeb.rgb() blee"
    )
    assert passes(
        stdchecker.functions, "blah string.rgb() blah", "blee string.rgb() blee"
    )
    assert passes(stdchecker.functions, "or domain().", "domain() verwag.")
    assert passes(
        stdchecker.functions,
        "Expected url(), url-prefix(), or domain().",
        "url(), url-prefix() of domain() verwag.",
    )


def test_emails() -> None:
    """Tests to see that email addresses are not translated."""
    stdchecker = checks.StandardChecker()
    assert fails(
        stdchecker.emails, "blah bob@example.net blah", "blee kobus@voorbeeld.net blee"
    )
    assert passes(
        stdchecker.emails, "blah bob@example.net blah", "blee bob@example.net blee"
    )


def test_urls() -> None:
    """Tests to see that URLs are not translated."""
    stdchecker = checks.StandardChecker()
    assert fails(
        stdchecker.urls,
        "blah http://translate.org.za blah",
        "blee http://vertaal.org.za blee",
    )
    assert passes(
        stdchecker.urls,
        "blah http://translate.org.za blah",
        "blee http://translate.org.za blee",
    )


def test_options() -> None:
    """Tests command line options e.g. --option."""
    stdchecker = checks.StandardChecker()
    assert passes(stdchecker.options, "--help", "--help")
    assert fails(stdchecker.options, "--help", "--hulp")
    assert fails(stdchecker.options, "--input=FILE", "--input=FILE")
    assert passes(stdchecker.options, "--input=FILE", "--input=LÊER")
    assert fails(stdchecker.options, "--input=FILE", "--tovoer=LÊER")
    # We don't want just any '--' to trigger this test - the error will be confusing
    assert passes(stdchecker.options, "Hello! -- Hi", "Hallo! &mdash; Haai")
    assert passes(stdchecker.options, "--blank--", "--vide--")
