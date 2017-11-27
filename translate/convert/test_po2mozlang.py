# -*- coding: utf-8 -*-

from translate.convert import po2mozlang, test_convert
from translate.misc import wStringIO
from translate.storage import po


class TestPO2Lang(object):

    def po2lang(self, input_string):
        """helper that converts po source to .lang source without requiring files"""
        inputfile = wStringIO.StringIO(input_string)
        inputpo = po.pofile(inputfile)
        convertor = po2mozlang.po2lang(mark_active=False)
        outputlang = convertor.convertstore(inputpo)
        return bytes(outputlang).decode('utf-8')

    def test_simple(self):
        """check the simplest case of merging a translation"""
        input_string = '''#: prop\nmsgid "Source"\nmsgstr "Target"\n'''
        expected_output = ''';Source\nTarget\n\n\n'''
        assert expected_output == self.po2lang(input_string)

    def test_comment(self):
        """Simple # comments"""
        input_string = '''#. Comment\n#: prop\nmsgid "Source"\nmsgstr "Target"\n'''
        expected_output = '''# Comment\n;Source\nTarget\n\n\n'''
        assert expected_output == self.po2lang(input_string)

    def test_fuzzy(self):
        """What happens with a fuzzy string"""
        input_string = '''#. Comment\n#: prop\n#, fuzzy\nmsgid "Source"\nmsgstr "Target"\n'''
        expected_output = '''# Comment\n;Source\nSource\n\n\n'''
        assert expected_output == self.po2lang(input_string)

    def test_ok_marker(self):
        """The {ok} marker"""
        input_string = '''#: prop\nmsgid "Same"\nmsgstr "Same"\n'''
        expected_output = ''';Same\nSame {ok}\n\n\n'''
        assert expected_output == self.po2lang(input_string)


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
