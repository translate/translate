import pytest

from translate.convert import test_convert, txt2po
from translate.misc import wStringIO
from translate.storage import txt


class BaseTxt2POTester(object):

    ConverterClass = txt2po.txt2po
    Flavour = None

    def _convert_to_store(self, input_string, template_string=None,
                          duplicate_style="msgctxt", encoding="utf-8",
                          success_expected=True):
        """Helper that converts to target format store without using files."""
        input_file = wStringIO.StringIO(input_string)
        output_file = wStringIO.StringIO()
        template_file = None
        if template_string:
            template_file = wStringIO.StringIO(template_string)
        expected_result = 1 if success_expected else 0
        converter = self.ConverterClass(input_file, output_file, template_file,
                                        duplicate_style, encoding,
                                        self.Flavour)
        assert converter.run() == expected_result
        return converter.target_store

    def _count_elements(self, po_store):
        """Helper that counts the number of non-header units."""
        assert po_store.units[0].isheader()
        return len(po_store.units) - 1


class TestTxt2PO(BaseTxt2POTester):

    def test_convert_empty(self):
        """Check converting empty file returns no output."""
        target_store = self._convert_to_store('', success_expected=False)
        assert self._count_elements(target_store) == 0

    def test_keep_duplicates(self):
        """Check converting keeps duplicates."""
        input_source = """
Simple

Simple
"""
        po_file = self._convert_to_store(input_source)
        assert self._count_elements(po_file) == 2
        assert po_file.units[1].source == "Simple"
        assert po_file.units[1].target == ""
        assert po_file.units[2].source == "Simple"
        assert po_file.units[2].target == ""

    def test_drop_duplicates(self):
        """Check converting drops duplicates."""
        input_source = """
Simple

Simple
"""
        input_file = wStringIO.StringIO(input_source)
        output_file = wStringIO.StringIO()
        convertor = self.ConverterClass(input_file, output_file,
                                        duplicate_style="merge",
                                        flavour=self.Flavour)
        convertor.run()
        po_file = convertor.target_store
        assert self._count_elements(po_file) == 1
        assert po_file.units[1].source == "Simple"
        assert po_file.units[1].target == ""

    def test_simple(self):
        """test the most basic txt conversion"""
        txtsource = "A simple string"
        poexpected = '''#: :1
msgid "A simple string"
msgstr ""
'''
        poresult = self._convert_to_store(txtsource)
        assert str(poresult.units[1]) == poexpected
        assert "extracted from " in str(poresult.header())

    def test_multiple_units(self):
        """test that we can handle txt with multiple units"""
        txtsource = """First unit
Still part of first unit

Second unit is a heading
------------------------

Third unit with blank after but no more units.

"""
        poresult = self._convert_to_store(txtsource)
        assert poresult.units[0].isheader()
        assert len(poresult.units) == 4

    def test_carriage_return(self):
        """Remove carriage returns from files in dos format."""
        txtsource = '''The rapid expansion of telecommunications infrastructure in recent years has\r
helped to bridge the digital divide to a limited extent.\r
'''

        txtexpected = '''The rapid expansion of telecommunications infrastructure in recent years has
helped to bridge the digital divide to a limited extent.'''

        poresult = self._convert_to_store(txtsource)
        pounit = poresult.units[1]
        assert str(pounit.source) == txtexpected

    def test_merge(self):
        """Check converter doesn't merge."""
        input_file = wStringIO.StringIO()
        output_file = wStringIO.StringIO()
        template_file = wStringIO.StringIO()
        with pytest.raises(txt2po.ConverterCantMergeError):
            self.ConverterClass(input_file, output_file, template_file).run()


class TestDoku2po(BaseTxt2POTester):

    Flavour = "dokuwiki"

    def test_convert_empty(self):
        """Check converting empty file returns no output."""
        input_file = wStringIO.StringIO('')
        output_file = wStringIO.StringIO()
        template_file = None
        converter = self.ConverterClass(input_file, output_file)
        assert converter.run() == 0
        assert converter.target_store.isempty()
        assert output_file.getvalue().decode('utf-8') == ''

    def test_duplicates(self):
        """Check converting drops duplicates."""
        input_source = '''
Simple

Simple
'''
        # First test with default duplicate style (msgctxt).
        po_file = self._convert_to_store(input_source)
        assert self._count_elements(po_file) == 2
        assert po_file.units[1].source == "Simple"
        assert po_file.units[1].target == ""
        assert po_file.units[2].source == "Simple"
        assert po_file.units[2].target == ""

        # Now test with merge duplicate style. This requires custom code to
        # pass the duplicate style to the converter.
        input_file = wStringIO.StringIO(input_source)
        output_file = wStringIO.StringIO()
        convertor = self.ConverterClass(input_file, output_file,
                                        duplicate_style="merge",
                                        flavour=self.Flavour)
        convertor.run()
        po_file = convertor.target_store
        assert self._count_elements(po_file) == 1
        assert po_file.units[1].source == "Simple"
        assert po_file.units[1].target == ""

    def test_basic(self):
        """Tests that we can convert some basic things."""
        dokusource = """=====Heading=====

This is a wiki page.
"""
        poresult = self._convert_to_store(dokusource)
        assert poresult.units[0].isheader()
        assert len(poresult.units) == 3
        assert poresult.units[1].source == "Heading"
        assert poresult.units[2].source == "This is a wiki page."

    def test_bullets(self):
        """Tests that we can convert some basic things."""
        dokusource = """  * This is a fact.
  * This is a fact.
"""
        poresult = self._convert_to_store(dokusource)
        assert poresult.units[0].isheader()
        assert len(poresult.units) == 3
        assert poresult.units[1].source == "This is a fact."
        assert poresult.units[1].getlocations() == [':1']
        assert poresult.units[2].source == "This is a fact."
        assert poresult.units[2].getlocations() == [':2']

    def test_numbers(self):
        """Tests that we can convert some basic things."""
        dokusource = """  - This is an item.
  - This is an item.
"""
        poresult = self._convert_to_store(dokusource)
        assert poresult.units[0].isheader()
        assert len(poresult.units) == 3
        assert poresult.units[1].source == "This is an item."
        assert poresult.units[1].getlocations() == [':1']
        assert poresult.units[2].source == "This is an item."
        assert poresult.units[2].getlocations() == [':2']

    def test_spacing(self):
        """Tests that we can convert some basic things."""
        dokusource = """ =====         Heading  =====
  * This is an item.
    * This is a subitem.
        * This is a tabbed item.
"""
        poresult = self._convert_to_store(dokusource)
        assert poresult.units[0].isheader()
        assert len(poresult.units) == 5
        assert poresult.units[1].source == "Heading"
        assert poresult.units[2].source == "This is an item."
        assert poresult.units[3].source == "This is a subitem."
        assert poresult.units[4].source == "This is a tabbed item."


class TestTxt2POCommand(test_convert.TestConvertCommand, TestTxt2PO):
    """Tests running actual txt2po commands on files"""
    convertmodule = txt2po
    defaultoptions = {"progress": "none"}

    def test_help(self):
        """tests getting help"""
        options = test_convert.TestConvertCommand.test_help(self)
        options = self.help_check(options, "-P, --pot")
        options = self.help_check(options, "--duplicates")
        options = self.help_check(options, "--encoding")
        options = self.help_check(options, "--flavour", last=True)
