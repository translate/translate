#
# Copyright 2010 Zuza Software Foundation
#
# This file is part of the Translate Toolkit.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""Tests for the HTML classes."""

from pytest import raises

from translate.storage import base, html


def test_guess_encoding():
    """Read an encoding header to guess the encoding correctly."""
    h = html.htmlfile()
    assert (
        h.guess_encoding(
            b"""<META HTTP-EQUIV="CONTENT-TYPE" CONTENT="text/html; charset=UTF-8">"""
        )
        == "UTF-8"
    )
    assert (
        h.guess_encoding(
            b"""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/REC-html40/loose.dtd"><html><head><meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1"><!-- base href="http://home.online.no/~rut-aane/linux.html" --><link rel="shortcut icon" href="http://home.online.no/~rut-aane/peng16x16a.gif"><meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1"><meta name="Description" content="Linux newbie stuff and a little about Watching TV under Linux"><meta name="MSSmartTagsPreventParsing" content="TRUE"><meta name="GENERATOR" content="Mozilla/4.7 [en] (X11; I; Linux 2.2.5-15 i586) [Netscape]"><title>Some Linux for beginners</title><style type="text/css">"""
        )
        == "iso-8859-1"
    )


class TestHTMLParsing:
    h = html.htmlfile

    def test_mismatched_tags(self):
        with raises(base.ParseError):
            self.h.parsestring("<h3><p>Some text<p></h3>")
        # First <tr> is not closed
        with raises(base.ParseError):
            self.h.parsestring(
                "<html><head></head><body><table><tr><th>Heading One</th><th>Heading Two</th><tr><td>One</td><td>Two</td></tr></table></body></html>"
            )
        # <tr> is not closed in <thead>
        with raises(base.ParseError):
            self.h.parsestring(
                """<table summary="This is the summary"><caption>A caption</caption><thead><tr><th abbr="Head 1">Heading One</th><th>Heading Two</th></thead><tfoot><tr><td>Foot One</td><td>Foot Two</td></tr></tfoot><tbody><tr><td>One</td><td>Two</td></tr></tbody></table>"""
            )

    def test_self_closing_tags(self):
        h = html.htmlfile()
        store = h.parsestring("<h3>Some text <img><br><img></h3>")
        assert len(store.units) == 1

    def test_escaping_script_and_pre(self):
        """
        <script> and <pre> can contain < and > and these should not be
        interpreted as tags.
        """
        h = html.htmlfile()
        store = h.parsestring(
            "<p>We are here</p><script>Some </tag>like data<script></p>"
        )
        print(store.units[0].source)
        assert len(store.units) == 1


