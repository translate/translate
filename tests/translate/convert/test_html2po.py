import os
from io import BytesIO

from translate.convert import html2po, po2html

from . import test_convert


class TestHTML2PO:
    @staticmethod
    def html2po(
        markup,
        duplicatestyle="msgctxt",
        keepcomments=False,
    ):
        """Helper to convert html to po without a file."""
        inputfile = BytesIO(markup.encode() if isinstance(markup, str) else markup)
        convertor = html2po.html2po()
        return convertor.convertfile(inputfile, "test", duplicatestyle, keepcomments)

    @staticmethod
    def po2html(posource, htmltemplate):
        """Helper to convert po to html without a file."""
        # Convert pofile object to bytes
        inputfile = BytesIO(bytes(posource))
        outputfile = BytesIO()
        templatefile = BytesIO(htmltemplate.encode())
        assert po2html.converthtml(inputfile, outputfile, templatefile)
        return outputfile.getvalue().decode("utf-8")

    @staticmethod
    def countunits(pofile, expected) -> None:
        """Helper to check that we got the expected number of messages."""
        actual = len(pofile.units)
        if actual > 0 and pofile.units[0].isheader():
            actual -= 1
        print(pofile)
        assert actual == expected

    @staticmethod
    def compareunit(pofile, unitnumber, expected) -> None:
        """Helper to validate a PO message."""
        if not pofile.units[0].isheader():
            unitnumber -= 1
        assert str(pofile.units[unitnumber].source) == str(expected)

    def check_single(self, markup, itemtext) -> None:
        """Checks that converting this markup produces a single element with value itemtext."""
        pofile = self.html2po(markup)
        self.countunits(pofile, 1)
        self.compareunit(pofile, 1, itemtext)

    def check_null(self, markup) -> None:
        """Checks that converting this markup produces no elements."""
        pofile = self.html2po(markup)
        self.countunits(pofile, 0)

    def check_phpsnippet(self, php) -> None:
        """Given a snippet of php, put it into an HTML shell and see if the results are as expected."""
        self.check_single(
            f'<html><head></head><body><p><a href="{php}/site.html">Body text</a></p></body></html>',
            "Body text",
        )
        self.check_single(
            f'<html><head></head><body><p>More things in <a href="{php}/site.html">Body text</a></p></body></html>',
            f'More things in <a href="{php}/site.html">Body text</a>',
        )
        self.check_single(f"<html><head></head><body><p>{php}</p></body></html>", php)

    def test_extract_lang_attribute_from_html_tag(self) -> None:
        """Test that the lang attribute is extracted from the html tag, issue #3884."""
        markup = """<!DOCTYPE html>
<html lang="en">
    <head>
        <title>translate lang attribute</title>
    </head>
    <body>
    </body>
</html>
"""
        pofile = self.html2po(markup)
        self.countunits(pofile, 2)
        self.compareunit(pofile, 1, "en")
        self.compareunit(pofile, 2, "translate lang attribute")

    def test_do_not_extract_lang_attribute_from_tags_other_than_html(self) -> None:
        """Test that the lang attribute is extracted from the html tag."""
        self.check_single('<p><span lang="fr">Français</span></p>', "Français")

    def test_title(self) -> None:
        """Test that we can extract the <title> tag."""
        self.check_single(
            "<html><head><title>My title</title></head><body></body></html>", "My title"
        )

    def test_title_with_linebreak(self) -> None:
        """Test a linebreak in the <title> tag."""
        htmltext = """<html>
<head>
  <title>My
title</title>
</head>
<body>
</body>
</html>
"""
        self.check_single(htmltext, "My title")

    def test_meta(self) -> None:
        """Test that we can extract certain <meta> info from <head>."""
        self.check_single(
            """<html><head><meta name="keywords" content="these are keywords"></head><body></body></html>""",
            "these are keywords",
        )

    def test_tag_p(self) -> None:
        """Test that we can extract the <p> tag."""
        self.check_single(
            "<html><head></head><body><p>A paragraph.</p></body></html>", "A paragraph."
        )

    def test_tag_p_with_br(self) -> None:
        """Test that we can extract the <p> tag with an embedded <br> element."""
        markup = "<p>First line.<br>Second line.</p>"
        pofile = self.html2po(markup)
        self.compareunit(pofile, 1, "First line.<br>Second line.")

    def test_tag_p_with_linebreak(self) -> None:
        """Test newlines within the <p> tag."""
        htmltext = """<html>
<head>
</head>
<body>
<p>
A paragraph is a section in a piece of writing, usually highlighting a
particular point or topic. It always begins on a new line and usually
with indentation, and it consists of at least one sentence.
</p>
</body>
</html>
"""
        self.check_single(
            htmltext,
            "A paragraph is a section in a piece of writing, usually highlighting a particular point or topic. It always begins on a new line and usually with indentation, and it consists of at least one sentence.",
        )

    def test_tag_p_with_linebreak_and_embedded_br(self) -> None:
        """Test newlines within the <p> tag when there is an embedded <br> element."""
        markup = "<p>First\nline.<br>Second\nline.</p>"
        pofile = self.html2po(markup)
        self.compareunit(pofile, 1, "First line.<br>Second line.")

    def test_uppercase_html(self) -> None:
        """Should ignore the casing of the html tags."""
        self.check_single(
            "<HTML><HEAD></HEAD><BODY><P>A paragraph.</P></BODY></HTML>", "A paragraph."
        )

    def test_tag_div(self) -> None:
        """Test that we can extract the <div> tag."""
        self.check_single(
            "<html><head></head><body><div>A paragraph.</div></body></html>",
            "A paragraph.",
        )
        markup = "<div>First line.<br>Second line.</div>"
        pofile = self.html2po(markup)
        self.compareunit(pofile, 1, "First line.<br>Second line.")

    def test_tag_div_with_linebreaks(self) -> None:
        """Test linebreaks within a <div> tag."""
        htmltext = """<html>
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
        self.check_single(
            htmltext,
            "A paragraph is a section in a piece of writing, usually highlighting a particular point or topic. It always begins on a new line and usually with indentation, and it consists of at least one sentence.",
        )
        markup = "<div>First\nline.<br>Second\nline.</div>"
        pofile = self.html2po(markup)
        self.compareunit(pofile, 1, "First line.<br>Second line.")

    def test_tag_a(self) -> None:
        """Test that we can extract the <a> tag."""
        self.check_single(
            '<html><head></head><body><p>A paragraph with <a href="http://translate.org.za/">hyperlink</a>.</p></body></html>',
            'A paragraph with <a href="http://translate.org.za/">hyperlink</a>.',
        )

    def test_tag_a_with_linebreak(self) -> None:
        """Test that we can extract the <a> tag with newlines in it."""
        htmltext = """<html>
