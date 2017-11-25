# -*- coding: utf-8 -*-

from translate.convert import mozlang2po, test_convert
from translate.misc import wStringIO
from translate.storage import mozilla_lang as lang


class TestLang2PO(object):

    def _convert_to_store(self, source):
        """helper that converts .lang source to po source without requiring files"""
        inputfile = wStringIO.StringIO(source)
        convertor = mozlang2po.lang2po(inputfile)
        outputpo = convertor.convert_store()
        return outputpo

    def _convert_to_string(self, input_string, template_string=None,
                           success_expected=True):
        """Helper that converts to target format string without using files."""
        input_file = wStringIO.StringIO(input_string)
        output_file = wStringIO.StringIO()
        template_file = None
        if template_string:
            template_file = wStringIO.StringIO(template_string)
        expected_result = 1 if success_expected else 0
        result = mozlang2po.run_converter(input_file, output_file,
                                          template_file)
        assert result == expected_result
        return output_file.getvalue().decode('utf-8')

    def _single_element(self, pofile):
        """checks that the pofile contains a single non-header element, and returns it"""
        assert len(pofile.units) == 2
        assert pofile.units[0].isheader()
        return pofile.units[1]

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
