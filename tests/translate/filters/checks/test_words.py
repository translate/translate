"""Tests for the checks that inspect the words of a translation."""

from pytest import mark

from tests.translate.filters.checks.helpers import fails, passes
from translate.filters import checks, spelling


def test_acronyms() -> None:
    """Tests acronyms."""
    stdchecker = checks.StandardChecker()
    assert passes(stdchecker.acronyms, "An HTML file", "'n HTML leer")
    assert fails(stdchecker.acronyms, "An HTML file", "'n LMTH leer")
    assert passes(stdchecker.acronyms, "It is HTML.", "Dit is HTML.")
    # We don't mind if you add an acronym to correct bad capitalisation in the original
    assert passes(stdchecker.acronyms, "An html file", "'n HTML leer")
    # We shouldn't worry about acronyms that appear in a musttranslate file
    stdchecker = checks.StandardChecker(checks.CheckerConfig(musttranslatewords=["OK"]))
    assert passes(stdchecker.acronyms, "OK", "Kulungile")
    # Assert punctuation should not hide accronyms
    assert fails(stdchecker.acronyms, "Location (URL) not found", "Blah blah blah")
    # Test '-W' (bug 283)
    assert passes(
        stdchecker.acronyms,
        "%s: option `-W %s' is ambiguous",
        "%s: opsie '-W %s' is dubbelsinnig",
    )


def test_doublewords() -> None:
    """Tests doublewords."""
    stdchecker = checks.StandardChecker()
    assert passes(stdchecker.doublewords, "Save the rhino", "Save the rhino")
    assert fails(stdchecker.doublewords, "Save the rhino", "Save the the rhino")
    # Double variables are not an error
    stdchecker = checks.StandardChecker(checks.CheckerConfig(varmatches=[("%", 1)]))
    assert passes(stdchecker.doublewords, "%s %s installation", "tsenyo ya %s %s")
    # Double XML tags are not an error
    stdchecker = checks.StandardChecker()
    assert passes(
        stdchecker.doublewords,
        "Line one <br> <br> line two",
        "Lyn een <br> <br> lyn twee",
    )
    # In some language certain double words are not errors
    st_checker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="st"))
    assert passes(
        st_checker.doublewords,
        "Color to draw the name of a message you sent.",
        "Mmala wa ho taka bitso la molaetsa oo o o rometseng.",
    )
    assert passes(st_checker.doublewords, "Ten men", "Banna ba ba leshome")
    assert passes(st_checker.doublewords, "Give SARS the tax", "Lekgetho le le fe SARS")


@mark.xfail(reason="FIXME: All fails() tests are not working")
def test_musttranslatewords() -> None:
    """Tests stopwords."""
    stdchecker = checks.StandardChecker(checks.CheckerConfig(musttranslatewords=[]))
    assert passes(
        stdchecker.musttranslatewords,
        "This uses Mozilla of course",
        "hierdie gebruik le mozille natuurlik",
    )
    stdchecker = checks.StandardChecker(
        checks.CheckerConfig(musttranslatewords=["Mozilla"])
    )
    assert passes(
        stdchecker.musttranslatewords,
        "This uses Mozilla of course",
        "hierdie gebruik le mozille natuurlik",
    )
    assert fails(
        stdchecker.musttranslatewords,
        "This uses Mozilla of course",
        "hierdie gebruik Mozilla natuurlik",
    )
    assert passes(
        stdchecker.musttranslatewords,
        "This uses Mozilla. Don't you?",
        "hierdie gebruik le mozille soos jy",
    )
    assert fails(
        stdchecker.musttranslatewords,
        "This uses Mozilla. Don't you?",
        "hierdie gebruik Mozilla soos jy",
    )
    # should always pass if there are no stopwords in the original
    assert passes(
        stdchecker.musttranslatewords,
        "This uses something else. Don't you?",
        "hierdie gebruik Mozilla soos jy",
    )
    # check that we can find words surrounded by punctuation
    assert passes(
        stdchecker.musttranslatewords,
        "Click 'Mozilla' button",
        "Kliek 'Motzille' knoppie",
    )
    assert fails(
        stdchecker.musttranslatewords,
        "Click 'Mozilla' button",
        "Kliek 'Mozilla' knoppie",
    )
    assert passes(
        stdchecker.musttranslatewords,
        'Click "Mozilla" button',
        'Kliek "Motzille" knoppie',
    )
    assert fails(
        stdchecker.musttranslatewords,
        'Click "Mozilla" button',
        'Kliek "Mozilla" knoppie',
    )
    assert fails(
        stdchecker.musttranslatewords,
        'Click "Mozilla" button',
        "Kliek «Mozilla» knoppie",
    )
    assert passes(
        stdchecker.musttranslatewords,
        "Click (Mozilla) button",
        "Kliek (Motzille) knoppie",
    )
    assert fails(
        stdchecker.musttranslatewords,
        "Click (Mozilla) button",
        "Kliek (Mozilla) knoppie",
    )
    assert passes(stdchecker.musttranslatewords, "Click Mozilla!", "Kliek Motzille!")
    assert fails(stdchecker.musttranslatewords, "Click Mozilla!", "Kliek Mozilla!")
    ## We need to define more word separators to allow us to find those hidden untranslated items
    # assert fails(stdchecker.musttranslatewords, "Click OK", "Blah we-OK")
    # Don't get confused when variables are the same as a musttranslate word
    stdchecker = checks.StandardChecker(
        checks.CheckerConfig(
            varmatches=[
                ("%", None),
            ],
            musttranslatewords=["OK"],
        )
    )
    assert passes(
        stdchecker.musttranslatewords, "Click %OK to start", "Kliek %OK om te begin"
    )
    # Unicode
    assert fails(stdchecker.musttranslatewords, "Click OK", "Kiḽikani OK")