<head>
</head>
<body>
<p>A
paragraph
with <a
href="http://translate.org.za/">hyperlink</a>
and
newlines.</p></body></html>
"""
        self.check_single(
            htmltext,
            'A paragraph with <a href="http://translate.org.za/">hyperlink</a> and newlines.',
        )

    def test_sequence_of_anchor_elements(self) -> None:
        """Test that we can extract a sequence of anchor elements without mixing up start/end tags, issue #3768."""
        self.check_single(
            '<p><a href="https://example.com">This is a link</a> but this is not. <a href="https://example.com">However this is too</a></p>',
            '<a href="https://example.com">This is a link</a> but this is not. <a href="https://example.com">However this is too</a>',
        )

    def test_tag_img(self) -> None:
        """Test that we can extract the alt attribute from the <img> tag."""
        self.check_single(
            """<html><head></head><body><img src="picture.png" alt="A picture"></body></html>""",
            "A picture",
        )

    def test_img_empty(self) -> None:
        """Test that we can extract the alt attribute from the <img> tag."""
        htmlsource = """<html><head></head><body><img src="images/topbar.jpg" width="750" height="80"></body></html>"""
        self.check_null(htmlsource)

    def test_tag_img_inside_a(self) -> None:
        """Test that we can extract the alt attribute from the <img> tag when the img is embedded in a link."""
        self.check_single(
            """<html><head></head><body><p><a href="#"><img src="picture.png" alt="A picture" /></a></p></body></html>""",
            "A picture",
        )

    def test_tag_table_summary(self) -> None:
        """Test that we can extract the summary attribute."""
        self.check_single(
            """<html><head></head><body><table summary="Table summary"></table></body></html>""",
            "Table summary",
        )

    def test_table_simple(self) -> None:
        """Test that we can fully extract a simple table."""
        markup = """<html><head></head><body><table><tr><th>Heading One</th><th>Heading Two</th></tr><tr><td>One</td><td>Two</td></tr></table></body></html>"""
        pofile = self.html2po(markup)
        self.countunits(pofile, 4)
        self.compareunit(pofile, 1, "Heading One")
        self.compareunit(pofile, 2, "Heading Two")
        self.compareunit(pofile, 3, "One")
        self.compareunit(pofile, 4, "Two")

    def test_table_complex(self) -> None:
        markup = """<table summary="This is the summary"><caption>A caption</caption><thead><tr><th abbr="Head 1">Heading One</th><th>Heading Two</th></tr></thead><tfoot><tr><td>Foot One</td><td>Foot Two</td></tr></tfoot><tbody><tr><td>One</td><td>Two</td></tr></tbody></table>"""
        pofile = self.html2po(markup)
        self.countunits(pofile, 9)
        self.compareunit(pofile, 1, "This is the summary")
        self.compareunit(pofile, 2, "A caption")
        self.compareunit(pofile, 3, "Head 1")
        self.compareunit(pofile, 4, "Heading One")
        self.compareunit(pofile, 5, "Heading Two")
        self.compareunit(pofile, 6, "Foot One")
        self.compareunit(pofile, 7, "Foot Two")
        self.compareunit(pofile, 8, "One")
        self.compareunit(pofile, 9, "Two")

    def test_table_empty(self) -> None:
        """
        Test that we ignore tables that are empty.

        A table is deemed empty if it has no translatable content.
        """
        self.check_null(
            """<html><head></head><body><table><tr><td><img src="bob.png"></td></tr></table></body></html>"""
        )
        self.check_null(
            """<html><head></head><body><table><tr><td>&nbsp;</td></tr></table></body></html>"""
        )
        self.check_null(
            """<html><head></head><body><table><tr><td><strong></strong></td></tr></table></body></html>"""
        )

    def test_address(self) -> None:
        """Test to see if the address element is extracted."""
        self.check_single("<body><address>My address</address></body>", "My address")

    def test_headings(self) -> None:
        """Test to see if the h* elements are extracted."""
        markup = "<html><head></head><body><h1>Heading One</h1><h2>Heading Two</h2><h3>Heading Three</h3><h4>Heading Four</h4><h5>Heading Five</h5><h6>Heading Six</h6></body></html>"
        pofile = self.html2po(markup)
        self.countunits(pofile, 6)
        self.compareunit(pofile, 1, "Heading One")
        self.compareunit(pofile, 2, "Heading Two")
        self.compareunit(pofile, 3, "Heading Three")
        self.compareunit(pofile, 4, "Heading Four")
        self.compareunit(pofile, 5, "Heading Five")
        self.compareunit(pofile, 6, "Heading Six")

    def test_headings_with_linebreaks(self) -> None:
        """Test to see if h* elements with newlines can be extracted."""
        markup = "<html><head></head><body><h1>Heading\nOne</h1><h2>Heading\nTwo</h2><h3>Heading\nThree</h3><h4>Heading\nFour</h4><h5>Heading\nFive</h5><h6>Heading\nSix</h6></body></html>"
        pofile = self.html2po(markup)
        self.countunits(pofile, 6)
        self.compareunit(pofile, 1, "Heading One")
        self.compareunit(pofile, 2, "Heading Two")
        self.compareunit(pofile, 3, "Heading Three")
        self.compareunit(pofile, 4, "Heading Four")
        self.compareunit(pofile, 5, "Heading Five")
        self.compareunit(pofile, 6, "Heading Six")

    def test_dt(self) -> None:
        """Test to see if the definition list title (dt) element is extracted."""
        self.check_single(
            "<html><head></head><body><dl><dt>Definition List Item Title</dt></dl></body></html>",
            "Definition List Item Title",
        )

    def test_dd(self) -> None:
        """Test to see if the definition list description (dd) element is extracted."""
        self.check_single(
            "<html><head></head><body><dl><dd>Definition List Item Description</dd></dl></body></html>",
            "Definition List Item Description",
        )

    def test_span(self) -> None:
        """Test to check that we don't double extract a span item."""
        self.check_single(
            "<html><head></head><body><p>You are a <span>Spanish</span> sentence.</p></body></html>",
            "You are a <span>Spanish</span> sentence.",
        )

    def test_standalone_span(self) -> None:
        """Standalone spans should be extracted and translated, issue #1610."""
        htmlsource = (
            "<html><head></head><body>"
            "<span>First span</span><span>Second span</span>"
            "</body></html>"
        )
        pofile = self.html2po(htmlsource)
        self.countunits(pofile, 2)
        self.compareunit(pofile, 1, "First span")
        self.compareunit(pofile, 2, "Second span")

        pofile.units[1].target = "Premier span"
        pofile.units[2].target = "Deuxième span"
        assert self.po2html(pofile, htmlsource) == (
            "<html><head></head><body>"
            "<span>Premier span</span><span>Deuxième span</span>"
            "</body></html>"
        )

    def test_nested_standalone_span(self) -> None:
        """Nested spans should remain inline in a standalone span unit."""
        self.check_single(
            "<html><head></head><body>"
            "<span>Outer <span>inner</span> text</span>"
            "</body></html>",
            "Outer <span>inner</span> text",
        )

    def test_standalone_span_with_ignored_descendant(self) -> None:
        """Ignored descendants should retain their position in standalone spans."""
        htmlsource = "<span>before <em data-translate-ignore>skip</em> after</span>"
        pofile = self.html2po(htmlsource)
        self.countunits(pofile, 2)
        self.compareunit(pofile, 1, "before")
        self.compareunit(pofile, 2, "after")

        pofile.units[1].target = "avant"
        pofile.units[2].target = "après"
        assert self.po2html(pofile, htmlsource) == (
            "<span>avant <em data-translate-ignore>skip</em> après</span>"
        )

    def test_standalone_span_with_comment_ignored_descendant(self) -> None:
        """Comment-ignored descendants should retain their position in spans."""
        htmlsource = (
            "<span>before <!-- translate:off --><em>skip</em>"
            "<!-- translate:on --> after</span>"
        )
        pofile = self.html2po(htmlsource)
        self.countunits(pofile, 2)
        self.compareunit(pofile, 1, "before")
        self.compareunit(pofile, 2, "after")

        pofile.units[1].target = "avant"
        pofile.units[2].target = "après"
        assert self.po2html(pofile, htmlsource) == (
            "<span>avant <!-- translate:off --><em>skip</em>"
            "<!-- translate:on --> après</span>"
        )

    def test_resumed_span_inherits_metadata(self) -> None:
        """A resumed span unit should inherit context and translator comments."""
        pofile = self.html2po(
            '<span data-translate-context="cta" '
            'data-translate-comment="Button label">'
            "<i data-translate-ignore>skip</i>Save</span>",
            keepcomments=True,
        )
        self.countunits(pofile, 1)
        self.compareunit(pofile, 1, "Save")
        assert pofile.units[1].getcontext() == "cta"
        assert str(pofile.units[1].getnotes()) == "Button label"

    def test_resumed_preformatted_span_preserves_whitespace(self) -> None:
        """A resumed preformatted unit should not normalize whitespace."""
        htmlsource = "<pre><i data-translate-ignore>skip</i>a  b\n c</pre>"
        pofile = self.html2po(htmlsource)
        self.countunits(pofile, 1)
        self.compareunit(pofile, 1, "a  b\n c")

        pofile.units[1].target = "x  y\n z"
        assert self.po2html(pofile, htmlsource) == (
            "<pre><i data-translate-ignore>skip</i>x  y\n z</pre>"
        )

    def test_translate_on_resumes_active_child(self) -> None:
        """translate:on should resume the child opened in the ignored region."""
        htmlsource = (
            "<div>before<!-- translate:off --><p>skip"
            "<!-- translate:on -->text</p>after</div>"
        )
        pofile = self.html2po(htmlsource)
        self.countunits(pofile, 3)
        self.compareunit(pofile, 1, "before")
        self.compareunit(pofile, 2, "text")
        self.compareunit(pofile, 3, "after")

        pofile.units[1].target = "avant"
        pofile.units[2].target = "texte"
        pofile.units[3].target = "après"
        assert self.po2html(pofile, htmlsource) == (
            "<div>avant<!-- translate:off --><p>skip"
            "<!-- translate:on -->texte</p>après</div>"
        )

    def test_translate_on_resumes_child_without_active_ancestor(self) -> None:
        """translate:on should activate an eligible child opened while ignored."""
        htmlsource = "<!-- translate:off --><p>skip<!-- translate:on -->text</p>"
        pofile = self.html2po(htmlsource)
        self.countunits(pofile, 1)
        self.compareunit(pofile, 1, "text")

        pofile.units[1].target = "texte"
        assert self.po2html(pofile, htmlsource) == (
            "<!-- translate:off --><p>skip<!-- translate:on -->texte</p>"
        )

    def test_translate_on_resumes_later_sibling(self) -> None:
        """An ignored region crossing siblings should resume the later child."""
        htmlsource = (
            "<div><p><!-- translate:off --></p>"
            "<p>skip<!-- translate:on -->text</p>after</div>"
        )
        pofile = self.html2po(htmlsource)
        self.countunits(pofile, 2)
        self.compareunit(pofile, 1, "text")
        self.compareunit(pofile, 2, "after")

        pofile.units[1].target = "texte"
        pofile.units[2].target = "après"
        assert self.po2html(pofile, htmlsource) == (
            "<div><p><!-- translate:off --></p>"
            "<p>skip<!-- translate:on -->texte</p>après</div>"
        )

    def test_ul(self) -> None:
        """Test to see if the list item <li> is extracted."""
        markup = "<html><head></head><body><ul><li>Unordered One</li><li>Unordered Two</li></ul><ol><li>Ordered One</li><li>Ordered Two</li></ol></body></html>"
        pofile = self.html2po(markup)
        self.countunits(pofile, 4)
        self.compareunit(pofile, 1, "Unordered One")
        self.compareunit(pofile, 2, "Unordered Two")
        self.compareunit(pofile, 3, "Ordered One")
        self.compareunit(pofile, 4, "Ordered Two")

    def test_nested_lists(self) -> None:
        """Nested lists should be extracted correctly."""
        markup = """<!DOCTYPE html><html><head><title>Nested lists</title></head><body>
<ul>
    <li>Vegetables</li>
    <li>Fruit
        <ul>
            <li>Bananas</li>
            <li>Apples</li>
            <li>Pears</li>
        </ul>
        yeah, that should be enough
    </li>
    <li>Meat</li>
</ul>
</body></html>"""
        pofile = self.html2po(markup)
        self.countunits(pofile, 8)
        self.compareunit(pofile, 1, "Nested lists")
        self.compareunit(pofile, 2, "Vegetables")
        self.compareunit(pofile, 3, "Fruit")
        self.compareunit(pofile, 4, "Bananas")
        self.compareunit(pofile, 5, "Apples")
        self.compareunit(pofile, 6, "Pears")
        self.compareunit(pofile, 7, "yeah, that should be enough")
        self.compareunit(pofile, 8, "Meat")

    def test_duplicates(self) -> None:
        """Check that we use the default style of msgctxt to disambiguate duplicate messages."""
        markup = (
            "<html><head></head><body><p>Duplicate</p><p>Duplicate</p></body></html>"
        )
        pofile = self.html2po(markup)
        self.countunits(pofile, 2)
        # FIXME change this so that we check that the msgctxt is correctly added
        self.compareunit(pofile, 1, "Duplicate")
        assert pofile.units[1].getlocations() == ["None+html.body.p:1-26"]
        self.compareunit(pofile, 2, "Duplicate")
        assert pofile.units[2].getlocations() == ["None+html.body.p:1-42"]

    def test_multiline_reflow(self) -> None:
        """Check that we reflow multiline content to make it more readable for translators."""
        self.check_single(
            """<td valign="middle" width="96%"><font class="headingwhite">South
                  Africa</font></td>""",
            """South Africa""",
        )

    def test_nested_tags(self) -> None:
        """Check that we can extract items within nested tags."""
        markup = "<div><p>Extract this</p>And this</div>"
        pofile = self.html2po(markup)
        self.countunits(pofile, 2)
        self.compareunit(pofile, 1, "Extract this")
        self.compareunit(pofile, 2, "And this")

    def test_carriage_return(self) -> None:
        """Remove carriage returns from files in dos format."""
        htmlsource = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">\r