class TestHTMLExtraction:
    h = html.htmlfile

    @staticmethod
    def strip_html(str):
        h = html.htmlfile()
        store = h.parsestring(str)
        return "\n".join(u.source for u in store.units)

    def test_strip_html(self):
        assert self.strip_html("<p><a>Something</a></p>") == "Something"
        assert (
            self.strip_html("<p>You are <a>Something</a></p>")
            == "You are <a>Something</a>"
        )
        assert (
            self.strip_html("<p><b>You</b> are <a>Something</a></p>")
            == "<b>You</b> are <a>Something</a>"
        )
        assert (
            self.strip_html(
                '<p><strong><font class="headingwhite">Projects</font></strong></p>'
            )
            == "Projects"
        )
        assert (
            self.strip_html("<p><strong>Something</strong> else.</p>")
            == "<strong>Something</strong> else."
        )
        assert (
            self.strip_html("<h1><strong>Something</strong> else.</h1>")
            == "<strong>Something</strong> else."
        )
        assert (
            self.strip_html(
                '<h1 id="moral"><strong>We believe</strong> that the internet should be public, open and accessible.</h1>'
            )
            == "<strong>We believe</strong> that the internet should be public, open and accessible."
        )
        assert (
            self.strip_html(
                '<h3><a href="http://www.firefox.com/" class="producttitle"><img src="../images/product-firefox-50.png" width="50" height="50" alt="" class="featured" style="display: block; margin-bottom: 30px;" /><strong>Firefox for Desktop</strong></a></h3>'
            )
            == "Firefox for Desktop"
        )

    def test_extraction_tag_figcaption(self):
        """Check that we can extract figcaption."""
        h = html.htmlfile()
        # Example form http://www.w3schools.com/tags/tag_figcaption.asp
        store = h.parsestring(
            """
               <figure>
                   <img src="img_pulpit.jpg" alt="The Pulpit Rock" width="304" height="228">
                   <figcaption>Fig1. - A view of the pulpit rock in Norway.</figcaption>
               </figure>"""
        )
        print(store.units[0].source)
        assert len(store.units) == 2
        assert store.units[0].source == "The Pulpit Rock"
        assert store.units[1].source == "Fig1. - A view of the pulpit rock in Norway."

    def test_extraction_tag_caption_td_th(self):
        """Check that we can extract table related translatable: th, td and caption."""
        h = html.htmlfile()
        # Example form http://www.w3schools.com/tags/tag_caption.asp
        store = h.parsestring(
            """
            <table>
                <caption>Monthly savings</caption>
                <tr>
                    <th>Month</th>
                    <th>Savings</th>
                </tr>
                <tr>
                    <td>January</td>
                    <td>$100</td>
                </tr>
            </table>"""
        )
        print(store.units[0].source)
        assert len(store.units) == 5
        assert store.units[0].source == "Monthly savings"
        assert store.units[1].source == "Month"
        assert store.units[2].source == "Savings"
        assert store.units[3].source == "January"
        assert store.units[4].source == "$100"

    def test_extraction_attr_alt(self):
        """Check that we can extract title attribute."""
        h = html.htmlfile()
        # Example from http://www.netmechanic.com/news/vol6/html_no1.htm
        store = h.parsestring(
            """
            <img src="cafeteria.jpg" height="200" width="200" alt="UAHC campers enjoy a meal in the camp cafeteria">
        """
        )
        assert len(store.units) == 1
        assert (
            store.units[0].source == "UAHC campers enjoy a meal in the camp cafeteria"
        )

    def test_extraction_attr_title(self):
        """Check that we can extract title attribute."""
        h = html.htmlfile()

        # Example form http://www.w3schools.com/tags/att_global_title.asp
        store = h.parsestring(
            """
            <p><abbr title="World Health Organization">WHO</abbr> was founded in 1948.</p>
            <p title="Free Web tutorials">W3Schools.com</p>"""
        )
        print(store.units[0].source)
        assert len(store.units) == 3
        assert (
            store.units[0].source
            == '<abbr title="World Health Organization">WHO</abbr> was founded in 1948.'
        )
        assert store.units[1].source == "Free Web tutorials"
        assert store.units[2].source == "W3Schools.com"

        # Example from http://www.netmechanic.com/news/vol6/html_no1.htm
        store = h.parsestring(
            """
            <table width="100" border="2" title="Henry Jacobs Camp summer 2003 schedule">
        """
        )
        assert len(store.units) == 1
        assert store.units[0].source == "Henry Jacobs Camp summer 2003 schedule"

        store = h.parsestring(
            """
           <div><a href="page1.html" title="HS Jacobs - a UAHC camp in Utica, MS">Henry S. Jacobs Camp</a></div>
        """
        )
        assert len(store.units) == 2
        assert store.units[0].source == "HS Jacobs - a UAHC camp in Utica, MS"
        assert store.units[1].source == "Henry S. Jacobs Camp"

        store = h.parsestring(
            """
            <form name="application" title="Henry Jacobs camper application" method="  " action="  ">
        """
        )
        assert len(store.units) == 1
        assert store.units[0].source == "Henry Jacobs camper application"

    def test_extraction_pre(self):
        """Check that we can preserve lines in the <pre> tag."""
        h = html.htmlfile()
        store = h.parsestring(
            """
<pre>
this is
a multiline
pre tag
</pre>
        """
        )
        assert len(store.units) == 1
        assert store.units[0].source == "this is\na multiline\npre tag"

    def test_extraction_pre_code(self):
        """Check that we can preserve lines in the <pre> tag."""
        h = html.htmlfile()
        store = h.parsestring(
            """
<pre><code>
this is
a multiline
pre tag
</code></pre>
        """
        )
        assert len(store.units) == 1
        assert store.units[0].source == "this is\na multiline\npre tag"

    def test_extraction_button(self):
        """Check that we can extract text from button elements."""
        h = html.htmlfile()

        # Simple button text
        store = h.parsestring(
            "<button>Zustimmen und weiter</button>"
        )  # codespell:ignore
        assert len(store.units) == 1
        assert store.units[0].source == "Zustimmen und weiter"  # codespell:ignore

        # Button with nested elements
        store = h.parsestring("<button><span>Click</span> here</button>")
        assert len(store.units) == 1
        assert store.units[0].source == "<span>Click</span> here"

        # Button with attributes
        store = h.parsestring('<button type="submit" class="btn">Submit</button>')
        assert len(store.units) == 1
        assert store.units[0].source == "Submit"

        # Multiple buttons
        store = h.parsestring(
            """
            <button>Accept</button>
            <button>Decline</button>
            """
        )
        assert len(store.units) == 2
        assert store.units[0].source == "Accept"
        assert store.units[1].source == "Decline"

        # Button within other elements
        store = h.parsestring(
            """
            <div>
                <button>Save</button>
            </div>
            """
        )
        assert len(store.units) == 1
        assert store.units[0].source == "Save"

        # Button with title attribute (should extract both)
        store = h.parsestring('<button title="Click to submit">Submit</button>')
        assert len(store.units) == 2
        assert store.units[0].source == "Click to submit"
        assert store.units[1].source == "Submit"

    def test_extraction_lang_attribute(self):
        """Check that we extract lang attribute only from html tag."""
        h = html.htmlfile()
        store = h.parsestring(
            """<!DOCTYPE html>
<html lang="en">
<head>
    <title>Test</title>
</head>
<body>
    <p lang="en">A paragraph with lang attribute</p>
    <div lang="fr">A div with lang attribute</div>
</body>
</html>"""
        )
        # Should extract "en" from html tag, but not from p or div
        sources = [unit.source for unit in store.units]
        assert "en" in sources  # from html tag
        assert "Test" in sources
        # lang attributes in p and div should not be extracted
        lang_units = [unit for unit in store.units if unit.source == "en"]
        assert len(lang_units) == 1  # Only one "en" unit from html tag
        # Check location to confirm it's from html tag
        assert "html[lang]" in lang_units[0].getlocations()[0]

    def test_data_translate_ignore_attribute(self):
        """Check that elements with data-translate-ignore are not extracted."""
        h = html.htmlfile()

        # Simple case: single ignored paragraph
        store = h.parsestring(
            "<p>Translate this</p><p data-translate-ignore>Do not translate</p><p>Translate this too</p>"
        )
        assert len(store.units) == 2
        assert store.units[0].source == "Translate this"
        assert store.units[1].source == "Translate this too"

        # Nested elements within ignored section should also be ignored
        store = h.parsestring(
            "<div>Translate this</div><div data-translate-ignore><p>Do not translate</p><span>Also ignore</span></div><div>Translate this too</div>"
        )
        assert len(store.units) == 2
        assert store.units[0].source == "Translate this"
        assert store.units[1].source == "Translate this too"

        # Attributes in ignored elements should not be extracted
        store = h.parsestring(
            '<p title="Extract this">Translate</p><p data-translate-ignore title="Do not extract">Do not translate</p>'
        )
        assert len(store.units) == 2
        assert store.units[0].source == "Extract this"
        assert store.units[1].source == "Translate"

        # Self-closing tags with data-translate-ignore should not have attributes extracted
        store = h.parsestring(
            '<img alt="Extract this" /><img alt="Do not extract" data-translate-ignore /><p>Translate</p>'
        )
        assert len(store.units) == 2
        assert store.units[0].source == "Extract this"
        assert store.units[1].source == "Translate"

    def test_translate_comment_directives(self):
        """Check that translate:off and translate:on comments work."""
        h = html.htmlfile()

        # Basic case with comments
        store = h.parsestring(
            "<p>Translate this</p><!-- translate:off --><p>Do not translate</p><!-- translate:on --><p>Translate this too</p>"
        )
        assert len(store.units) == 2
        assert store.units[0].source == "Translate this"
        assert store.units[1].source == "Translate this too"

        # Multiple elements between translate:off and translate:on
        store = h.parsestring(
            "<div>Translate</div><!-- translate:off --><p>Skip 1</p><p>Skip 2</p><div>Skip 3</div><!-- translate:on --><p>Translate again</p>"
        )
        assert len(store.units) == 2
        assert store.units[0].source == "Translate"
        assert store.units[1].source == "Translate again"

        # translate:off without translate:on should ignore rest of document
        store = h.parsestring(
            "<p>Translate this</p><!-- translate:off --><p>Do not translate 1</p><p>Do not translate 2</p>"
        )
        assert len(store.units) == 1
        assert store.units[0].source == "Translate this"
