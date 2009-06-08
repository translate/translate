# -*- coding: utf-8 -*-

from translate.tools import podebug
from translate.storage import base, po, xliff

PO_DOC = """
msgid "This is a test, hooray."
msgstr ""
"""

XLIFF_DOC = """<?xml version='1.0' encoding='utf-8'?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:1.1" version="1.1">
  <file original="NoName" source-language="en" datatype="plaintext">
    <body>
      <trans-unit id="office:document-content[0]/office:body[0]/office:text[0]/text:p[0]">
        <source>This <g id="0">is a</g> test <x id="1" xid="office:document-content[0]/office:body[0]/office:text[0]/text:p[0]/text:note[0]"/>, hooray.</source>
      </trans-unit>
    </body>
  </file>
</xliff>
"""

class TestPODebug:
    debug = podebug.podebug()

    def setup_method(self, method):
        self.postore = po.pofile(PO_DOC)
        self.xliffstore = xliff.xlifffile(XLIFF_DOC)

    def test_ignore_gtk(self):
        """Test operation of GTK message ignoring"""
        unit = base.TranslationUnit("default:LTR")
        assert self.debug.ignore_gtk(unit) == True

    def test_rewrite_blank(self):
        """Test the blank rewrite function"""
        assert str(self.debug.rewrite_blank(u"Test")) == u""

    def test_rewrite_en(self):
        """Test the en rewrite function"""
        assert str(self.debug.rewrite_en(u"Test")) == u"Test"

    def test_rewrite_xxx(self):
        """Test the xxx rewrite function"""
        assert str(self.debug.rewrite_xxx(u"Test")) == u"xxxTestxxx"
        assert str(self.debug.rewrite_xxx(u"Newline\n")) == u"xxxNewlinexxx\n"

    def test_rewrite_unicode(self):
        """Test the unicode rewrite function"""
        assert unicode(self.debug.rewrite_unicode(u"Test")) == u"Ŧḗşŧ"

    def test_rewrite_flipped(self):
        """Test the unicode rewrite function"""
        assert unicode(self.debug.rewrite_flipped(u"Test")) == u"\u202e⊥ǝsʇ"
        #alternative with reversed string and no RTL override:
        #assert unicode(self.debug.rewrite_flipped("Test")) == u"ʇsǝ⊥"

    def test_rewrite_chef(self):
        """Test the chef rewrite function

        This is not realy critical to test but a simple tests ensures
        that it stays working.
        """
        assert str(self.debug.rewrite_chef(u"Mock Swedish test you muppet")) == u"Mock Swedish test yooo mooppet"

    def test_xliff_rewrite(self):
        debug = podebug.podebug(rewritestyle='xxx')
        xliff_out = debug.convertstore(self.xliffstore)

        in_unit = self.xliffstore.units[0]
        out_unit = xliff_out.units[0]

        assert in_unit.source == out_unit.source
        print out_unit.target
        print str(xliff_out)
        assert out_unit.target == u'xxx%sxxx' % (in_unit.source)