<html><!-- InstanceBegin template="/Templates/masterpage.dwt" codeOutsideHTMLIsLocked="false" -->\r
<head>\r
<!-- InstanceBeginEditable name="doctitle" -->\r
<link href="fmfi.css" rel="stylesheet" type="text/css">\r
</head>\r
\r
<body>\r
<p>The rapid expansion of telecommunications infrastructure in recent\r
years has helped to bridge the digital divide to a limited extent.</p> \r
</body>\r
<!-- InstanceEnd --></html>\r
"""

        self.check_single(
            htmlsource,
            "The rapid expansion of telecommunications infrastructure in recent years has helped to bridge the digital divide to a limited extent.",
        )

    def test_encoding_latin1(self) -> None:
        """
        Convert HTML input in windows-1250 correctly to unicode.

        Also verifies that the charset declaration isn't extracted as a translation unit.
        """
        htmlsource = b"""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html><!-- InstanceBegin template="/Templates/masterpage.dwt" codeOutsideHTMLIsLocked="false" -->
<head>
<!-- InstanceBeginEditable name="doctitle" -->
<title>FMFI - South Africa - CSIR Openphone - Overview</title>
<!-- InstanceEndEditable -->
<meta http-equiv="Content-Type" content="text/html; charset=windows-1250">
<meta name="keywords" content="fmfi, first mile, first inch, wireless, rural development, access devices, mobile devices, wifi, connectivity, rural connectivity, ict, low cost, cheap, digital divide, csir, idrc, community">

