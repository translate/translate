#!/usr/bin/env python
# -*- coding: utf-8 -*-

from translate.convert import po2ini
from translate.convert import test_convert
from translate.misc import wStringIO
from translate.storage import po

class TestPO2Prop:
    def po2ini(self, posource):
        """helper that converts po source to .properties source without requiring files"""
        inputfile = wStringIO.StringIO(posource)
        inputpo = po.pofile(inputfile)
        convertor = po2ini.reini()
        outputprop = convertor.convertstore(inputpo)
        return outputprop

    def merge2ini(self, propsource, posource, dialect="default"):
        """helper that merges po translations to .properties source without requiring files"""
        inputfile = wStringIO.StringIO(posource)
        inputpo = po.pofile(inputfile)
        templatefile = wStringIO.StringIO(propsource)
        #templateprop = properties.propfile(templatefile)
        convertor = po2ini.reini(templatefile, inputpo, dialect=dialect)
        outputprop = convertor.convertstore()
        print outputprop
        return outputprop

    def test_merging_simple(self):
        """check the simplest case of merging a translation"""
        posource = '''#: [section]prop\nmsgid "value"\nmsgstr "waarde"\n'''
        proptemplate = '''[section]\nprop=value\n'''
        propexpected = '''[section]\nprop=waarde\n'''
        propfile = self.merge2ini(proptemplate, posource)
        print propfile
        assert propfile == propexpected

    def test_space_preservation(self):
        """check that we preserve any spacing in properties files when merging"""
        posource = '''#: [section]prop\nmsgid "value"\nmsgstr "waarde"\n'''
        proptemplate = '''[section]\nprop  =  value\n'''
        propexpected = '''[section]\nprop  =  waarde\n'''
        propfile = self.merge2ini(proptemplate, posource)
        print propfile
        assert propfile == propexpected

    def test_merging_blank_entries(self):
        """check that we can correctly merge entries that are blank in the template"""
        posource = r'''#: [section]accesskey-accept
msgid ""
"_: accesskey-accept\n"
""
msgstr ""'''
        proptemplate = '[section]\naccesskey-accept=\n'
        propexpected = '[section]\naccesskey-accept=\n'
        propfile = self.merge2ini(proptemplate, posource)
        print propfile
        assert propfile == propexpected

    def test_merging_fuzzy(self):
        """check merging a fuzzy translation"""
        posource = '''#: [section]prop\n#, fuzzy\nmsgid "value"\nmsgstr "waarde"\n'''
        proptemplate = '''[section]\nprop=value\n'''
        propexpected = '''[section]\nprop=value\n'''
        propfile = self.merge2ini(proptemplate, posource)
        print propfile
        assert propfile == propexpected

    def test_merging_propertyless_template(self):
        """check that when merging with a template with no property values that we copy the template"""
        posource = ""
        proptemplate = "# A comment\n"
        propexpected = proptemplate
        propfile = self.merge2ini(proptemplate, posource)
        print propfile
        assert propfile == propexpected

    def test_empty_value(self):
        """test that we handle an value in translation that is missing in the template"""
        posource = '''#: [section]key
msgctxt "key"
msgid ""
msgstr "translated"
'''
        proptemplate = '''[section]\nkey =\n'''
        propexpected = '''[section]\nkey =translated\n'''
        propfile = self.merge2ini(proptemplate, posource)
        print propfile
        assert propfile == propexpected

    def xtest_dialects_inno(self):
        # FIXME we have some encoding issues with this test
        """test that we output correctly for Inno files."""
        posource = ur'''#: [section]prop
msgid "value\tvalue2\n"
msgstr "ṽḁḽṻḝ\tṽḁḽṻḝ2\n"
'''
        proptemplate = u'''[section]\nprop  =  value%tvalue%n\n'''
        propexpected = u'''[section]\nprop  =  ṽḁḽṻḝ%tṽḁḽṻḝ2%n'''
        propfile = self.merge2ini(proptemplate, posource, "inno")
        print propfile
        assert propfile == propexpected

class TestPO2PropCommand(test_convert.TestConvertCommand, TestPO2Prop):
    """Tests running actual po2ini commands on files"""
    convertmodule = po2ini
    defaultoptions = {"progress": "none"}

    def test_help(self):
        """tests getting help"""
        options = test_convert.TestConvertCommand.test_help(self)
        options = self.help_check(options, "-t TEMPLATE, --template=TEMPLATE")
        options = self.help_check(options, "--fuzzy")
        options = self.help_check(options, "--nofuzzy", last=True)

