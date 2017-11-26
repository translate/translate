# -*- coding: utf-8 -*-

import pytest

from translate.convert import mozlang2po, test_convert
from translate.misc import wStringIO
from translate.storage import mozilla_lang as lang


class TestLang2PO(object):

    ConverterClass = mozlang2po.lang2po

    def _convert_to_store(self, input_string, template_string=None,
                          blank_msgstr=False, duplicate_style="msgctxt",
                          encoding="utf-8", success_expected=True):
        """Helper that converts to target format store without using files."""
        input_file = wStringIO.StringIO(input_string)
        output_file = wStringIO.StringIO()
        template_file = None
        if template_string:
            template_file = wStringIO.StringIO(template_string)
        expected_result = 1 if success_expected else 0
        converter = self.ConverterClass(input_file, output_file, template_file,
                                        blank_msgstr, duplicate_style,
                                        encoding)
        assert converter.run() == expected_result
        return converter.target_store

    def _convert_to_string(self, input_string, template_string=None,
                           blank_msgstr=False, duplicate_style="msgctxt",
                           encoding="utf-8", success_expected=True):
        """Helper that converts to target format string without using files."""
        input_file = wStringIO.StringIO(input_string)
        output_file = wStringIO.StringIO()
        template_file = None
        if template_string:
            template_file = wStringIO.StringIO(template_string)
        expected_result = 1 if success_expected else 0
        result = mozlang2po.run_converter(input_file, output_file,
                                          template_file, blank_msgstr,
                                          duplicate_style, encoding)
        assert result == expected_result
        return output_file.getvalue().decode('utf-8')

    def _single_element(self, po_store):
        """Helper that returns first non-header unit.

        It also checks that the store has a single non-header unit.
        """
        assert len(po_store.units) == 2
        assert po_store.units[0].isheader()
        return po_store.units[1]

    def test_convert_empty(self):
        """Check converting empty file returns no output."""
        assert self._convert_to_string('', success_expected=False) == ''

    def test_simple_string(self):
        """Checks a simple lang string converts correctly."""
        input_string = """;One
Een
"""
        expected_output = """
msgid "One"
msgstr "Een"
"""
        assert expected_output in self._convert_to_string(input_string)

    def test_merge(self):
        """Check converter doesn't merge."""
        input_file = wStringIO.StringIO()
        output_file = wStringIO.StringIO()
        template_file = wStringIO.StringIO()
        with pytest.raises(NotImplementedError):
            self.ConverterClass(input_file, output_file, template_file).run()

    def test_simpleentry(self):
        """checks that a simple lang entry converts properly to a po entry"""
        source = """;One
Een
"""
        pofile = self._convert_to_store(source)
        pounit = self._single_element(pofile)
        assert pounit.source == "One"
        assert pounit.target == "Een"

    def test_simplecomment(self):
        """Handle simple comments"""
        source = """# Comment
;One
Een
"""
        pofile = self._convert_to_store(source)
        pounit = self._single_element(pofile)
        assert pounit.source == "One"
        assert pounit.target == "Een"
        assert pounit.getnotes() == "Comment"

    def test_meta_tags(self):
        """Meta tags are not extracted"""
        source = """## tag
# Comment
;One
Een
"""
        pofile = self._convert_to_store(source)
        pounit = self._single_element(pofile)
        assert "tag" not in pounit.getnotes()


class TestLang2POCommand(test_convert.TestConvertCommand, TestLang2PO):
    """Tests running actual lang2po commands on files"""
    convertmodule = mozlang2po
    defaultoptions = {"progress": "none"}

    def test_help(self):
        """tests getting help"""
        options = test_convert.TestConvertCommand.test_help(self)
        options = self.help_check(options, "-P, --pot")
        options = self.help_check(options, "--encoding=ENCODING")
        options = self.help_check(options, "--duplicates=DUPLICATESTYLE",
                                  last=True)