<!-- InstanceBeginEditable name="head" -->
<!-- InstanceEndEditable -->
<link href="../../../fmfi.css" rel="stylesheet" type="text/css">
</head>

<body>
<p>We aim to please \x96 will you aim too, please?</p>
<p>South Africa\x92s language diversity can be challenging.</p>
</body>
</html>
"""
        pofile = self.html2po(htmlsource)
        self.countunits(pofile, 4)
        self.compareunit(pofile, 1, "FMFI - South Africa - CSIR Openphone - Overview")
        self.compareunit(
            pofile,
            2,
            "fmfi, first mile, first inch, wireless, rural development, access devices, mobile devices, wifi, connectivity, rural connectivity, ict, low cost, cheap, digital divide, csir, idrc, community",
        )
        self.compareunit(pofile, 3, "We aim to please – will you aim too, please?")
        self.compareunit(
            pofile, 4, "South Africa’s language diversity can be challenging."
        )

    def test_encoding_http_equiv_attribute_order(self) -> None:
        """Detect charset regardless of meta attribute order, issue #909."""
        self.check_single(
            b'<meta content="text/html; charset=windows-1250" '
            b'http-equiv="content-type"><p>South Africa\x92s language</p>',
            "South Africa’s language",
        )

    def test_encoding_ignores_custom_charset_attribute(self) -> None:
        """Custom attributes containing charset must not control decoding."""
        self.check_single(
            '<meta charset="UTF-8" data-charset="windows-1252">'
            "<p>South Africa’s language</p>",
            "South Africa’s language",
        )

    def test_strip_html(self) -> None:
        """Ensure that unnecessary html is stripped from the resulting unit."""
        htmlsource = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
