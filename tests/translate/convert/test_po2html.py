import os
from io import BytesIO

import pytest

from translate.convert import po2html, test_convert


class TestPO2Html:
    @staticmethod
    def converthtml(posource, htmltemplate, includefuzzy=False):
        """helper to exercise the command line function."""
        inputfile = BytesIO(posource.encode())
        print(inputfile.getvalue())
        outputfile = BytesIO()
        templatefile = BytesIO(htmltemplate.encode())
        assert po2html.converthtml(inputfile, outputfile, templatefile, includefuzzy)
        print(outputfile.getvalue())
        return outputfile.getvalue().decode("utf-8")

    def test_simple(self):
        """simple po to html test."""
        htmlsource = "<p>A sentence.</p>"
        posource = """#: html:3\nmsgid "A sentence."\nmsgstr "'n Sin."\n"""
        htmlexpected = """<p>'n Sin.</p>"""
        assert htmlexpected in self.converthtml(posource, htmlsource)

    def test_linebreaks(self):
        """Test that a po file can be merged into a template with linebreaks in
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

    def test_replace_substrings(self):
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

    def test_attribute_outside_translatable_content(self):
        htmlsource = '<img alt="a picture"><p>A sentence.</p>'
        posource = """#: html:3\nmsgid "A sentence."\nmsgstr "'n Sin."\n#: html:1\nmsgid "a picture"\nmsgstr "n prentjie"\n"""
        htmlexpected = """<img alt="n prentjie"><p>'n Sin.</p>"""
        assert htmlexpected in self.converthtml(posource, htmlsource)

    def test_attribute_within_translatable_content_not_embedded(self):
        htmlsource = '<p><img alt="a picture">A sentence.</p>'
        posource = """#: html:3\nmsgid "A sentence."\nmsgstr "'n Sin."\n#: html:1\nmsgid "a picture"\nmsgstr "n prentjie"\n"""
        htmlexpected = """<p><img alt="n prentjie">'n Sin.</p>"""
        assert htmlexpected in self.converthtml(posource, htmlsource)

    def test_attribute_embedded_within_translatable_content(self):
        htmlsource = '<p>A sentence<img alt="a picture">.</p>'
        posource = """#: html:3\nmsgid "A sentence<img alt="a picture">."\nmsgstr "'n Sin<img alt="n prentjie">."\n"""
        htmlexpected = """<p>'n Sin<img alt="n prentjie">.</p>"""
        assert htmlexpected in self.converthtml(posource, htmlsource)

    def test_attribute_without_value(self):
        htmlsource = '<ul><li><a href="logoColor.eps" download>EPS färg</a></li></ul>'
        posource = """#: html:3\nmsgid "EPS färg"\nmsgstr "EPS color"\n"""
        htmlexpected = """<li><a href="logoColor.eps" download>EPS color</a></li>"""
        assert htmlexpected in self.converthtml(posource, htmlsource)

    def test_entities(self):
        """Tests that entities are handled correctly."""
        htmlsource = "<p>5 less than 6</p>"
        posource = '#:html:3\nmsgid "5 less than 6"\nmsgstr "5 &lt; 6"\n'
        htmlexpected = "<p>5 &lt; 6</p>"
        assert htmlexpected in self.converthtml(posource, htmlsource)

        htmlsource = "<p>Fish &amp; chips</p>"
        posource = '#: html:3\nmsgid "Fish &amp; chips"\nmsgstr "Vis &amp; skyfies"\n'
        htmlexpected = "<p>Vis &amp; skyfies</p>"
        assert htmlexpected in self.converthtml(posource, htmlsource)

    def test_escapes(self):
        """Tests that PO escapes are correctly handled."""
        htmlsource = '<p>"leverage"</p>'
        posource = '#: html3\nmsgid "\\"leverage\\""\nmsgstr "\\"ek is dom\\""\n'
        htmlexpected = '<p>"ek is dom"</p>'
        assert htmlexpected in self.converthtml(posource, htmlsource)

    def test_states_translated(self):
        """Test that we use target when translated."""
        htmlsource = "<div>aaa</div>"
        posource = 'msgid "aaa"\nmsgstr "bbb"\n'
        htmltarget = "<div>bbb</div>"
        assert htmltarget in self.converthtml(posource, htmlsource)
        assert htmlsource not in self.converthtml(posource, htmlsource)

    def test_states_untranslated(self):
        """Test that we use source when a string is untranslated."""
        htmlsource = "<div>aaa</div>"
        posource = 'msgid "aaa"\nmsgstr ""\n'
        htmltarget = htmlsource
        assert htmltarget in self.converthtml(posource, htmlsource)

    def test_states_fuzzy(self):
        """Test that we use source when a string is fuzzy.

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

    def test_untranslated_attributes(self):
        """Verify that untranslated attributes are output as source, not
        dropped.
        """
        htmlsource = '<meta name="keywords" content="life, the universe, everything" />'
        posource = '#: test.html+:-1\nmsgid "life, the universe, everything"\nmsgstr ""'
        expected = '<meta name="keywords" content="life, the universe, everything" />'
        assert expected in self.converthtml(posource, htmlsource)


class TestPO2HtmlCommand(test_convert.TestConvertCommand, TestPO2Html):
    """Tests running actual po2html commands on files."""

    convertmodule = po2html

    expected_options = [
        "-t TEMPLATE, --template=TEMPLATE",
        "--threshold=PERCENT",
        "--fuzzy",
        "--nofuzzy",
    ]

    def test_individual_files(self):
        """Test the fully non-recursive case where all inputs and outputs
        (input po, template html, output html) are specified as individual
        files.
        """
        self.given_html_test_file("file1.html")
        self.given_po_test_file("file1.po")

        self.run_command("file1.po", "out.html", template="file1.html")

        self.then_html_file_is_translated("out.html")

    def test_fully_recursive(self):
        """Test the fully recursive case where all inputs and outputs (input,
        template, output) are specified as directories.
        """
        self.given_html_test_file("template/file1.html")
        self.given_html_test_file("template/file2.html")
        self.given_po_test_file("translation/file1.po")

        self.run_command("translation", "translated", template="template")

        self.then_html_file_is_translated("translated/file1.html")
        # then: file2.html is not translated because there is no matching po file.
        assert not os.path.isfile(self.get_testfilename("translated/file2.html"))

    def test_no_input_specified(self):
        """Test the case where no input file or directory is specified.
        Expect failure with exit.
        """
        self.given_html_test_file("template/file1.html")
        with pytest.raises(SystemExit):
            self.run_command(output="translated", template="template")

    def test_no_template_specified(self, caplog):
        """Test the case where no template file or directory is specified.
        Expect failure with log message.
        """
        self.given_po_test_file("translation/file1.po")
        self.run_command("translation", "translated")
        assert "Error processing:" in caplog.text

    def test_no_output_specified(self, capsys):
        """Test the case where there is a single input file and no output file
        or directory is specified. Defaults to stdout.
        """
        self.given_html_test_file("file1.html")
        self.given_po_test_file("file1.po")

        self.run_command("file1.po", template="file1.html")

        content, err = capsys.readouterr()
        assert "<div>target1</div>" in content
        assert err == ""

    def test_recursive_templates_with_single_po_file(self):
        """Test the case where templates and outputs are directories, and the
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

    def test_recursive_templates_with_single_po_file_and_templates_overwritten(self):
        """Test the case where templates and outputs are in the same directory,
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

    def given_html_test_file(self, filename):
        self.create_testfile(
            filename, "<div>You are only coming through in waves</div>"
        )

    def given_po_test_file(self, filename):
        self.create_testfile(
            filename,
            """
#: 'ref'
msgid "You are only coming through in waves"
msgstr "target1"
""",
        )

    def then_html_file_is_translated(self, filename):
        assert os.path.isfile(self.get_testfilename(filename))
        content = str(self.read_testfile(filename))
        assert "<div>target1</div>" in content
