"""Tests for the XML/HTML tag checks."""

from pytest import mark

from tests.translate.filters.checks.helpers import fails, passes
from translate.filters import checks


def test_xmltags() -> None:
    """Tests xml tags."""
    stdchecker = checks.StandardChecker()
    assert fails(stdchecker.xmltags, "Do it <b>now</b>", "Doen dit <v>nou</v>")
    assert passes(stdchecker.xmltags, "Do it <b>now</b>", "Doen dit <b>nou</b>")
    assert passes(
        stdchecker.xmltags,
        'Click <img src="img.jpg">here</img>',
        'Klik <img src="img.jpg">hier</img>',
    )
    assert fails(
        stdchecker.xmltags,
        'Click <img src="image.jpg">here</img>',
        'Klik <img src="prent.jpg">hier</img>',
    )
    assert passes(
        stdchecker.xmltags,
        'Click <img src="img.jpg" alt="picture">here</img>',
        'Klik <img src="img.jpg" alt="prentjie">hier</img>',
    )
    assert passes(
        stdchecker.xmltags,
        'Click <a title="tip">here</a>',
        'Klik <a title="wenk">hier</a>',
    )
    assert passes(
        stdchecker.xmltags,
        'Click <div title="tip">here</div>',
        'Klik <div title="wenk">hier</div>',
    )
    assert passes(
        stdchecker.xmltags,
        "Start with the &lt;start&gt; tag",
        "Begin met die &lt;begin&gt;",
    )

    assert fails(
        stdchecker.xmltags,
        'Click <a href="page.html">',
        'Klik <a hverw="page.html">',
    )
    assert passes(
        stdchecker.xmltags,
        'Click <a xml-lang="en" href="page.html">',
        'Klik <a xml-lang="af" href="page.html">',
    )
    assert passes(
        stdchecker.xmltags,
        'Click <div lang="en" dir="ltr">',
        'Klik <div lang="ar" dir="rtl">',
    )
    assert fails(
        stdchecker.xmltags,
        'Click <a href="page.html" target="koei">',
        'Klik <a href="page.html">',
    )
    assert fails(
        stdchecker.xmltags, "<b>Current Translation</b>", "<b>Traducción Actual:<b>"
    )
    assert passes(stdchecker.xmltags, "<Error>", "<Fout>")
    assert fails(
        stdchecker.xmltags,
        "%d/%d translated\n(%d blank, %d fuzzy)",
        "<br>%d/%d μεταφρασμένα\n<br>(%d κενά, %d ασαφή)",
    )
    assert fails(
        stdchecker.xmltags,
        '(and <a href="https://www.schoolforge.net/education-software" class="external">other open source software</a>)',
        '(en <a href="https://www.schoolforge.net/education-software" class="external">ander Vry Sagteware</a)',
    )
    assert fails(
        stdchecker.xmltags,
        'Because Tux Paint (and <a href="https://www.schoolforge.net/education-software" class="external">other open source software</a>) is free of cost and not limited in any way, a school can use it <i>today</i>, without waiting for procurement or a budget!',
        'Omdat Tux Paint (en <a href="https://www.schoolforge.net/education-software" class="external">ander Vry Sagteware</a)gratis is en nie beperk is op enige manier nie, kan \'n skool dit vandag</i> gebruik sonder om te wag vir goedkeuring of \'n begroting!',
    )
    assert fails(stdchecker.xmltags, "test <br />", "test <br>")
    assert fails(
        stdchecker.xmltags, "test <img src='foo.jpg'/ >", "test <img src='foo.jpg'  >"
    )

    # This used to cause an error (traceback), because of mismatch between
    # different regular expressions (because of the newlines)
    assert passes(
        stdchecker.xmltags,
        """<markup>
<span weight="bold" size="large"
style="oblique">
Can't create server !
</span>
</markup>""",
        """<markup>
<span weight="bold" size="large"
style="oblique">
No s'ha pogut crear el servidor
</span>
</markup>""",
    )
    frchecker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="fr"))
    assert fails(
        frchecker.xmltags, 'Click <a href="page.html">', "Klik <a href=« page.html »>"
    )


def test_ooxmltags() -> None:
    """Tests the xml tags in OpenOffice.org translations for quality as done in gsicheck."""
    for ooochecker in (checks.OpenOfficeChecker(), checks.LibreOfficeChecker()):
        # some attributes can be changed or removed
        assert fails(
            ooochecker.xmltags,
            '<img src="a.jpg" width="400">',
            '<img src="b.jpg" width="500">',
        )
        assert passes(
            ooochecker.xmltags,
            '<img src="a.jpg" width="400">',
            '<img src="a.jpg" width="500">',
        )
        assert passes(
            ooochecker.xmltags,
            '<img src="a.jpg" width="400">',
            '<img src="a.jpg">',
        )
        assert passes(
            ooochecker.xmltags,
            '<img src="a.jpg">',
            '<img src="a.jpg" width="400">',
        )
        assert passes(
            ooochecker.xmltags, '<alt xml-lang="ab">text</alt>', "<alt>teks</alt>"
        )
        assert passes(
            ooochecker.xmltags,
            '<ahelp visibility="visible">bla</ahelp>',
            "<ahelp>blu</ahelp>",
        )
        assert fails(
            ooochecker.xmltags,
            '<ahelp visibility="visible">bla</ahelp>',
            '<ahelp visibility="invisible">blu</ahelp>',
        )
        assert fails(
            ooochecker.xmltags,
            '<ahelp visibility="invisible">bla</ahelp>',
            "<ahelp>blu</ahelp>",
        )
        # some attributes can be changed, but not removed
        assert passes(ooochecker.xmltags, '<link name="John">', '<link name="Jan">')
        assert fails(ooochecker.xmltags, '<link name="John">', '<link naam="Jan">')

        # Reported OOo error
        ## Bug 1910
        assert fails(
            ooochecker.xmltags,
            """<variable id="FehlendesElement">In a database file window, click the <emph>Queries</emph> icon, then choose <emph>Edit - Edit</emph>. When referenced fields no longer exist, you see this dialog</variable>""",
            """<variable id="FehlendesElement">Dans  une fenêtre de fichier de base de données, cliquez sur l'icône <emph>Requêtes</emph>, puis choisissez <emph>Éditer - Éditer</emp>. Lorsque les champs de référence n'existent plus, vous voyez cette boîte de dialogue</variable>""",
        )
        assert fails(
            ooochecker.xmltags,
            "<variable> <emph></emph> <emph></emph> </variable>",
            "<variable> <emph></emph> <emph></emp> </variable>",
        )


@mark.xfail(reason="Bug #3506")
def test_bengali_mozilla_inverted_xmltags() -> None:
    """Test Bengali Mozilla XML tags."""
    bn_mozilla_checker = checks.MozillaChecker(
        checkerconfig=checks.CheckerConfig(targetlanguage="bn")
    )
    str_en = """We <a href="%(cofound_url)s" rel="external">co-founded</a> the <a href="%(whatwg_url)s" rel="external">WHAT-WG</a> to."""
    str_bn = """এর প্রচলন ঘটাতে আমরা <a href="%(whatwg_url)s" rel="external">WHAT-WG</a> প্রতিষ্ঠায় <a href="%(cofound_url)s" rel="external">সহযোগী</a> ছিলাম।ন।"""
    assert passes(bn_mozilla_checker.xmltags, str_en, str_bn)
