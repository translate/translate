#!/usr/bin/env python

from translate.convert import po2prop
from translate.convert import prop2po
from translate.convert import test_convert
from translate.misc import wStringIO
from translate.storage import po
from translate.storage import properties
from py import test

class TestPO2Prop:
    def po2prop(self, posource):
        """helper that converts po source to .properties source without requiring files"""
        inputfile = wStringIO.StringIO(posource)
        inputpo = po.pofile(inputfile)
        convertor = po2prop.po2prop()
        outputprop = convertor.convertfile(inputpo)
        return outputprop

    def merge2prop(self, propsource, posource):
        """helper that merges po translations to .properties source without requiring files"""
        inputfile = wStringIO.StringIO(posource)
        inputpo = po.pofile(inputfile)
        templatefile = wStringIO.StringIO(propsource)
        #templateprop = properties.propfile(templatefile)
        convertor = po2prop.reprop(templatefile)
        outputprop = convertor.convertfile(inputpo)
        print outputprop
        return outputprop

    def test_hard_newlines_preserved(self):
        """check that we preserver hard coded newlines at the start and end of sentence"""
        posource = '''#: prop\nmsgid "\\nvalue\\n\\n"\nmsgstr "\\nwaarde\\n\\n"\n'''
        proptemplate = '''prop=\\nvalue\\n\\n\n'''
        propexpected = '''prop=\\nwaarde\\n\\n\n'''
        propfile = self.merge2prop(proptemplate, posource)
        print propfile
        assert propfile == [propexpected]

    def test_space_preservation(self):
        """check that we preserve any spacing in properties files when merging"""
        posource = '''#: prop\nmsgid "value"\nmsgstr "waarde"\n'''
        proptemplate = '''prop  =  value\n'''
        propexpected = '''prop  =  waarde\n'''
        propfile = self.merge2prop(proptemplate, posource)
        print propfile
        assert propfile == [propexpected]

    def test_merging_blank_entries(self):
        """check that we can correctly merge entries that are blank in the template"""
        posource = '''#: accesskey-accept
msgid ""
"_: accesskey-accept\n"
""
msgstr ""'''
        proptemplate = 'accesskey-accept=\n'
        propexpected = 'accesskey-accept=\n'
        propfile = self.merge2prop(proptemplate, posource)
        print propfile
        assert propfile == [propexpected]

class TestPO2PropCommand(test_convert.TestConvertCommand, TestPO2Prop):
    """Tests running actual po2prop commands on files"""
    convertmodule = po2prop
    defaultoptions = {"progress": "none"}

    def test_help(self):
        """tests getting help"""
        options = test_convert.TestConvertCommand.test_help(self)
        options = self.help_check(options, "-tTEMPLATE, --template=TEMPLATE")
        options = self.help_check(options, "--fuzzy")
        options = self.help_check(options, "--nofuzzy", last=True)

