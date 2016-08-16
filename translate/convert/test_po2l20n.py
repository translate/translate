# -*- coding: utf-8 -*-

from translate.convert import po2l20n, test_convert
from translate.misc import wStringIO


class TestPO2L20n(object):

    def po2l20n(self, po_source):
        """helper that converts po source to .ftl (l20n) source without requiring files"""
        inputfile = wStringIO.StringIO(po_source)
        convertor = po2l20n.po2l20n(inputfile, None, None)
        output_l20n = convertor.convert_store()
        return u"%s" % output_l20n

    def merge2l20n(self, l20n_source, po_source):
        """helper that merges po translations to .ftl (l20n) source with templates"""
        inputfile = wStringIO.StringIO(po_source)
        templatefile = wStringIO.StringIO(l20n_source)
        convertor = po2l20n.po2l20n(inputfile, None, templatefile)
        outputfile = wStringIO.StringIO()
        convertor.convert_store().serialize(outputfile)
        output_l20n = outputfile.getvalue()
        print(output_l20n)
        return output_l20n.decode('utf8')

    def test_merging_simple(self):
        """check the simplest case of merging a translation"""
        po_source = '''#: l20n\nmsgid "value"\nmsgstr "waarde"\n'''
        l20n_template = '''l20n = value\n'''
        l20n_expected = '''l20n = waarde\n'''
        l20n_file = self.merge2l20n(l20n_template, po_source)
        print(l20n_file)
        assert l20n_file == l20n_expected

    def test_merging_untranslated(self):
        """check the simplest case of merging an untranslated unit"""
        po_source = '''#: l20n\nmsgid "value"\nmsgstr ""\n'''
        l20n_template = '''l20n = value\n'''
        l20n_expected = l20n_template
        l20n_file = self.merge2l20n(l20n_template, po_source)
        print(l20n_file)
        assert l20n_file == l20n_expected


class TestPO2L20nCommand(test_convert.TestConvertCommand, TestPO2L20n):
    """Tests running actual po2prop commands on files"""
    convertmodule = po2l20n
    defaultoptions = {"progress": "none"}

    def test_help(self):
        """tests getting help"""
        options = test_convert.TestConvertCommand.test_help(self)
        options = self.help_check(options, "-t TEMPLATE, --template=TEMPLATE")
        options = self.help_check(options, "--fuzzy")
        options = self.help_check(options, "--threshold=PERCENT")
        options = self.help_check(options, "--nofuzzy", last=True)
