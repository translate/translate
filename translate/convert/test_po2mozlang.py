# -*- coding: utf-8 -*-

from translate.convert import po2mozlang, test_convert
from translate.misc import wStringIO
from translate.storage import po


class TestPO2Lang(object):

    def _convert(self, input_string, template_string=None, include_fuzzy=False,
                 output_threshold=None, remove_untranslated=None,
                 mark_active=True, success_expected=True):
        """Helper that converts to target format without using files."""
        input_file = wStringIO.StringIO(input_string)
        output_file = wStringIO.StringIO()
        template_file = None
        if template_string:
            template_file = wStringIO.StringIO(template_string)
        expected_result = 1 if success_expected else 0
        result = po2mozlang.convertlang(input_file, output_file, template_file,
                                        include_fuzzy, mark_active,
                                        output_threshold, remove_untranslated)
        assert result == expected_result
        return None, output_file

    def _convert_to_string(self, *args, **kwargs):
        """Helper that converts to target format string without using files."""
        return self._convert(*args, **kwargs)[1].getvalue().decode('utf-8')

    def test_convert_empty(self):
        """Check converting empty file returns no output."""
        assert self._convert_to_string('', success_expected=False) == ''

    def test_simple(self):
        """check the simplest case of merging a translation"""
        input_string = """#: prop
msgid "Source"
msgstr "Target"
"""
        expected_output = """;Source
Target


"""
        assert expected_output == self._convert_to_string(input_string,
                                                          mark_active=False)

    def test_comment(self):
        """Simple # comments"""
        input_string = """#. Comment
#: prop
msgid "Source"
msgstr "Target"
"""
        expected_output = """# Comment
;Source
Target


"""
        assert expected_output == self._convert_to_string(input_string,
                                                          mark_active=False)

    def test_fuzzy(self):
        """What happens with a fuzzy string"""
        input_string = """#. Comment
#: prop
#, fuzzy
msgid "Source"
msgstr "Target"
"""
        expected_output = """# Comment
;Source
Source


"""
        assert expected_output == self._convert_to_string(input_string,
                                                          mark_active=False)

    def test_ok_marker(self):
        """The {ok} marker"""
        input_string = """#: prop
msgid "Same"
msgstr "Same"
"""
        expected_output = """;Same
Same {ok}


"""
        assert expected_output == self._convert_to_string(input_string,
                                                          mark_active=False)


class TestPO2LangCommand(test_convert.TestConvertCommand, TestPO2Lang):
    """Tests running actual po2prop commands on files"""
    convertmodule = po2mozlang
    defaultoptions = {"progress": "none"}

    def test_help(self):
        """tests getting help"""
        options = test_convert.TestConvertCommand.test_help(self)
        options = self.help_check(options, "-t TEMPLATE, --template=TEMPLATE")
        options = self.help_check(options, "--threshold=PERCENT")
        options = self.help_check(options, "--fuzzy")
        options = self.help_check(options, "--mark-active")
        options = self.help_check(options, "--nofuzzy", last=True)
