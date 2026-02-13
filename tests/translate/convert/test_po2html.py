import os
from io import BytesIO

import pytest

from translate.convert import po2html

from . import test_convert


class TestPO2Html:
    @staticmethod
    def converthtml(posource, htmltemplate, includefuzzy=False):
        """Helper to exercise the command line function."""
        inputfile = BytesIO(posource.encode())
        print(inputfile.getvalue())
        outputfile = BytesIO()
        templatefile = BytesIO(htmltemplate.encode())
        assert po2html.converthtml(inputfile, outputfile, templatefile, includefuzzy)
        print(outputfile.getvalue())
        return outputfile.getvalue().decode("utf-8")

    def test_simple(self) -> None:
        """Simple po to html test."""
        htmlsource = "<p>A sentence.</p>"
        posource = """#: html:3\nmsgid "A sentence."\nmsgstr "'n Sin."\n"""
        htmlexpected = """<p>'n Sin.</p>"""
        assert htmlexpected in self.converthtml(posource, htmlsource)

    def test_linebreaks(self) -> None:
        """
        Test that a po file can be merged into a template with linebreaks in
        it.
        """
        htmlsource = """<html>
<head>
</head>
<body>
<div>
A paragraph is a section in a piece of writing, usually highlighting a
particular point or topic. It always begins on a new line and usually
with indentation, and it consists of at least one sentence.
</div>
</body>
</html>
"""
        posource = """#: None:1
msgid ""
"A paragraph is a section in a piece of writing, usually highlighting a "
"particular point or topic. It always begins on a new line and usually with "
"indentation, and it consists of at least one sentence."
msgstr ""
"'n Paragraaf is 'n afdeling in 'n geskrewe stuk wat gewoonlik 'n spesifieke "
"punt uitlig. Dit begin altyd op 'n nuwe lyn (gewoonlik met indentasie) en "
"dit bestaan uit ten minste een sin."
"""
        htmlexpected = """<body>
<div>
'n Paragraaf is 'n afdeling in 'n geskrewe stuk wat gewoonlik
'n spesifieke punt uitlig. Dit begin altyd op 'n nuwe lyn
(gewoonlik met indentasie) en dit bestaan uit ten minste een
sin.
</div>
</body>"""
        assert htmlexpected.replace("\n", " ") in self.converthtml(
            posource, htmlsource
        ).replace("\n", " ")

    def test_replace_substrings(self) -> None:
        """Should replace substrings correctly, issue #3416."""
        htmlsource = """<!DOCTYPE html><html><head><title>sub-strings substitution</title></head><body>
<h2>This is heading 2</h2>
<p>The heading says: <b>This is heading 2</b></p>
</body></html>"""
        posource = '#:html.body.h2:2-1\nmsgid "This is heading 2"\nmsgstr "Αυτή είναι μία Ετικέτα 2"\n\n#html.body.p:3-1\nmsgid "The heading says: <b>This is heading 2</b>"\nmsgstr "Η ετικέτα λέει: <b>Αυτή είναι μία Ετικέτα 2</b>"\n'
        htmlexpected = """<!DOCTYPE html><html><head><title>sub-strings substitution</title></head><body>
<h2>Αυτή είναι μία Ετικέτα 2</h2>
<p>Η ετικέτα λέει: <b>Αυτή είναι μία Ετικέτα 2</b></p>
</body></html>"""
        assert htmlexpected in self.converthtml(posource, htmlsource)

    def test_attribute_outside_translatable_content(self) -> None:
        htmlsource = '<img alt="a picture"><p>A sentence.</p>'
        posource = """#: html:3\nmsgid "A sentence."\nmsgstr "'n Sin."\n#: html:1\nmsgid "a picture"\nmsgstr "n prentjie"\n"""
        htmlexpected = """<img alt="n prentjie"><p>'n Sin.</p>"""
        assert htmlexpected in self.converthtml(posource, htmlsource)

    def test_attribute_within_translatable_content_not_embedded(self) -> None:
        htmlsource = '<p><img alt="a picture">A sentence.</p>'
        posource = """#: html:3\nmsgid "A sentence."\nmsgstr "'n Sin."\n#: html:1\nmsgid "a picture"\nmsgstr "n prentjie"\n"""
        htmlexpected = """<p><img alt="n prentjie">'n Sin.</p>"""
        assert htmlexpected in self.converthtml(posource, htmlsource)

    def test_attribute_embedded_within_translatable_content(self) -> None:
        htmlsource = '<p>A sentence<img alt="a picture">.</p>'
        posource = """#: html:3\nmsgid "A sentence<img alt="a picture">."\nmsgstr "'n Sin<img alt="n prentjie">."\n"""
        htmlexpected = """<p>'n Sin<img alt="n prentjie">.</p>"""
        assert htmlexpected in self.converthtml(posource, htmlsource)

    def test_attribute_without_value(self) -> None:
        htmlsource = '<ul><li><a href="logoColor.eps" download>EPS färg</a></li></ul>'
        posource = """#: html:3\nmsgid "EPS färg"\nmsgstr "EPS color"\n"""
        htmlexpected = """<li><a href="logoColor.eps" download>EPS color</a></li>"""
        assert htmlexpected in self.converthtml(posource, htmlsource)

    def test_entities(self) -> None:
        """Tests that entities are handled correctly."""
        htmlsource = "<p>5 less than 6</p>"
        posource = '#:html:3\nmsgid "5 less than 6"\nmsgstr "5 &lt; 6"\n'
        htmlexpected = "<p>5 &lt; 6</p>"
        assert htmlexpected in self.converthtml(posource, htmlsource)

        htmlsource = "<p>Fish &amp; chips</p>"
        posource = '#: html:3\nmsgid "Fish &amp; chips"\nmsgstr "Vis &amp; skyfies"\n'
        htmlexpected = "<p>Vis &amp; skyfies</p>"
        assert htmlexpected in self.converthtml(posource, htmlsource)

    def test_entities_template_vs_po_mismatch(self) -> None:
        """
        Test that po2html handles HTML entity mismatches between template and PO file.

        This addresses the issue where the template contains HTML entities (like &amp;)
        but the PO file has the actual characters (like &), or vice versa.
        """
        # Case 1: Template has &amp; but PO file has & (actual character)
        htmlsource = "<p>Fish &amp; chips</p>"
        posource = '#: html:3\nmsgid "Fish & chips"\nmsgstr "Poisson & frites"\n'
        result = self.converthtml(posource, htmlsource)
        assert "Poisson" in result
        # Verify ampersand is properly preserved in output
        assert "Poisson & frites" in result or "Poisson &amp; frites" in result

        # Case 2: Template has & (actual character) but PO file has &amp;
        htmlsource = "<p>Fish & chips</p>"
        posource = (
            '#: html:3\nmsgid "Fish &amp; chips"\nmsgstr "Poisson &amp; frites"\n'
        )
        result = self.converthtml(posource, htmlsource)
        assert "Poisson" in result
        # Verify ampersand entity is properly preserved
        assert "Poisson &amp; frites" in result

        # Case 3: Template has &lt; but PO file has < (actual character)
        htmlsource = "<p>5 &lt; 6</p>"
        posource = '#: html:3\nmsgid "5 < 6"\nmsgstr "5 inférieur à 6"\n'
        result = self.converthtml(posource, htmlsource)
        assert "inférieur" in result
        # Verify the translation is applied (note: translation doesn't include < symbol)
        assert "<p>5 inférieur à 6</p>" in result

        # Case 4: Template has < (actual character) but PO file has &lt;
        htmlsource = "<p>Text about less than</p>"
        posource = (
            '#: html:3\nmsgid "Text about less than"\nmsgstr "Texte à propos de &lt;"\n'
        )
        result = self.converthtml(posource, htmlsource)
        assert "Texte" in result
        # Verify the &lt; entity from translation is preserved
        assert "&lt;" in result

        # Case 5: Template has &gt; but PO file has > (actual character)
        htmlsource = "<p>x &gt; y</p>"
        posource = '#: html:3\nmsgid "x > y"\nmsgstr "x supérieur à y"\n'
        result = self.converthtml(posource, htmlsource)
        assert "supérieur" in result
        # Verify the translation is applied (note: translation doesn't include > symbol)
        assert "<p>x supérieur à y</p>" in result

    def test_utf8_non_ascii_characters(self) -> None:
        """
        Tests that non-ASCII UTF-8 characters are handled correctly.

        This addresses issue #1043 where non-ASCII characters like ü were
        being incorrectly converted to double-encoded entities like
        &Atilde;&frac14; instead of being preserved as UTF-8.
        """
        # Test German umlauts
        htmlsource = "<p>Übung macht den Meister</p>"
        posource = '#: html:3\nmsgid "Übung macht den Meister"\nmsgstr "Übung macht den Meister"\n'
        htmlexpected = "<p>Übung macht den Meister</p>"
        result = self.converthtml(posource, htmlsource)
        assert htmlexpected in result
        # Ensure no double encoding like &Atilde;&frac14;
        assert "&Atilde;" not in result
        assert "&frac14;" not in result

        # Test various non-ASCII characters
        htmlsource = "<p>Café naïve résumé</p>"
        posource = '#: html:3\nmsgid "Café naïve résumé"\nmsgstr "Café naïve résumé"\n'
        htmlexpected = "<p>Café naïve résumé</p>"
        result = self.converthtml(posource, htmlsource)
        assert htmlexpected in result

        # Test with translation containing UTF-8
        htmlsource = "<p>Hello world</p>"
        posource = '#: html:3\nmsgid "Hello world"\nmsgstr "Hej världen"\n'
        htmlexpected = "<p>Hej världen</p>"
        result = self.converthtml(posource, htmlsource)
        assert htmlexpected in result

    def test_custom_entities_preserved(self) -> None:
        """
        Tests that custom entities are preserved and not double-encoded.

        This addresses issue #1043 where custom entities like &brandShortName;
        were being incorrectly double-encoded to &amp;brandShortName;.
        """
        # Test custom entity preservation
        htmlsource = "<p>Use &brandShortName; for the best experience.</p>"
        posource = '#: html:3\nmsgid "Use &brandShortName; for the best experience."\nmsgstr "Verwenden Sie &brandShortName; für die beste Erfahrung."\n'  # codespell:ignore
        htmlexpected = "<p>Verwenden Sie &brandShortName; für die beste Erfahrung.</p>"  # codespell:ignore
        result = self.converthtml(posource, htmlsource)
        assert htmlexpected in result
        # Ensure no double encoding
        assert "&amp;brandShortName;" not in result

        # Test multiple custom entities
        htmlsource = "<p>&brandShortName; &version; &copyright;</p>"
        posource = '#: html:3\nmsgid "&brandShortName; &version; &copyright;"\nmsgstr "&brandShortName; &version; &copyright;"\n'
        htmlexpected = "<p>&brandShortName; &version; &copyright;</p>"
        result = self.converthtml(posource, htmlsource)
        assert htmlexpected in result
        assert "&amp;brandShortName;" not in result
        assert "&amp;version;" not in result
        assert "&amp;copyright;" not in result

    def test_escapes(self) -> None:
        """Tests that PO escapes are correctly handled."""
        htmlsource = '<p>"leverage"</p>'
        posource = '#: html3\nmsgid "\\"leverage\\""\nmsgstr "\\"ek is dom\\""\n'
        htmlexpected = '<p>"ek is dom"</p>'
        assert htmlexpected in self.converthtml(posource, htmlsource)

    def test_dir_attribute_auto_rtl(self) -> None:
        """Test that dir attribute is automatically set to rtl for RTL languages."""
        htmlsource = '<html lang="en" dir="ltr"><head><title>Test</title></head><body><p>Content</p></body></html>'
        posource = """#: html+html[lang]:1-1
msgid "en"
msgstr "ar"

#: html+html.head.title:1-19
msgid "Test"
msgstr "اختبار"

#: html+html.body.p:1-48
msgid "Content"
msgstr "محتوى"
"""
        result = self.converthtml(posource, htmlsource)
        # Check that dir was automatically changed to rtl
        assert 'dir="rtl"' in result
        assert 'dir="ltr"' not in result
        assert 'lang="ar"' in result

    def test_dir_attribute_auto_ltr(self) -> None:
        """Test that dir attribute is automatically set to ltr for LTR languages."""
        htmlsource = '<html lang="ar" dir="rtl"><head><title>اختبار</title></head><body><p>محتوى</p></body></html>'
        posource = """#: html+html[lang]:1-1
msgid "ar"
msgstr "en"

#: html+html.head.title:1-25
msgid "اختبار"
msgstr "Test"

#: html+html.body.p:1-54
msgid "محتوى"
msgstr "Content"
"""
        result = self.converthtml(posource, htmlsource)
        # Check that dir was automatically changed to ltr
        assert 'dir="ltr"' in result
        assert 'dir="rtl"' not in result
        assert 'lang="en"' in result

    def test_dir_attribute_added_when_missing(self) -> None:
        """Test that dir attribute is added when translating to RTL language."""
        htmlsource = '<html lang="en"><head><title>Test</title></head><body><p>Content</p></body></html>'
        posource = """#: html+html[lang]:1-1
msgid "en"
msgstr "he"

#: html+html.head.title:1-13
msgid "Test"
msgstr "בדיקה"

#: html+html.body.p:1-42
msgid "Content"
msgstr "תוכן"
"""
        result = self.converthtml(posource, htmlsource)
        # Check that dir was automatically added with rtl value
        assert 'dir="rtl"' in result
        assert 'lang="he"' in result

    def test_dir_attribute_not_changed_without_lang_translation(self) -> None:
        """Test that dir attribute is not changed when lang is not translated."""
        htmlsource = '<html lang="en" dir="ltr"><head><title>Test</title></head><body><p>Content</p></body></html>'
        posource = """#: html+html.head.title:1-19
msgid "Test"
msgstr "Prueba"

#: html+html.body.p:1-48
msgid "Content"
msgstr "Contenido"
"""
        result = self.converthtml(posource, htmlsource)
        # Check that dir remains unchanged since lang was not translated
        assert 'dir="ltr"' in result
        assert 'lang="en"' in result

    def test_states_translated(self) -> None:
        """Test that we use target when translated."""
        htmlsource = "<div>aaa</div>"
        posource = 'msgid "aaa"\nmsgstr "bbb"\n'
        htmltarget = "<div>bbb</div>"
        assert htmltarget in self.converthtml(posource, htmlsource)
        assert htmlsource not in self.converthtml(posource, htmlsource)

    def test_states_untranslated(self) -> None:
        """Test that we use source when a string is untranslated."""
        htmlsource = "<div>aaa</div>"
        posource = 'msgid "aaa"\nmsgstr ""\n'
        htmltarget = htmlsource
        assert htmltarget in self.converthtml(posource, htmlsource)

    def test_states_fuzzy(self) -> None:
        """
        Test that we use source when a string is fuzzy.

        This fixes :issue:`3145`
        """
        htmlsource = "<div>aaa</div>"
        posource = '#: html:3\n#, fuzzy\nmsgid "aaa"\nmsgstr "bbb"\n'
        htmltarget = "<div>bbb</div>"
        # Don't use fuzzies
        assert htmltarget not in self.converthtml(
            posource, htmlsource, includefuzzy=False
        )
        assert htmlsource in self.converthtml(posource, htmlsource, includefuzzy=False)
        # Use fuzzies
        assert htmltarget in self.converthtml(posource, htmlsource, includefuzzy=True)
        assert htmlsource not in self.converthtml(
            posource, htmlsource, includefuzzy=True
        )

    def test_untranslated_attributes(self) -> None:
        """
        Verify that untranslated attributes are output as source, not
        dropped.
        """
        htmlsource = '<meta name="keywords" content="life, the universe, everything" />'
        posource = '#: test.html+:-1\nmsgid "life, the universe, everything"\nmsgstr ""'
        expected = '<meta name="keywords" content="life, the universe, everything" />'
        assert expected in self.converthtml(posource, htmlsource)

    def test_button_translation(self) -> None:
        """Test that button elements are properly translated."""
        htmlsource = "<button>Zustimmen und weiter</button>"  # codespell:ignore
        posource = '#: html:3\nmsgid "Zustimmen und weiter"\nmsgstr "Agree and continue"\n'  # codespell:ignore
        htmlexpected = "<button>Agree and continue</button>"
        assert htmlexpected in self.converthtml(posource, htmlsource)

        # Test button with attributes
        htmlsource = '<button type="submit" class="btn">Submit</button>'
        posource = '#: html:3\nmsgid "Submit"\nmsgstr "Enviar"\n'
        htmlexpected = '<button type="submit" class="btn">Enviar</button>'
        assert htmlexpected in self.converthtml(posource, htmlsource)

        # Test button with nested elements
        htmlsource = "<button><strong>Click</strong> here</button>"
        posource = '#: html:3\nmsgid "<strong>Click</strong> here"\nmsgstr "<strong>Klicken</strong> Sie hier"\n'  # codespell:ignore
        htmlexpected = (
            "<button><strong>Klicken</strong> Sie hier</button>"  # codespell:ignore
        )
        assert htmlexpected in self.converthtml(posource, htmlsource)

    def test_lang_attribute_only_on_html_tag(self) -> None:
        """
        Test that the lang attribute is only translated on the html tag, not on other tags.

        Issue: https://github.com/translate/translate/issues/5504
        """
        htmlsource = """<!DOCTYPE html>
<html lang="en">
<head>
    <title>Test</title>
</head>
<body>
    <nav>
     Language switcher:
     <a lang="en" href="/en">English</a>
     <a lang="es" href="/es">Español</a>
     <a lang="fr" href="/fr">Français</a>
    </nav>
    <p>This is a page about the English word <strong lang="en">Hello</strong>.</p>
</body>
</html>"""
        posource = """#: test.html+html[lang]:1-16
msgid "en"
msgstr "fr"

#: test.html+html.body.p:12-1
msgid "This is a page about the English word <strong lang=\\"en\\">Hello</strong>."
msgstr "Ceci est une page à propos du mot anglais <strong lang=\\"en\\">Hello</strong>."
"""
        result = self.converthtml(posource, htmlsource)
        # The html tag should have lang="fr" (translated) and dir="ltr" (auto-added)
        assert 'lang="fr"' in result
        assert 'dir="ltr"' in result
        # Other elements should keep lang="en" (not translated)
        assert 'lang="en" href="/en">English</a>' in result
        # Verify that <a lang="en"> is present
        assert '<a lang="en"' in result

    def test_data_translate_ignore_preserved(self) -> None:
        """Test that ignored content is preserved in po2html output."""
        # Simple case
        htmlsource = "<p>Translate this</p><p data-translate-ignore>Do not translate</p><p>Translate this too</p>"
        posource = """#: test.html
msgid "Translate this"
msgstr "Traduire ceci"

#: test.html
msgid "Translate this too"
msgstr "Traduire ceci aussi"
"""
        result = self.converthtml(posource, htmlsource)
        assert "<p>Traduire ceci</p>" in result
        assert "<p data-translate-ignore>Do not translate</p>" in result
        assert "<p>Traduire ceci aussi</p>" in result

        # Nested elements
        htmlsource = "<div>Translate this</div><div data-translate-ignore><p>Do not translate</p></div><div>Translate this too</div>"
        posource = """#: test.html
msgid "Translate this"
msgstr "Traduire ceci"

#: test.html
msgid "Translate this too"
msgstr "Traduire ceci aussi"
"""
        result = self.converthtml(posource, htmlsource)
        assert "<div>Traduire ceci</div>" in result
        assert "<div data-translate-ignore><p>Do not translate</p></div>" in result
        assert "<div>Traduire ceci aussi</div>" in result

        # Self-closing tags with data-translate-ignore should not have attributes translated
        htmlsource = '<img alt="Extract this" /><img alt="Do not extract" data-translate-ignore /><p>Translate</p>'
        posource = """#: test.html
msgid "Extract this"
msgstr "Extraire ceci"

#: test.html
msgid "Translate"
msgstr "Traduire"
"""
        result = self.converthtml(posource, htmlsource)
        assert '<img alt="Extraire ceci" />' in result
        assert '<img alt="Do not extract" data-translate-ignore />' in result
        assert "<p>Traduire</p>" in result

    def test_translate_comment_directives_preserved(self) -> None:
        """Test that translate:off/on comments are preserved and content ignored."""
        htmlsource = "<p>Translate this</p><!-- translate:off --><p>Do not translate</p><!-- translate:on --><p>Translate this too</p>"
        posource = """#: test.html
msgid "Translate this"
msgstr "Traduire ceci"

#: test.html
msgid "Translate this too"
msgstr "Traduire ceci aussi"
"""
        result = self.converthtml(posource, htmlsource)
        assert "<p>Traduire ceci</p>" in result
        assert "<!-- translate:off -->" in result
        assert "<p>Do not translate</p>" in result
        assert "<!-- translate:on -->" in result
        assert "<p>Traduire ceci aussi</p>" in result

    def test_data_translate_ignore_with_translation_in_po(self) -> None:
        """Test that ignored content is not translated even if translation exists in PO file."""
        # Test with data-translate-ignore attribute
        htmlsource = "<p>Translate this</p><p data-translate-ignore>Do not translate</p><p>Translate this too</p>"
        posource = """#: test.html
msgid "Translate this"
msgstr "Traduire ceci"

#: test.html
msgid "Do not translate"
msgstr "NE PAS traduire ceci"

#: test.html
msgid "Translate this too"
msgstr "Traduire ceci aussi"
"""
        result = self.converthtml(posource, htmlsource)
        assert "<p>Traduire ceci</p>" in result
        # Verify the ignored content is NOT translated even though translation exists
        assert "<p data-translate-ignore>Do not translate</p>" in result
        assert "NE PAS traduire ceci" not in result
        assert "<p>Traduire ceci aussi</p>" in result

    def test_translate_comment_with_translation_in_po(self) -> None:
        """Test that content between translate:off/on is not translated even if translation exists in PO file."""
        # Test with comment directives
        htmlsource = "<p>Translate this</p><!-- translate:off --><p>Do not translate</p><!-- translate:on --><p>Translate this too</p>"
        posource = """#: test.html
msgid "Translate this"
msgstr "Traduire ceci"

#: test.html
msgid "Do not translate"
msgstr "NE PAS traduire ceci"

#: test.html
msgid "Translate this too"
msgstr "Traduire ceci aussi"
"""
        result = self.converthtml(posource, htmlsource)
        assert "<p>Traduire ceci</p>" in result
        # Verify the ignored content is NOT translated even though translation exists
        assert "<p>Do not translate</p>" in result
        assert "NE PAS traduire ceci" not in result
        assert "<p>Traduire ceci aussi</p>" in result

    def test_meta_social_media_tags_translation(self) -> None:
        """Test that social media meta tags are properly translated."""
        # Test Open Graph tags
        htmlsource = """<html><head>
        <meta property="og:title" content="My Page Title">
        <meta property="og:description" content="A description of my page">
        <meta property="og:site_name" content="My Website">
        </head><body></body></html>"""
        posource = """#: test.html
msgid "My Page Title"
msgstr "Mon Titre de Page"

#: test.html
msgid "A description of my page"
msgstr "Une description de ma page"

#: test.html
msgid "My Website"
msgstr "Mon Site Web"
"""
        result = self.converthtml(posource, htmlsource)
        assert '<meta property="og:title" content="Mon Titre de Page">' in result
        assert (
            '<meta property="og:description" content="Une description de ma page">'
            in result
        )
        assert '<meta property="og:site_name" content="Mon Site Web">' in result

        # Test Twitter Card tags
        htmlsource = """<html><head>
        <meta name="twitter:title" content="My Tweet Title">
        <meta name="twitter:description" content="A tweet description">
        </head><body></body></html>"""
        posource = """#: test.html
msgid "My Tweet Title"
msgstr "Mon Titre de Tweet"

#: test.html
msgid "A tweet description"
msgstr "Une description de tweet"
"""
        result = self.converthtml(posource, htmlsource)
        assert '<meta name="twitter:title" content="Mon Titre de Tweet">' in result
        assert (
            '<meta name="twitter:description" content="Une description de tweet">'
            in result
        )

    def test_meta_non_translatable_tags_preserved(self) -> None:
        """Test that non-translatable meta tags are preserved without translation."""
        htmlsource = """<html><head>
        <meta property="og:title" content="My Page Title">
        <meta property="og:image" content="https://example.com/image.jpg">
        <meta property="og:url" content="https://example.com/">
        <meta name="twitter:card" content="summary">
        </head><body></body></html>"""
        posource = """#: test.html
msgid "My Page Title"
msgstr "Mon Titre de Page"
"""
        result = self.converthtml(posource, htmlsource)
        # Translatable tag should be translated
        assert '<meta property="og:title" content="Mon Titre de Page">' in result
        # Non-translatable tags should be preserved as-is
        assert (
            '<meta property="og:image" content="https://example.com/image.jpg">'
            in result
        )
        assert '<meta property="og:url" content="https://example.com/">' in result
        assert '<meta name="twitter:card" content="summary">' in result


