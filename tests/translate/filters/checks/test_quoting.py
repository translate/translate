"""Tests for the quotation mark checks."""

from pytest import mark

from tests.translate.filters.checks.helpers import fails, passes
from translate.filters import checks


def test_singlequoting() -> None:
    """Tests single quotes."""
    stdchecker = checks.StandardChecker()
    assert passes(stdchecker.singlequoting, "A 'Hot' plate", "Ipuleti 'elishisa' kunye")
    # FIXME this should pass but doesn't probably to do with our logic that got confused at the end of lines
    assert passes(stdchecker.singlequoting, "'Hot' plate", "Ipuleti 'elishisa'")
    # FIXME newlines also confuse our algorithm for single quotes
    assert passes(stdchecker.singlequoting, "File '%s'\n", "'%s' Faele\n")
    assert fails(stdchecker.singlequoting, "'Hot' plate", 'Ipuleti "elishisa"')
    assert passes(stdchecker.singlequoting, "It's here.", "Dit is hier.")
    # Don't get confused by punctuation that touches a single quote
    assert passes(stdchecker.singlequoting, "File '%s'.", "'%s' Faele.")
    assert passes(
        stdchecker.singlequoting, "Blah 'format' blah.", "Blah blah 'sebopego'."
    )
    assert passes(
        stdchecker.singlequoting, "Blah 'format' blah!", "Blah blah 'sebopego'!"
    )
    assert passes(
        stdchecker.singlequoting, "Blah 'format' blah?", "Blah blah 'sebopego'?"
    )
    # Real examples
    assert passes(
        stdchecker.singlequoting,
        "A nickname that identifies this publishing site (e.g.: 'MySite')",
        "Vito ro duvulela leri tirhisiwaka ku kuma sayiti leri ro kandziyisa (xik.: 'Sayiti ra Mina')",
    )
    assert passes(stdchecker.singlequoting, "isn't", "ayikho")
    assert passes(
        stdchecker.singlequoting,
        "Required (can't send message unless all recipients have certificates)",
        "Verlang (kan nie boodskappe versend tensy al die ontvangers sertifikate het nie)",
    )
    # Afrikaans 'n
    assert passes(
        stdchecker.singlequoting,
        "Please enter a different site name.",
        "Tik 'n ander werfnaam in.",
    )
    assert passes(
        stdchecker.singlequoting,
        '"%name%" already exists. Please enter a different site name.',
        '"%name%" bestaan reeds. Tik \'n ander werfnaam in.',
    )
    # Check that accelerators don't mess with removing singlequotes
    mozillachecker = checks.MozillaChecker()
    assert passes(
        mozillachecker.singlequoting,
        "&Don't import anything",
        "&Moenie enigiets invoer nie",
    )
    ooochecker = checks.OpenOfficeChecker()
    assert passes(
        ooochecker.singlequoting,
        "~Don't import anything",
        "~Moenie enigiets invoer nie",
    )
    lochecker = checks.LibreOfficeChecker()
    assert passes(
        lochecker.singlequoting, "~Don't import anything", "~Moenie enigiets invoer nie"
    )


def test_doublequoting() -> None:
    """Tests double quotes."""
    stdchecker = checks.StandardChecker()
    assert fails(stdchecker.doublequoting, "Hot plate", '"Ipuleti" elishisa')
    assert passes(stdchecker.doublequoting, '"Hot" plate', '"Ipuleti" elishisa')
    assert fails(stdchecker.doublequoting, "'Hot' plate", '"Ipuleti" elishisa')
    assert passes(stdchecker.doublequoting, '\\"Hot\\" plate', '\\"Ipuleti\\" elishisa')

    # We don't want the filter to complain about "untranslated" quotes in xml attributes
    frchecker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="fr"))
    assert passes(
        frchecker.doublequoting,
        'Click <a href="page.html">',
        'Clique <a href="page.html">',
    )
    assert fails(frchecker.doublequoting, 'Do "this"', 'Do "this"')
    assert passes(frchecker.doublequoting, 'Do "this"', "Do « this »")
    assert fails(frchecker.doublequoting, 'Do "this"', "Do « this » « this »")
    # This used to fail because we strip variables, and was left with an empty quotation that was not converted
    assert passes(
        frchecker.doublequoting, "Copying `%s' to `%s'", "Copie de « %s » vers « %s »"
    )

    vichecker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="vi"))
    assert passes(vichecker.doublequoting, 'Save "File"', "Lưu « Tập tin »")

    # Had a small exception with such a case:
    eschecker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="es"))
    assert passes(
        eschecker.doublequoting,
        "<![CDATA[ Enter the name of the Windows workgroup that this server should appear in. ]]>",
        "<![CDATA[ Ingrese el nombre del grupo de trabajo de Windows en el que debe aparecer este servidor. ]]>",
    )