def test_notranslatewords() -> None:
    """Tests stopwords."""
    stdchecker = checks.StandardChecker(checks.CheckerConfig(notranslatewords=[]))
    assert passes(
        stdchecker.notranslatewords,
        "This uses Mozilla of course",
        "hierdie gebruik le mozille natuurlik",
    )
    stdchecker = checks.StandardChecker(
        checks.CheckerConfig(notranslatewords=["Mozilla", "Opera"])
    )
    assert fails(
        stdchecker.notranslatewords,
        "This uses Mozilla of course",
        "hierdie gebruik le mozille natuurlik",
    )
    assert passes(
        stdchecker.notranslatewords,
        "This uses Mozilla of course",
        "hierdie gebruik Mozilla natuurlik",
    )
    assert fails(
        stdchecker.notranslatewords,
        "This uses Mozilla. Don't you?",
        "hierdie gebruik le mozille soos jy",
    )
    assert passes(
        stdchecker.notranslatewords,
        "This uses Mozilla. Don't you?",
        "hierdie gebruik Mozilla soos jy",
    )
    # should always pass if there are no stopwords in the original
    assert passes(
        stdchecker.notranslatewords,
        "This uses something else. Don't you?",
        "hierdie gebruik Mozilla soos jy",
    )
    # Cope with commas
    assert passes(
        stdchecker.notranslatewords,
        "using Mozilla Task Manager",
        "šomiša Selaola Mošomo sa Mozilla, gomme",
    )
    # Find words even if they are embedded in punctuation
    assert fails(
        stdchecker.notranslatewords,
        "Click 'Mozilla' button",
        "Kliek 'Motzille' knoppie",
    )
    assert passes(
        stdchecker.notranslatewords, "Click 'Mozilla' button", "Kliek 'Mozilla' knoppie"
    )
    assert fails(stdchecker.notranslatewords, "Click Mozilla!", "Kliek Motzille!")
    assert passes(stdchecker.notranslatewords, "Click Mozilla!", "Kliek Mozilla!")
    assert fails(
        stdchecker.notranslatewords,
        "Searches (From Opera)",
        "adosako (kusukela ku- Ophera)",
    )
    stdchecker = checks.StandardChecker(
        checks.CheckerConfig(notranslatewords=["Sun", "NeXT"])
    )
    assert fails(
        stdchecker.notranslatewords, "Sun/NeXT Audio", "Odio dza Ḓuvha/TeVHELAHO"
    )
    assert passes(stdchecker.notranslatewords, "Sun/NeXT Audio", "Odio dza Sun/NeXT")
    stdchecker = checks.StandardChecker(
        checks.CheckerConfig(notranslatewords=["sendmail"])
    )
    assert fails(
        stdchecker.notranslatewords,
        "because 'sendmail' could",
        "ngauri 'rumelameiḽi' a yo",
    )
    assert passes(
        stdchecker.notranslatewords,
        "because 'sendmail' could",
        "ngauri 'sendmail' a yo",
    )
    stdchecker = checks.StandardChecker(checks.CheckerConfig(notranslatewords=["Base"]))
    assert fails(
        stdchecker.notranslatewords,
        " - %PRODUCTNAME Base: Relation design",
        " - %PRODUCTNAME Sisekelo: Umsiko wekuhlobana",
    )
    stdchecker = checks.StandardChecker(
        checks.CheckerConfig(notranslatewords=["Writer"])
    )
    assert fails(
        stdchecker.notranslatewords,
        "&[ProductName] Writer/Web",
        "&[ProductName] Umbhali/iWebhu",
    )
    # Unicode - different decompositions
    stdchecker = checks.StandardChecker(
        checks.CheckerConfig(notranslatewords=["\u1e3cike"])
    )
    assert passes(
        stdchecker.notranslatewords, "You \u1e3cike me", "Ek \u004c\u032dike jou"
    )