<title>FMFI - Contact</title>
</head>
<body>
<table width="100%"  border="0" cellpadding="0" cellspacing="0">
  <tr align="left" valign="top">
    <td width="150" height="556">
      <table width="157" height="100%" border="0" cellspacing="0" id="leftmenubg-color">
      <tr>
          <td align="left" valign="top" height="555">
            <table width="100%" border="0" cellspacing="0" cellpadding="2">
              <tr align="left" valign="top" bgcolor="#660000">
                <td width="4%"><strong></strong></td>
                <td width="96%"><strong><font class="headingwhite">Projects</font></strong></td>
              </tr>
              <tr align="left" valign="top">
                <td valign="middle" width="4%"><img src="images/arrow.gif" width="8" height="8"></td>
                <td width="96%"><a href="index.html">Home Page</a></td>
              </tr>
            </table>
          </td>
      </tr>
      </table>
    </td>
  </tr>
</table>
</body>
</html>
"""
        pofile = self.html2po(htmlsource)
        self.countunits(pofile, 3)
        self.compareunit(pofile, 2, "Projects")
        self.compareunit(pofile, 3, "Home Page")

        # Translate and convert back:
        pofile.units[2].target = "Projekte"
        pofile.units[3].target = "Tuisblad"
        htmlresult = (
            self.po2html(bytes(pofile), htmlsource)
            .replace("\n", " ")
            .replace('= "', '="')
            .replace("> <", "><")
        )
        snippet = '<td width="96%"><strong><font class="headingwhite">Projekte</font></strong></td>'
        assert snippet in htmlresult
        snippet = '<td width="96%"><a href="index.html">Tuisblad</a></td>'
        assert snippet in htmlresult

    def test_entityrefs_in_text(self) -> None:
        """
        Should extract html entityrefs, preserving the ones representing reserved characters.

        `See <https://developer.mozilla.org/en-US/docs/Glossary/Entity>`.
        """
        self.check_single(
            "<html><head></head><body><p>&lt;not an element&gt; &amp; &quot; &apos; &rsquo;</p></body></html>",
            "&lt;not an element&gt; &amp; \" ' \u2019",
        )

    def test_entityrefs_in_attributes(self) -> None:
        """Should convert html entityrefs in attribute values."""
        # it would be even nicer if &quot; and &apos; could be preserved, but the automatic unescaping of
        # attributes is deep inside html.HTMLParser.
        self.check_single(
            '<html><head></head><body><img alt="&lt;not an element&gt; &amp; &quot; &apos; &rsquo;"></body></html>',
            "<not an element> & \" ' \u2019",
        )

    def test_charrefs(self) -> None:
        """Should extract html charrefs."""
        self.check_single(
            "<html><head></head><body><p>&#8217; &#x2019;</p></body></html>",
            "\u2019 \u2019",
        )

    def test_php(self) -> None:
        """Test that PHP snippets don't interfere."""
        # A simple string
        self.check_phpsnippet("""<?=$phpvariable?>""")

        # Contains HTML tag characters (< and >)
        self.check_phpsnippet("""<?=($a < $b ? $foo : ($b > c ? $bar : $cat))?>""")

        # Make sure basically any symbol can be handled
        # NOTE quotation mark removed since it violates the HTML format when placed in an attribute
        self.check_phpsnippet(
            """<? asdfghjkl qwertyuiop 1234567890!@#$%^&*()-=_+[]\\{}|;':,./<>? ?>"""
        )

    def test_multiple_php(self) -> None:
        """Test multiple PHP snippets in a string to make sure they get restored properly."""
        php1 = """<?=$phpvariable?>"""
        php2 = """<?=($a < $b ? $foo : ($b > c ? $bar : $cat))?>"""
        php3 = """<? asdfghjklqwertyuiop1234567890!@#$%^&*()-=_+[]\\{}|;':",./<>? ?>"""

        # Put 3 different strings into an html string
        innertext = f'<a href="{php1}/site.html">Body text</a> and some {php2} more text {php2}{php3}'
        htmlsource = f"<html><head></head><body><p>{innertext}</p></body></html>"
        self.check_single(htmlsource, innertext)

    def test_php_multiline(self) -> None:
        # A multi-line php string to test
        php1 = """<? abc
def
ghi ?>"""

        # Scatter the php strings throughout the file, and show what the translation should be
        innertext = f'<a href="{php1}/site.html">Body text</a> and some {php1} more text {php1}{php1}'
        innertrans = f'<a href="{php1}/site.html">Texte de corps</a> et encore de {php1} plus de texte {php1}{php1}'

        htmlsource = f"<html><head></head><body><p>{innertext}</p></body></html>"  # Current html file
        transsource = f"<html><head></head><body><p>{innertrans}</p></body></html>"  # Expected translation

        pofile = self.html2po(htmlsource)
        pofile.units[1].target = innertrans  # Register the translation in the PO file
        htmlresult = self.po2html(pofile, htmlsource)
        assert htmlresult == transsource

    def test_php_with_embedded_html(self) -> None:
        """Should not consume HTML within processing instructions."""
        self.check_single(
            "<html><head></head><body><p>a <? <p>b</p> ?> c</p></body></html>",
            "a <? <p>b</p> ?> c",
        )

    def test_comments(self) -> None:
        """Test that HTML comments are converted to translator notes in output."""
        pofile = self.html2po(
            "<!-- comment outside block --><p><!-- a comment -->A paragraph<!-- with another comment -->.</p>",
            keepcomments=True,
        )
        self.compareunit(pofile, 1, "A paragraph.")
        notes = pofile.getunits()[-1].getnotes()
        assert str(notes) == " a comment \n with another comment "

    def test_attribute_without_value(self) -> None:
        htmlsource = """<ul>
                <li><a href="logoColor.eps" download>EPS färg</a></li>
            </ul>
"""
        pofile = self.html2po(htmlsource)
        self.compareunit(pofile, 1, "EPS färg")

    def test_data_translate_ignore_attribute(self) -> None:
        """Test that elements with data-translate-ignore are not extracted."""
        # Simple case
        htmlsource = "<p>Translate this</p><p data-translate-ignore>Do not translate</p><p>Translate this too</p>"
        pofile = self.html2po(htmlsource)
        self.countunits(pofile, 2)
        self.compareunit(pofile, 1, "Translate this")
        self.compareunit(pofile, 2, "Translate this too")

        # Nested elements within ignored section
        htmlsource = "<div>Translate this</div><div data-translate-ignore><p>Do not translate</p><span>Also ignore</span></div><div>Translate this too</div>"
        pofile = self.html2po(htmlsource)
        self.countunits(pofile, 2)
        self.compareunit(pofile, 1, "Translate this")
        self.compareunit(pofile, 2, "Translate this too")

        # Attributes in ignored elements should not be extracted
        htmlsource = '<p title="Extract this">Translate</p><p data-translate-ignore title="Do not extract">Do not translate</p>'
        pofile = self.html2po(htmlsource)
        self.countunits(pofile, 2)
        self.compareunit(pofile, 1, "Extract this")
        self.compareunit(pofile, 2, "Translate")

        # Self-closing tags with data-translate-ignore should not have attributes extracted
        htmlsource = '<img alt="Extract this" /><img alt="Do not extract" data-translate-ignore /><p>Translate</p>'
        pofile = self.html2po(htmlsource)
        self.countunits(pofile, 2)
        self.compareunit(pofile, 1, "Extract this")
        self.compareunit(pofile, 2, "Translate")

    def test_translate_comment_directives(self) -> None:
        """Test that translate:off and translate:on comments work."""
        # Basic case
        htmlsource = "<p>Translate this</p><!-- translate:off --><p>Do not translate</p><!-- translate:on --><p>Translate this too</p>"
        pofile = self.html2po(htmlsource)
        self.countunits(pofile, 2)
        self.compareunit(pofile, 1, "Translate this")
        self.compareunit(pofile, 2, "Translate this too")

        # Multiple elements between translate:off and translate:on
        htmlsource = "<div>Translate</div><!-- translate:off --><p>Skip 1</p><p>Skip 2</p><div>Skip 3</div><!-- translate:on --><p>Translate again</p>"
        pofile = self.html2po(htmlsource)
        self.countunits(pofile, 2)
        self.compareunit(pofile, 1, "Translate")
        self.compareunit(pofile, 2, "Translate again")

        # translate:off without translate:on should ignore rest of document
        htmlsource = "<p>Translate this</p><!-- translate:off --><p>Do not translate 1</p><p>Do not translate 2</p>"
        pofile = self.html2po(htmlsource)
        self.countunits(pofile, 1)
        self.compareunit(pofile, 1, "Translate this")

    def test_meta_social_media_tags(self) -> None:
        """Test that we can extract common social media meta tags."""
        # Test Open Graph tags
        markup = """<html><head>
        <meta property="og:title" content="My Page Title">
        <meta property="og:description" content="A description of my page">
        <meta property="og:site_name" content="My Website">
        </head><body></body></html>"""
        pofile = self.html2po(markup)
        self.countunits(pofile, 3)
        self.compareunit(pofile, 1, "My Page Title")
        self.compareunit(pofile, 2, "A description of my page")
        self.compareunit(pofile, 3, "My Website")

        # Test Twitter Card tags
        markup = """<html><head>
        <meta name="twitter:title" content="My Tweet Title">
        <meta name="twitter:description" content="A tweet description">
        </head><body></body></html>"""
        pofile = self.html2po(markup)
        self.countunits(pofile, 2)
        self.compareunit(pofile, 1, "My Tweet Title")
        self.compareunit(pofile, 2, "A tweet description")

    def test_meta_non_translatable_tags_not_extracted(self) -> None:
        """Test that non-translatable meta tags are not extracted."""
        markup = """<html><head>
        <meta property="og:image" content="https://example.com/image.jpg">
        <meta property="og:url" content="https://example.com/page">
        <meta property="og:type" content="website">
        <meta name="twitter:card" content="summary_large_image">
        <meta name="twitter:image" content="https://example.com/twitter-image.jpg">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head><body></body></html>"""
        self.check_null(markup)

    def test_meta_mixed_translatable_and_non_translatable(self) -> None:
        """Test that translatable and non-translatable meta tags are handled correctly when mixed."""
        markup = """<html><head>
        <meta property="og:title" content="My Page Title">
        <meta property="og:image" content="https://example.com/image.jpg">
        <meta property="og:description" content="Page description">
        <meta property="og:url" content="https://example.com/">
        <meta name="twitter:card" content="summary">
        <meta name="twitter:title" content="Twitter Title">
        </head><body></body></html>"""
        pofile = self.html2po(markup)
        self.countunits(pofile, 3)
        self.compareunit(pofile, 1, "My Page Title")
        self.compareunit(pofile, 2, "Page description")
        self.compareunit(pofile, 3, "Twitter Title")

    def test_data_translate_comment_attribute(self) -> None:
        """Test that data-translate-comment attribute is extracted as automatic comment."""
        # Single element with data-translate-comment
        markup = '<h1 data-translate-comment="This is the first text">Hello world!</h1>'
        pofile = self.html2po(markup, keepcomments=True)
        self.countunits(pofile, 1)
        self.compareunit(pofile, 1, "Hello world!")
        unit = pofile.units[1] if pofile.units[0].isheader() else pofile.units[0]
        assert unit.getnotes(origin="developer") == "This is the first text"

        # Multiple elements with data-translate-comment
        markup = '<h1 data-translate-comment="Header comment">Header</h1><p data-translate-comment="Paragraph comment">Paragraph text</p>'
        pofile = self.html2po(markup, keepcomments=True)
        self.countunits(pofile, 2)
        self.compareunit(pofile, 1, "Header")
        unit = pofile.units[1] if pofile.units[0].isheader() else pofile.units[0]
        assert unit.getnotes(origin="developer") == "Header comment"
        self.compareunit(pofile, 2, "Paragraph text")
        unit = pofile.units[2] if pofile.units[0].isheader() else pofile.units[1]
        assert unit.getnotes(origin="developer") == "Paragraph comment"

        # Element with both HTML comment and data-translate-comment (comment inside unit)
        markup = '<h1 data-translate-comment="Attribute comment"><!-- HTML comment -->Title</h1>'
        pofile = self.html2po(markup, keepcomments=True)
        self.countunits(pofile, 1)
        self.compareunit(pofile, 1, "Title")
        unit = pofile.units[1] if pofile.units[0].isheader() else pofile.units[0]
        notes = unit.getnotes(origin="developer")
        assert " HTML comment " in notes
        assert "Attribute comment" in notes

    def test_data_translate_comment_without_keepcomments(self) -> None:
        """Test that data-translate-comment is not extracted when keepcomments is False."""
        markup = '<h1 data-translate-comment="This is the first text">Hello world!</h1>'
        pofile = self.html2po(markup, keepcomments=False)
        self.countunits(pofile, 1)
        self.compareunit(pofile, 1, "Hello world!")
        unit = pofile.units[1] if pofile.units[0].isheader() else pofile.units[0]
        # Comments should not be extracted when keepcomments=False
        assert unit.getnotes(origin="developer") == ""

    def test_resumed_comment_is_not_duplicated(self) -> None:
        """Reused fragments should not duplicate an inherited comment."""
        pofile = self.html2po(
            '<p data-translate-context="shared" data-translate-comment="note">'
            "Same<i data-translate-ignore>skip</i>Same</p>",
            keepcomments=True,
        )

        self.countunits(pofile, 1)
        unit = pofile.units[1] if pofile.units[0].isheader() else pofile.units[0]
        assert unit.getnotes(origin="developer") == "note"

    def test_text_after_empty_tags(self) -> None:
        """Test that text is extracted after empty tags (regression test for issue #xxx)."""
        # Test case from the original bug report
        markup = """<p></p>
<a></a>

<h2>7&nbsp;&nbsp;About using the OFL for your original fonts</h2>"""
        pofile = self.html2po(markup)
        self.countunits(pofile, 1)
        # Note: &nbsp; entities are normalized to regular spaces during whitespace normalization
        self.compareunit(pofile, 1, "7 About using the OFL for your original fonts")

        # Also test variations to ensure robustness
        markup2 = "<p></p><a></a><h2>Title text</h2>"
        pofile2 = self.html2po(markup2)
        self.countunits(pofile2, 1)
        self.compareunit(pofile2, 1, "Title text")


