# -*- coding: utf-8 -*-

from translate.convert import po2mozlang, test_convert
from translate.misc import wStringIO
from translate.storage import po


class TestPO2Lang(object):

    def po2lang(self, posource):
        """helper that converts po source to .lang source without requiring files"""
        inputfile = wStringIO.StringIO(posource)
        inputpo = po.pofile(inputfile)
        convertor = po2mozlang.po2lang(mark_active=False)
        outputlang = convertor.convertstore(inputpo)
        return bytes(outputlang).decode('utf-8')

    def test_simple(self):
        """check the simplest case of merging a translation"""
        posource = '''#: prop\nmsgid "Source"\nmsgstr "Target"\n'''
        prop_expected = ''';Source\nTarget\n\n\n'''
        prop_result = self.po2lang(posource)
        print(prop_result)
        assert prop_result == prop_expected

    def test_comment(self):
        """Simple # comments"""
        posource = '''#. Comment\n#: prop\nmsgid "Source"\nmsgstr "Target"\n'''
        prop_expected = '''# Comment\n;Source\nTarget\n\n\n'''
        prop_result = self.po2lang(posource)
        print(prop_result)
        assert prop_result == prop_expected

    def test_fuzzy(self):
        """What happens with a fuzzy string"""
        posource = '''#. Comment\n#: prop\n#, fuzzy\nmsgid "Source"\nmsgstr "Target"\n'''
        prop_expected = '''# Comment\n;Source\nSource\n\n\n'''
        prop_result = self.po2lang(posource)
        print(prop_result)
        assert prop_result == prop_expected

    def test_ok_marker(self):
        """The {ok} marker"""
        posource = '''#: prop\nmsgid "Same"\nmsgstr "Same"\n'''
        prop_expected = ''';Same\nSame {ok}\n\n\n'''
        prop_result = self.po2lang(posource)
        print(prop_result)
        assert prop_result == prop_expected


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
