from io import BytesIO

from translate.convert import po2html, test_convert


class TestPO2Html:

    def converthtml(self, posource, htmltemplate, includefuzzy=False):
        """helper to exercise the command line function"""
        inputfile = BytesIO(posource.encode())
        print(inputfile.getvalue())
        outputfile = BytesIO()
        templatefile = BytesIO(htmltemplate.encode())
        assert po2html.converthtml(inputfile, outputfile, templatefile, includefuzzy)
        print(outputfile.getvalue())
        return outputfile.getvalue().decode('utf-8')

    def test_simple(self):
        """simple po to html test"""
        htmlsource = '<p>A sentence.</p>'
        posource = '''#: html:3\nmsgid "A sentence."\nmsgstr "'n Sin."\n'''
        htmlexpected = '''<p>'n Sin.</p>'''
        assert htmlexpected in self.converthtml(posource, htmlsource)

    def test_linebreaks(self):
        """Test that a po file can be merged into a template with linebreaks in it."""
        htmlsource = '''<html>
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
'''
        posource = '''#: None:1
msgid ""
"A paragraph is a section in a piece of writing, usually highlighting a "
"particular point or topic. It always begins on a new line and usually with "
"indentation, and it consists of at least one sentence."
msgstr ""
"'n Paragraaf is 'n afdeling in 'n geskrewe stuk wat gewoonlik 'n spesifieke "
"punt uitlig. Dit begin altyd op 'n nuwe lyn (gewoonlik met indentasie) en "
"dit bestaan uit ten minste een sin."
'''
        htmlexpected = '''<body>
<div>
'n Paragraaf is 'n afdeling in 'n geskrewe stuk wat gewoonlik
'n spesifieke punt uitlig. Dit begin altyd op 'n nuwe lyn
(gewoonlik met indentasie) en dit bestaan uit ten minste een
sin.
</div>
</body>'''
        assert htmlexpected.replace("\n", " ") in self.converthtml(posource, htmlsource).replace("\n", " ")

    def test_replace_substrings(self):
        """Should replace substrings correctly, issue #3416"""
        htmlsource = '''<!DOCTYPE html><html><head><title>sub-strings substitution</title></head><body>
<h2>This is heading 2</h2>
<p>The heading says: <b>This is heading 2</b></p>
</body></html>'''
        posource = '#:html.body.h2:2-1\nmsgid "This is heading 2"\nmsgstr "Αυτή είναι μία Ετικέτα 2"\n\n#html.body.p:3-1\nmsgid "The heading says: <b>This is heading 2</b>"\nmsgstr "Η ετικέτα λέει: <b>Αυτή είναι μία Ετικέτα 2</b>"\n'
        htmlexpected = '''<!DOCTYPE html><html><head><title>sub-strings substitution</title></head><body>
<h2>Αυτή είναι μία Ετικέτα 2</h2>
<p>Η ετικέτα λέει: <b>Αυτή είναι μία Ετικέτα 2</b></p>
</body></html>'''
        assert htmlexpected in self.converthtml(posource, htmlsource)

    def test_attribute_outside_translatable_content(self):
        htmlsource = '<img alt="a picture"><p>A sentence.</p>'
        posource = '''#: html:3\nmsgid "A sentence."\nmsgstr "'n Sin."\n#: html:1\nmsgid "a picture"\nmsgstr "n prentjie"\n'''
        htmlexpected = '''<img alt="n prentjie"><p>'n Sin.</p>'''
        assert htmlexpected in self.converthtml(posource, htmlsource)

    def test_attribute_within_translatable_content_not_embedded(self):
        htmlsource = '<p><img alt="a picture">A sentence.</p>'
        posource = '''#: html:3\nmsgid "A sentence."\nmsgstr "'n Sin."\n#: html:1\nmsgid "a picture"\nmsgstr "n prentjie"\n'''
        htmlexpected = '''<p><img alt="n prentjie">'n Sin.</p>'''
        assert htmlexpected in self.converthtml(posource, htmlsource)

    def test_attribute_embedded_within_translatable_content(self):
        htmlsource = '<p>A sentence<img alt="a picture">.</p>'
        posource = '''#: html:3\nmsgid "A sentence<img alt="a picture">."\nmsgstr "'n Sin<img alt="n prentjie">."\n'''
        htmlexpected = '''<p>'n Sin<img alt="n prentjie">.</p>'''
        assert htmlexpected in self.converthtml(posource, htmlsource)

    def test_attribute_without_value(self):
        htmlsource = '<ul><li><a href="logoColor.eps" download>EPS färg</a></li></ul>'
        posource = '''#: html:3\nmsgid "EPS färg"\nmsgstr "EPS color"\n'''
        htmlexpected = '''<li><a href="logoColor.eps" download>EPS color</a></li>'''
        assert htmlexpected in self.converthtml(posource, htmlsource)

    def test_entities(self):
        """Tests that entities are handled correctly"""
        htmlsource = '<p>5 less than 6</p>'
        posource = '#:html:3\nmsgid "5 less than 6"\nmsgstr "5 &lt; 6"\n'
        htmlexpected = '<p>5 &lt; 6</p>'
        assert htmlexpected in self.converthtml(posource, htmlsource)

        htmlsource = '<p>Fish &amp; chips</p>'
        posource = '#: html:3\nmsgid "Fish &amp; chips"\nmsgstr "Vis &amp; skyfies"\n'
        htmlexpected = '<p>Vis &amp; skyfies</p>'
        assert htmlexpected in self.converthtml(posource, htmlsource)

    def test_escapes(self):
        """Tests that PO escapes are correctly handled"""
        htmlsource = '<p>"leverage"</p>'
        posource = '#: html3\nmsgid "\\"leverage\\""\nmsgstr "\\"ek is dom\\""\n'
        htmlexpected = '<p>"ek is dom"</p>'
        assert htmlexpected in self.converthtml(posource, htmlsource)

    def test_states_translated(self):
        """Test that we use target when translated"""
        htmlsource = '<div>aaa</div>'
        posource = 'msgid "aaa"\nmsgstr "bbb"\n'
        htmltarget = '<div>bbb</div>'
        assert htmltarget in self.converthtml(posource, htmlsource)
        assert htmlsource not in self.converthtml(posource, htmlsource)

    def test_states_untranslated(self):
        """Test that we use source when a string is untranslated"""
        htmlsource = '<div>aaa</div>'
        posource = 'msgid "aaa"\nmsgstr ""\n'
        htmltarget = htmlsource
        assert htmltarget in self.converthtml(posource, htmlsource)

    def test_states_fuzzy(self):
        """Test that we use source when a string is fuzzy

        This fixes :issue:`3145`
        """
        htmlsource = '<div>aaa</div>'
        posource = '#: html:3\n#, fuzzy\nmsgid "aaa"\nmsgstr "bbb"\n'
        htmltarget = '<div>bbb</div>'
        # Don't use fuzzies
        assert htmltarget not in self.converthtml(posource, htmlsource, includefuzzy=False)
        assert htmlsource in self.converthtml(posource, htmlsource, includefuzzy=False)
        # Use fuzzies
        assert htmltarget in self.converthtml(posource, htmlsource, includefuzzy=True)
        assert htmlsource not in self.converthtml(posource, htmlsource, includefuzzy=True)

    def test_untranslated_attributes(self):
        """Verify that untranslated attributes are output as source, not dropped."""
        htmlsource = '<meta name="keywords" content="life, the universe, everything" />'
        posource = '#: test.html+:-1\nmsgid "life, the universe, everything"\nmsgstr ""'
        expected = '<meta name="keywords" content="life, the universe, everything" />'
        assert expected in self.converthtml(posource, htmlsource)


class TestPO2HtmlCommand(test_convert.TestConvertCommand, TestPO2Html):
    """Tests running actual po2oo commands on files"""
    convertmodule = po2html

    def test_help(self, capsys):
        """tests getting help"""
        options = test_convert.TestConvertCommand.test_help(self, capsys)
        options = self.help_check(options, "-t TEMPLATE, --template=TEMPLATE")
        options = self.help_check(options, "--threshold=PERCENT")
        options = self.help_check(options, "--fuzzy")
        options = self.help_check(options, "--nofuzzy", last=True)