class TestPO2HtmlCommand(test_convert.TestConvertCommand, TestPO2Html):
    """Tests running actual po2html commands on files."""

    convertmodule = po2html

    expected_options = [
        "-t TEMPLATE, --template=TEMPLATE",
        "--threshold=PERCENT",
        "--fuzzy",
        "--nofuzzy",
    ]

    def test_individual_files(self) -> None:
        """
        Test the fully non-recursive case where all inputs and outputs
        (input po, template html, output html) are specified as individual
        files.
        """
        self.given_html_test_file("file1.html")
        self.given_po_test_file("file1.po")

        self.run_command("file1.po", "out.html", template="file1.html")

        self.then_html_file_is_translated("out.html")

    def test_fully_recursive(self) -> None:
        """
        Test the fully recursive case where all inputs and outputs (input,
        template, output) are specified as directories.
        """
        self.given_html_test_file("template/file1.html")
        self.given_html_test_file("template/file2.html")
        self.given_po_test_file("translation/file1.po")

        self.run_command("translation", "translated", template="template")

        self.then_html_file_is_translated("translated/file1.html")
        # then: file2.html is not translated because there is no matching po file.
        assert not os.path.isfile(self.get_testfilename("translated/file2.html"))

    def test_no_input_specified(self) -> None:
        """
        Test the case where no input file or directory is specified.
        Expect failure with exit.
        """
        self.given_html_test_file("template/file1.html")
        with pytest.raises(SystemExit):
            self.run_command(output="translated", template="template")

    def test_no_template_specified(self, caplog) -> None:
        """
        Test the case where no template file or directory is specified.
        Expect failure with log message.
        """
        self.given_po_test_file("translation/file1.po")
        self.run_command("translation", "translated")
        assert "Error processing:" in caplog.text

    def test_no_output_specified(self, capsys) -> None:
        """
        Test the case where there is a single input file and no output file
        or directory is specified. Defaults to stdout.
        """
        self.given_html_test_file("file1.html")
        self.given_po_test_file("file1.po")

        self.run_command("file1.po", template="file1.html")

        content, err = capsys.readouterr()
        assert "<div>target1</div>" in content
        assert err == ""

    def test_recursive_templates_with_single_po_file(self) -> None:
        """
        Test the case where templates and outputs are directories, and the
        input is specified as an individual po file.

        This indicates that the po file should be applied to all
        template files.
        """
        self.given_html_test_file("template/file1.html")
        self.given_html_test_file("template/subdir/file2.html")
        self.given_po_test_file("translation/file1.po")

        self.run_command("translation/file1.po", "translated", template="template")

        self.then_html_file_is_translated("translated/file1.html")
        self.then_html_file_is_translated("translated/subdir/file2.html")

    def test_recursive_templates_with_single_po_file_and_templates_overwritten(
        self,
    ) -> None:
        """
        Test the case where templates and outputs are in the same directory,
        and the input is specified as an individual po file.

        This indicates that the po file should be applied to all
        template files.
        """
        self.given_html_test_file("html/file1.html")
        self.given_html_test_file("html/subdir/file2.html")
        self.given_po_test_file("translation/file1.po")

        self.run_command("translation/file1.po", "html", template="html")

        self.then_html_file_is_translated("html/file1.html")
        self.then_html_file_is_translated("html/subdir/file2.html")

    def given_html_test_file(self, filename) -> None:
        self.create_testfile(
            filename, "<div>You are only coming through in waves</div>"
        )

    def given_po_test_file(self, filename) -> None:
        self.create_testfile(
            filename,
            """
#: 'ref'
msgid "You are only coming through in waves"
msgstr "target1"
""",
        )

    def then_html_file_is_translated(self, filename) -> None:
        assert os.path.isfile(self.get_testfilename(filename))
        content = str(self.read_testfile(filename))
        assert "<div>target1</div>" in content