class TestHTML2POCommand(test_convert.TestConvertCommand, TestHTML2PO):
    """Tests running actual html2po commands on files."""

    convertmodule = html2po
    defaultoptions = {"progress": "none"}

    expected_options = [
        "-P, --pot",
        "-t TEMPLATE, --template=TEMPLATE",
        "--duplicates=DUPLICATESTYLE",
        "--keepcomments",
        "--multifile=MULTIFILESTYLE",
    ]

    def test_multifile_single(self) -> None:
        """Test the --multifile=single option and make sure it produces one pot file per input file."""
        self.create_testfile(
            "file1.html", "<div>You are only coming through in waves</div>"
        )
        self.create_testfile(
            "file2.html", "<div>Your lips move but I cannot hear what you say</div>"
        )
        self.run_command("./", "pots", pot=True, multifile="single")
        assert os.path.isfile(self.get_testfilename("pots/file1.pot"))
        assert os.path.isfile(self.get_testfilename("pots/file2.pot"))
        content = str(self.read_testfile("pots/file1.pot"))
        assert "coming through" in content
        assert "cannot hear" not in content

    def test_multifile_onefile(self) -> None:
        """Test the --multifile=onefile option and make sure it produces a file, not a directory."""
        self.create_testfile(
            "file1.html", "<div>You are only coming through in waves</div>"
        )
        self.create_testfile(
            "file2.html", "<div>Your lips move but I cannot hear what you say</div>"
        )
        self.run_command("./", "one.pot", pot=True, multifile="onefile")
        assert os.path.isfile(self.get_testfilename("one.pot"))
        content = str(self.read_testfile("one.pot"))
        assert "coming through" in content
        assert "cannot hear" in content

    def test_multifile_onefile_to_stdout(self, capsys) -> None:
        """Test the --multifile=onefile option without specifying an output file. Default is stdout."""
        self.create_testfile(
            "file1.html", "<div>You are only coming through in waves</div>"
        )
        self.create_testfile(
            "file2.html", "<div>Your lips move but I cannot hear what you say</div>"
        )
        self.run_command("./", pot=True, multifile="onefile")
        content, err = capsys.readouterr()
        assert "coming through" in content
        assert "cannot hear" in content
        assert err == ""

    def test_html_with_template_basic(self):
        """Test html2po with template file for basic matching."""
        # Create template (source language)
        self.create_testfile(
            "template.html",
            "<html><body><h1>Hello</h1><p>World</p></body></html>",
        )
        # Create translated file
        self.create_testfile(
            "translated.html",
            "<html><body><h1>Hola</h1><p>Mundo</p></body></html>",
        )
        # Run conversion with template
        self.run_command("translated.html", "output.po", template="template.html")

        # Verify output
        assert os.path.isfile(self.get_testfilename("output.po"))
        content = self.read_testfile("output.po").decode()
        assert "Hello" in content  # source
        assert "Hola" in content  # target
        assert "World" in content  # source
        assert "Mundo" in content  # target

    def test_html_with_template_complex(self):
        """Test html2po with template file for complex HTML structure."""
        # Create template (source language)
        template_html = """<html>
<body>
    <h1>Welcome</h1>
    <p>First paragraph</p>
    <p>Second paragraph</p>
    <ul>
        <li>Item 1</li>
        <li>Item 2</li>
    </ul>
</body>
</html>"""

        # Create translated file (same structure, different content)
        translated_html = """<html>
<body>
    <h1>Bienvenue</h1>
    <p>Premier paragraphe</p>
    <p>Deuxième paragraphe</p>
    <ul>
        <li>Article 1</li>
        <li>Article 2</li>
    </ul>
</body>
</html>"""

        self.create_testfile("template_complex.html", template_html)
        self.create_testfile("translated_complex.html", translated_html)

        # Run conversion
        self.run_command(
            "translated_complex.html",
            "output_complex.po",
            template="template_complex.html",
        )

        # Verify output
        assert os.path.isfile(self.get_testfilename("output_complex.po"))
        content = self.read_testfile("output_complex.po").decode()

        # Check source strings
        assert "Welcome" in content
        assert "First paragraph" in content
        assert "Second paragraph" in content
        assert "Item 1" in content
        assert "Item 2" in content

        # Check target strings
        assert "Bienvenue" in content
        assert "Premier paragraphe" in content
        assert "Deuxième paragraphe" in content
        assert "Article 1" in content
        assert "Article 2" in content