def test_validchars() -> None:
    """Tests valid characters."""
    stdchecker = checks.StandardChecker(checks.CheckerConfig())
    assert passes(
        stdchecker.validchars,
        "The check always passes if you don't specify chars",
        "Die toets sal altyd werk as jy nie karacters specifisier",
    )
    stdchecker = checks.StandardChecker(
        checks.CheckerConfig(
            validchars="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        )
    )
    assert passes(
        stdchecker.validchars,
        "This sentence contains valid characters",
        "Hierdie sin bevat ware karakters",
    )
    assert fails(stdchecker.validchars, "Some unexpected characters", "©®°±÷¼½¾")
    stdchecker = checks.StandardChecker(
        checks.CheckerConfig(
            validchars="⠁⠂⠃⠄⠅⠆⠇⠈⠉⠊⠋⠌⠍⠎⠏⠐⠑⠒⠓⠔⠕⠖⠗⠘⠙⠚⠛⠜⠝⠞⠟⠠⠡⠢⠣⠤⠥⠦⠧⠨⠩⠪⠫⠬⠭⠮⠯⠰"
        )
    )
    assert passes(
        stdchecker.validchars,
        "Our target language is all non-ascii",
        "⠁⠂⠃⠄⠆⠇⠈⠉⠜⠝⠞⠟⠠⠡⠢⠣⠤⠥⠦⠧⠨⠩⠪⠫",
    )
    assert fails(
        stdchecker.validchars,
        "Our target language is all non-ascii",
        "Some ascii⠁⠂⠃⠄⠆⠇⠈⠉⠜⠝⠞⠟⠠⠡⠢⠣⠤⠥⠦⠧⠨⠩⠪⠫",
    )
    stdchecker = checks.StandardChecker(checks.CheckerConfig(validchars="\u004c\u032d"))
    assert passes(
        stdchecker.validchars, "This sentence contains valid chars", "\u004c\u032d"
    )
    assert passes(stdchecker.validchars, "This sentence contains valid chars", "\u1e3c")
    stdchecker = checks.StandardChecker(checks.CheckerConfig(validchars="\u1e3c"))
    assert passes(stdchecker.validchars, "This sentence contains valid chars", "\u1e3c")
    assert passes(
        stdchecker.validchars, "This sentence contains valid chars", "\u004c\u032d"
    )


@mark.skipif(
    not spelling.available or not spelling._get_checker("af"),
    reason="Spell checking for af is not available",
)
def test_spellcheck() -> None:
    """Tests spell checking."""
    stdchecker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="af"))
    assert passes(stdchecker.spellcheck, "Great trek", "Groot trek")
    assert fails(stdchecker.spellcheck, "Final deadline", "End of the road")
    # Bug 289: filters accelerators before spell checking
    stdchecker = checks.StandardChecker(
        checks.CheckerConfig(accelmarkers=["&"], targetlanguage="fi")
    )
    assert passes(stdchecker.spellcheck, "&Reload Frame", "P&äivitä kehys")
    # Ensure we don't check notranslatewords
    stdchecker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="af"))
    assert fails(
        stdchecker.spellcheck, "Mozilla is wonderful", "Mozillaaa is wonderlik"
    )
    # We should pass the test if the "error" occurs in the English
    assert passes(
        stdchecker.spellcheck, "Mozillaxxx is wonderful", "Mozillaxxx is wonderlik"
    )
    stdchecker = checks.StandardChecker(
        checks.CheckerConfig(targetlanguage="af", notranslatewords=["Mozilla"])
    )
    assert passes(stdchecker.spellcheck, "Mozilla is wonderful", "Mozilla is wonderlik")
    # Some variables were still being spell checked
    mozillachecker = checks.MozillaChecker(
        checkerconfig=checks.CheckerConfig(targetlanguage="af")
    )
    assert passes(
        mozillachecker.spellcheck,
        "&brandShortName.labels; is wonderful",
        "&brandShortName.label; is wonderlik",
    )


def test_sentencecount() -> None:
    """Tests sentencecount messages."""
    stdchecker = checks.StandardChecker()
    assert passes(stdchecker.sentencecount, "One. Two. Three.", "Een. Twee. Drie.")
    assert passes(stdchecker.sentencecount, "One two three", "Een twee drie.")
    assert fails(stdchecker.sentencecount, "One. Two. Three.", "Een Twee. Drie.")
    assert passes(
        stdchecker.sentencecount, "Sentence with i.e. in it.", "Sin met d.w.s. in dit."
    )  # bug 178, description item 8
    el_checker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="el"))
    assert fails(
        el_checker.sentencecount,
        "First sentence. Second sentence.",
        "Πρώτη πρόταση. δεύτερη πρόταση.",
    )


def test_simpleplurals() -> None:
    """Test that we can find English style plural(s)."""
    stdchecker = checks.StandardChecker()
    assert passes(stdchecker.simpleplurals, "computer(s)", "rekenaar(s)")
    assert fails(stdchecker.simpleplurals, "plural(s)", "meervoud(e)")
    assert fails(
        stdchecker.simpleplurals,
        "Ungroup Metafile(s)...",
        "Kuvhanganyululani Metafaela(dzi)...",
    )

    # Test a language that doesn't use plurals
    stdchecker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="vi"))
    assert passes(stdchecker.simpleplurals, "computer(s)", "Máy tính")
    assert fails(stdchecker.simpleplurals, "computer(s)", "Máy tính(s)")
