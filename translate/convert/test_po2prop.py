#!/usr/bin/env python
# -*- coding: utf-8 -*-

from translate.convert import po2prop
from translate.convert import test_convert
from translate.misc import wStringIO
from translate.storage import po


class TestPO2Prop:

    def po2prop(self, posource):
        """helper that converts po source to .properties source without requiring files"""
        inputfile = wStringIO.StringIO(posource)
        inputpo = po.pofile(inputfile)
        convertor = po2prop.po2prop()
        outputprop = convertor.convertstore(inputpo)
        return outputprop

    def merge2prop(self, propsource, posource, personality="java", remove_untranslated=False):
        """helper that merges po translations to .properties source without requiring files"""
        inputfile = wStringIO.StringIO(posource)
        inputpo = po.pofile(inputfile)
        templatefile = wStringIO.StringIO(propsource)
        #templateprop = properties.propfile(templatefile)
        convertor = po2prop.reprop(templatefile, inputpo, personality=personality, remove_untranslated=remove_untranslated)
        outputprop = convertor.convertstore()
        print outputprop
        return outputprop

    def test_merging_simple(self):
        """check the simplest case of merging a translation"""
        posource = '''#: prop\nmsgid "value"\nmsgstr "waarde"\n'''
        proptemplate = '''prop=value\n'''
        propexpected = '''prop=waarde\n'''
        propfile = self.merge2prop(proptemplate, posource)
        print propfile
        assert propfile == propexpected

    def test_merging_untranslated(self):
        """check the simplest case of merging an untranslated unit"""
        posource = '''#: prop\nmsgid "value"\nmsgstr ""\n'''
        proptemplate = '''prop=value\n'''
        propexpected = proptemplate
        propfile = self.merge2prop(proptemplate, posource)
        print propfile
        assert propfile == propexpected

    def test_hard_newlines_preserved(self):
        """check that we preserver hard coded newlines at the start and end of sentence"""
        posource = '''#: prop\nmsgid "\\nvalue\\n\\n"\nmsgstr "\\nwaarde\\n\\n"\n'''
        proptemplate = '''prop=\\nvalue\\n\\n\n'''
        propexpected = '''prop=\\nwaarde\\n\\n\n'''
        propfile = self.merge2prop(proptemplate, posource)
        print propfile
        assert propfile == propexpected

    def test_space_preservation(self):
        """check that we preserve any spacing in properties files when merging"""
        posource = '''#: prop\nmsgid "value"\nmsgstr "waarde"\n'''
        proptemplate = '''prop  =  value\n'''
        propexpected = '''prop  =  waarde\n'''
        propfile = self.merge2prop(proptemplate, posource)
        print propfile
        assert propfile == propexpected

    def test_merging_blank_entries(self):
        """check that we can correctly merge entries that are blank in the template"""
        posource = r'''#: accesskey-accept
msgid ""
"_: accesskey-accept\n"
""
msgstr ""'''
        proptemplate = 'accesskey-accept=\n'
        propexpected = 'accesskey-accept=\n'
        propfile = self.merge2prop(proptemplate, posource)
        print propfile
        assert propfile == propexpected

    def test_merging_fuzzy(self):
        """check merging a fuzzy translation"""
        posource = '''#: prop\n#, fuzzy\nmsgid "value"\nmsgstr "waarde"\n'''
        proptemplate = '''prop=value\n'''
        propexpected = '''prop=value\n'''
        propfile = self.merge2prop(proptemplate, posource)
        print propfile
        assert propfile == propexpected

    def test_merging_propertyless_template(self):
        """check that when merging with a template with no property values that we copy the template"""
        posource = ""
        proptemplate = "# A comment\n"
        propexpected = proptemplate
        propfile = self.merge2prop(proptemplate, posource)
        print propfile
        assert propfile == propexpected

    def test_delimiters(self):
        """test that we handle different delimiters."""
        posource = '''#: prop\nmsgid "value"\nmsgstr "translated"\n'''
        proptemplate = '''prop %s value\n'''
        propexpected = '''prop %s translated\n'''
        for delim in ['=', ':', '']:
            print "testing '%s' as delimiter" % delim
            propfile = self.merge2prop(proptemplate % delim, posource)
            print propfile
            assert propfile == propexpected % delim

    def test_empty_value(self):
        """test that we handle an value in the template"""
        posource = '''#: key
msgctxt "key"
msgid ""
msgstr "translated"
'''
        proptemplate = '''key\n'''
        propexpected = '''key = translated\n'''
        propfile = self.merge2prop(proptemplate, posource)
        print propfile
        assert propfile == propexpected

    def test_personalities(self):
        """test that we output correctly for Java and Mozilla style property files.  Mozilla uses Unicode, while Java uses escaped Unicode"""
        posource = u'''#: prop\nmsgid "value"\nmsgstr "ṽḁḽṻḝ"\n'''
        proptemplate = u'''prop  =  value\n'''
        propexpectedjava = u'''prop  =  \\u1E7D\\u1E01\\u1E3D\\u1E7B\\u1E1D\n'''
        propfile = self.merge2prop(proptemplate, posource)
        assert propfile == propexpectedjava

        propexpectedmozilla = u'''prop  =  ṽḁḽṻḝ\n'''.encode('utf-8')
        propfile = self.merge2prop(proptemplate, posource, personality="mozilla")
        assert propfile == propexpectedmozilla

        proptemplate = u'''prop  =  value\n'''.encode('utf-16')
        propexpectedskype = u'''prop  =  ṽḁḽṻḝ\n'''.encode('utf-16')
        propfile = self.merge2prop(proptemplate, posource, personality="skype")
        assert propfile == propexpectedskype

        proptemplate = u'''"prop" = "value";\n'''.encode('utf-16')
        propexpectedstrings = u'''"prop" = "ṽḁḽṻḝ";\n'''.encode('utf-16')
        propfile = self.merge2prop(proptemplate, posource, personality="strings")
        assert propfile == propexpectedstrings

    def test_merging_untranslated_simple(self):
        """check merging untranslated entries in two 1) use English 2) drop key, value pair"""
        posource = '''#: prop\nmsgid "value"\nmsgstr ""\n'''
        proptemplate = '''prop = value\n'''
        propfile = self.merge2prop(proptemplate, posource)
        print propfile
        assert propfile == proptemplate  # We use the existing values
        propfile = self.merge2prop(proptemplate, posource, remove_untranslated=True)
        print propfile
        assert propfile == ''  # We drop the key

    def test_merging_untranslated_multiline(self):
        """check merging untranslated entries with multiline values"""
        posource = '''#: prop\nmsgid "value1 value2"\nmsgstr ""\n'''
        proptemplate = '''prop = value1 \
    value2
'''
        propexpected = '''prop = value1 value2\n'''
        propfile = self.merge2prop(proptemplate, posource)
        print propfile
        assert propfile == propexpected  # We use the existing values
        propfile = self.merge2prop(proptemplate, posource, remove_untranslated=True)
        print propfile
        assert propfile == ''  # We drop the key

    def test_merging_untranslated_comments(self):
        """check merging untranslated entries with comments"""
        posource = '''#: prop\nmsgid "value"\nmsgstr ""\n'''
        proptemplate = '''# A comment\nprop = value\n'''
        propexpected = '# A comment\nprop = value\n'
        propfile = self.merge2prop(proptemplate, posource)
        print propfile
        assert propfile == propexpected  # We use the existing values
        propfile = self.merge2prop(proptemplate, posource, remove_untranslated=True)
        print propfile
        # FIXME ideally we should drop the comment as well as the unit
        assert propfile == '# A comment\n'  # We drop the key

    def test_gaia_plurals(self):
        """Test back conversion of gaia plural units."""
        proptemplate = '''
message-multiedit-header={[ plural(n) ]}
message-multiedit-header[zero]=Edit
message-multiedit-header[one]={{ n }} selected
message-multiedit-header[two]={{ n }} selected
message-multiedit-header[few]={{ n }} selected
message-multiedit-header[many]={{ n }} selected
message-multiedit-header[other]={{ n }} selected
'''
        posource = r'''#: message-multiedit-header[zero]
msgctxt "message-multiedit-header[zero]"
msgid "Edit"
msgstr "Redigeer"

#: message-multiedit-header
msgctxt "message-multiedit-header"
msgid "Edit"
msgid_plural "{{ n }} selected"
msgstr[0] "xxxRedigeerxxx"
msgstr[1] "{{ n }} gekies"
msgstr[2] "{{ n }} gekies"
msgstr[3] "{{ n }} gekies"
msgstr[4] "{{ n }} gekies"
msgstr[5] "{{ n }} gekies"
'''
        propexpected = '''
message-multiedit-header={[ plural(n) ]}
message-multiedit-header[zero]=Redigeer
message-multiedit-header[one]={{ n }} gekies
message-multiedit-header[two]={{ n }} gekies
message-multiedit-header[few]={{ n }} gekies
message-multiedit-header[many]={{ n }} gekies
message-multiedit-header[other]={{ n }} gekies
'''
        propfile = self.merge2prop(proptemplate, posource, personality="gaia")
        assert propfile == propexpected

    def test_mozilla_plurals(self):
        """Test back conversion of mozilla plural units."""
        proptemplate = '''# LOCALIZATION NOTE (addonDownloading, addonDownloadCancelled, addonDownloadRestart):
# Semi-colon list of plural forms. See:
# http://developer.mozilla.org/en/docs/Localization_and_Plurals
addonDownloading=Add-on downloading;Add-ons downloading
someStringNotPlural1=We have a semicolon here; but not a plural
addonDownloadCancelled=Add-on download cancelled.;Add-on downloads cancelled.
addonDownloadRestart=Restart Download;Restart Downloads
someStringNotPlural2=We have a semicolon here too; but still not a plural
# LOCALIZATION NOTE (stringWithPlural):
# Semi-colon list of plural forms. See:
# http://developer.mozilla.org/en/docs/Localization_and_Plurals
# but we are soo smart and using a short key above
foo.stringWithPlural=Singular string;Plural string
# LOCALIZATION NOTE (anotherStringWithPlural):
# Semi-colon list of plural forms. See:
# http://developer.mozilla.org/en/docs/Localization_and_Plurals
# but we are soo smart so placing the comment above unrelated string
someStringNotPlural3=We are not a plural
anotherStringWithPlural=Singular;Plural
'''
        posource = r'''
#: addonDownloading
msgid "Add-on downloading"
msgid_plural "Add-ons downloading"
msgstr[0] "Singular 1"
msgstr[1] "Plural 1"

#: someStringNotPlural1
msgid "We have a semicolon here; but not a plural"
msgstr "Non plural 1"

#: addonDownloadCancelled
msgid "Add-on download cancelled."
msgid_plural "Add-on downloads cancelled."
msgstr[0] "Singular 2"
msgstr[1] "Plural 2"

#: addonDownloadRestart
msgid "Restart Download"
msgid_plural "Restart Downloads"
msgstr[0] "Singular 3"
msgstr[1] "Plural 3"

#: someStringNotPlural2
msgid "We have a semicolon here too; but still not a plural"
msgstr "Non plural 2"

#: foo.stringWithPlural
msgid "Singular string"
msgid_plural "Plural string"
msgstr[0] "Singular 4"
msgstr[1] "Plural 4"

#: someStringNotPlural3
msgid "We are not a plural"
msgstr "Non plural 3"

#: anotherStringWithPlural
msgid "Singular"
msgid_plural "Plural"
msgstr[0] "Singular 5"
msgstr[1] "Plural 5"
'''
        propexpected = '''# LOCALIZATION NOTE (addonDownloading, addonDownloadCancelled, addonDownloadRestart):
# Semi-colon list of plural forms. See:
# http://developer.mozilla.org/en/docs/Localization_and_Plurals
addonDownloading=Singular 1;Plural 1
someStringNotPlural1=Non plural 1
addonDownloadCancelled=Singular 2;Plural 2
addonDownloadRestart=Singular 3;Plural 3
someStringNotPlural2=Non plural 2
# LOCALIZATION NOTE (stringWithPlural):
# Semi-colon list of plural forms. See:
# http://developer.mozilla.org/en/docs/Localization_and_Plurals
# but we are soo smart and using a short key above
foo.stringWithPlural=Singular 4;Plural 4
# LOCALIZATION NOTE (anotherStringWithPlural):
# Semi-colon list of plural forms. See:
# http://developer.mozilla.org/en/docs/Localization_and_Plurals
# but we are soo smart so placing the comment above unrelated string
someStringNotPlural3=Non plural 3
anotherStringWithPlural=Singular 5;Plural 5
'''
        propfile = self.merge2prop(proptemplate, posource, personality="mozilla")
        assert propfile == propexpected


class TestPO2PropCommand(test_convert.TestConvertCommand, TestPO2Prop):
    """Tests running actual po2prop commands on files"""
    convertmodule = po2prop
    defaultoptions = {"progress": "none"}

    def test_help(self):
        """tests getting help"""
        options = test_convert.TestConvertCommand.test_help(self)
        options = self.help_check(options, "-t TEMPLATE, --template=TEMPLATE")
        options = self.help_check(options, "--fuzzy")
        options = self.help_check(options, "--personality=TYPE")
        options = self.help_check(options, "--encoding=ENCODING")
        options = self.help_check(options, "--removeuntranslated")
        options = self.help_check(options, "--nofuzzy", last=True)