def test_vietnamese_singlequoting() -> None:
    vichecker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="vi"))
    assert passes(vichecker.singlequoting, "Save 'File'", "Lưu « Tập tin »")
    assert passes(vichecker.singlequoting, "Save `File'", "Lưu « Tập tin »")


@mark.xfail(reason="Bug #3408")
def test_persian_single_and_double_quote_fail_at_the_same_time() -> None:
    """Test Persian single and double quote failures in string with single quotes."""
    checker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="fa"))

    # With single quote check.
    assert fails(checker.singlequoting, "Path: '%S'", "مسیر: '%S'‎")
    assert fails(checker.singlequoting, "Path: '%S'", 'مسیر: "%S"‎')
    assert passes(checker.singlequoting, "Path: '%S'", "مسیر: «%S»")

    # With double quote check.
    assert passes(checker.doublequoting, "Path: '%S'", "مسیر: '%S'‎")
    assert passes(checker.doublequoting, "Path: '%S'", 'مسیر: "%S"‎')
    assert passes(checker.doublequoting, "Path: '%S'", "مسیر: «%S»")


def test_persian_quoting() -> None:
    """Test single and double quoting for Persian."""
    checker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="fa"))

    # Just double quoting.
    assert fails(checker.doublequoting, 'Path: "%S"', "مسیر: '%S'‎")
    assert fails(checker.doublequoting, 'Path: "%S"', 'مسیر: "%S"‎')
    assert passes(checker.doublequoting, 'Path: "%S"', "مسیر: «%S»")

    # Just XML quoting.
    assert passes(
        checker.singlequoting, '<area shape="circle">', '<area shape="circle">'
    )
    assert passes(
        checker.doublequoting, '<area shape="circle">', '<area shape="circle">'
    )

    # XML quoting and double quoting.
    assert passes(
        checker.singlequoting,
        'The "coords" attribute of the <area shape="circle"> tag has a negative radius.',
        'مشخصهٔ «coords» برچسب ‪<area shape="circle">‬ دارای «radius» منفی است.',
    )
    assert passes(
        checker.doublequoting,
        'The "coords" attribute of the <area shape="circle"> tag has a negative "radius".',
        'مشخصهٔ «coords» برچسب ‪<area shape="circle">‬ دارای «radius» منفی است.',
    )

    # Single quotes with variables in source fails both single and double quote
    # checks.
    assert fails(
        checker.singlequoting, "'%1$S' is not a directory", "'%1$S' یک شاخه نیست"
    )
    # TODO the following should fail.
    assert passes(
        checker.singlequoting, "'%1$S' is not a directory", '"%1$S" یک شاخه نیست'
    )
    assert fails(
        checker.doublequoting, "'%1$S' is not a directory", "'%1$S' یک شاخه نیست"
    )
    assert fails(
        checker.doublequoting, "'%1$S' is not a directory", '"%1$S" یک شاخه نیست'
    )
    # But works when using the right quoting in translation.
    assert passes(
        checker.singlequoting, "'%1$S' is not a directory", "«%1$S» یک شاخه نیست"
    )
    assert passes(
        checker.doublequoting, "'%1$S' is not a directory", "«%1$S» یک شاخه نیست"
    )

    # Mixing single quotes and and single quotes that shouldn't be translated.
    assert fails(
        checker.singlequoting, "Can't find property '%S'", "خاصیت '%S' یافت نشد"
    )
    assert passes(
        checker.singlequoting, "Can't find property '%S'", "خاصیت «%S» یافت نشد"
    )

    # Mixed single quotes do not trigger double quote check.
    assert passes(
        checker.doublequoting, "Can't find property '%S'", "خاصیت '%S' یافت نشد"
    )
    # TODO the following should pass.
    assert fails(
        checker.doublequoting, "Can't find property '%S'", "خاصیت «%S» یافت نشد"
    )

    # Single quotes that are not errors pass.
    assert passes(
        checker.singlequoting,
        "Request the version of a user's client.",
        "درخواست نسخه کلاینت کاربر.",
    )
    assert passes(
        checker.doublequoting,
        "Request the version of a user's client.",
        "درخواست نسخه کلاینت کاربر.",
    )
