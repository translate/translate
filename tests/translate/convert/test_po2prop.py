from io import BytesIO

from translate.convert import po2prop, test_convert
from translate.storage import po


class TestPO2Prop:
    @staticmethod
    def po2prop(posource):
        """helper that converts po source to .properties source without requiring files"""
        inputfile = BytesIO(posource.encode())
        inputpo = po.pofile(inputfile)
        convertor = po2prop.po2prop()
        outputprop = convertor.convertstore(inputpo)
        return outputprop

    @staticmethod
    def merge2prop(
        propsource,
        posource,
        personality="java",
        remove_untranslated=False,
        encoding="utf-8",
    ):
        """helper that merges po translations to .properties source without requiring files"""
        inputfile = BytesIO(posource.encode())
        inputpo = po.pofile(inputfile)
        templatefile = BytesIO(
            propsource.encode() if isinstance(propsource, str) else propsource
        )
        # templateprop = properties.propfile(templatefile)
        convertor = po2prop.reprop(
            templatefile,
            inputpo,
            personality=personality,
            remove_untranslated=remove_untranslated,
        )
        outputprop = convertor.convertstore()
        print(outputprop)
        return outputprop.decode(encoding)

    def test_merging_simple(self):
        """check the simplest case of merging a translation"""
        posource = """#: prop\nmsgid "value"\nmsgstr "waarde"\n"""
        proptemplate = """prop=value\n"""
        propexpected = """prop=waarde\n"""
        propfile = self.merge2prop(proptemplate, posource)
        print(propfile)
        assert propfile == propexpected

    def test_merging_untranslated(self):
        """check the simplest case of merging an untranslated unit"""
        posource = """#: prop\nmsgid "value"\nmsgstr ""\n"""
        proptemplate = """prop=value\n"""
        propexpected = proptemplate
        propfile = self.merge2prop(proptemplate, posource)
        print(propfile)
        assert propfile == propexpected

    def test_hard_newlines_preserved(self):
        """check that we preserver hard coded newlines at the start and end of sentence"""
        posource = """#: prop\nmsgid "\\nvalue\\n\\n"\nmsgstr "\\nwaarde\\n\\n"\n"""
        proptemplate = """prop=\\nvalue\\n\\n\n"""
        propexpected = """prop=\\nwaarde\\n\\n\n"""
        propfile = self.merge2prop(proptemplate, posource)
        print(propfile)
        assert propfile == propexpected

    def test_space_preservation(self):
        """check that we preserve any spacing in properties files when merging"""
        posource = """#: prop\nmsgid "value"\nmsgstr "waarde"\n"""
        proptemplate = """prop  =  value\n"""
        propexpected = """prop  =  waarde\n"""
        propfile = self.merge2prop(proptemplate, posource)
        print(propfile)
        assert propfile == propexpected

    def test_no_value(self):
        """check that we can handle keys without value"""
        posource = """#: KEY\nmsgctxt "KEY"\nmsgid ""\nmsgstr ""\n"""
        proptemplate = """KEY = \n"""
        propexpected = """KEY = \n"""
        propfile = self.merge2prop(proptemplate, posource)
        print(propfile)
        assert propfile == propexpected

    def test_no_separator(self):
        """check that we can handle keys without separator"""
        posource = """#: KEY\nmsgctxt "KEY"\nmsgid ""\nmsgstr ""\n"""
        proptemplate = """KEY\n"""
        propexpected = """KEY\n"""
        propfile = self.merge2prop(proptemplate, posource)
        print(propfile)
        assert propfile == propexpected

    def test_merging_blank_entries(self):
        """check that we can correctly merge entries that are blank in the template"""
        posource = r'''#: accesskey-accept
msgid ""
"_: accesskey-accept\n"
""
msgstr ""'''
        proptemplate = "accesskey-accept=\n"
        propexpected = "accesskey-accept=\n"
        propfile = self.merge2prop(proptemplate, posource)
        print(propfile)
        assert propfile == propexpected

    def test_merging_fuzzy(self):
        """check merging a fuzzy translation"""
        posource = """#: prop\n#, fuzzy\nmsgid "value"\nmsgstr "waarde"\n"""
        proptemplate = """prop=value\n"""
        propexpected = """prop=value\n"""
        propfile = self.merge2prop(proptemplate, posource)
        print(propfile)
        assert propfile == propexpected

    def test_mozilla_accesskeys(self):
        """check merging Mozilla accesskeys"""
        posource = """#: prop.label prop.accesskey
msgid "&Value"
msgstr "&Waarde"

#: key.label key.accesskey
msgid "&Key"
msgstr "&Sleutel"
"""
        proptemplate = """prop.label=Value
prop.accesskey=V
key.label=Key
key.accesskey=K
"""
        propexpected = """prop.label=Waarde
prop.accesskey=W
key.label=Sleutel
key.accesskey=S
"""
        propfile = self.merge2prop(proptemplate, posource, personality="mozilla")
        print(propfile)
        assert propfile == propexpected

    def test_mozilla_accesskeys_missing_accesskey(self):
        """check merging Mozilla accesskeys"""
        posource = """#: prop.label prop.accesskey
# No accesskey because we forgot or language doesn't do accesskeys
msgid "&Value"
msgstr "Waarde"
"""
        proptemplate = """prop.label=Value
prop.accesskey=V
"""
        propexpected = """prop.label=Waarde
prop.accesskey=V
"""
        propfile = self.merge2prop(proptemplate, posource, personality="mozilla")
        print(propfile)
        assert propfile == propexpected

    def test_mozilla_margin_whitespace(self):
        """Check handling of Mozilla leading and trailing spaces"""
        posource = """#: sepAnd
msgid " and "
msgstr " و "

#: sepComma
msgid ", "
msgstr "، "
"""
        proptemplate = r"""sepAnd = \u0020and\u0020
sepComma = ,\u20
"""
        propexpected = """sepAnd = \\u0020و\\u0020
sepComma = ،\\u0020
"""
        propfile = self.merge2prop(proptemplate, posource, personality="mozilla")
        print(propfile)
        assert propfile == propexpected

    def test_mozilla_all_whitespace(self):
        """
        Check for all white-space Mozilla hack, remove when the corresponding code
        is removed.
        """
        posource = """#: accesskey-accept
msgctxt "accesskey-accept"
msgid ""
msgstr " "

#: accesskey-help
msgid "H"
msgstr "م"
"""
        proptemplate = """accesskey-accept=
accesskey-help=H
"""
        propexpected = """accesskey-accept=
accesskey-help=م
"""
        propfile = self.merge2prop(proptemplate, posource, personality="mozilla")
        print(propfile)
        assert propfile == propexpected

    def test_merging_propertyless_template(self):
        """check that when merging with a template with no property values that we copy the template"""
        posource = ""
        proptemplate = "# A comment\n"
        propexpected = proptemplate
        propfile = self.merge2prop(proptemplate, posource)
        print(propfile)
        assert propfile == propexpected

    def test_delimiters(self):
        """test that we handle different delimiters."""
        posource = """#: prop\nmsgid "value"\nmsgstr "translated"\n"""
        proptemplate = """prop %s value\n"""
        propexpected = """prop %s translated\n"""
        for delim in ["=", ":", ""]:
            print("testing '%s' as delimiter" % delim)
            propfile = self.merge2prop(proptemplate % delim, posource)
            print(propfile)
            assert propfile == propexpected % delim

    def test_empty_value(self):
        """test that we handle an value in the template"""
        posource = """#: key
msgctxt "key"
msgid ""
msgstr "translated"
"""
        proptemplate = """key\n"""
        propexpected = """key = translated\n"""
        propfile = self.merge2prop(proptemplate, posource)
        print(propfile)
        assert propfile == propexpected

    def test_personalities(self):
        """test that we output correctly for Java and Mozilla style property files.  Mozilla uses Unicode, while Java uses escaped Unicode"""
        posource = """#: prop\nmsgid "value"\nmsgstr "ṽḁḽṻḝ"\n"""
        proptemplate = """prop  =  value\n"""
        propexpectedjava = """prop  =  \\u1E7D\\u1E01\\u1E3D\\u1E7B\\u1E1D\n"""
        propfile = self.merge2prop(proptemplate, posource)
        assert propfile == propexpectedjava

        propexpectedmozilla = """prop  =  ṽḁḽṻḝ\n"""
        propfile = self.merge2prop(proptemplate, posource, personality="mozilla")
        assert propfile == propexpectedmozilla

        proptemplate = """prop  =  value\n""".encode("utf-16")
        propexpectedskype = """prop  =  ṽḁḽṻḝ\n"""
        propfile = self.merge2prop(
            proptemplate, posource, personality="skype", encoding="utf-16"
        )
        assert propfile == propexpectedskype

        proptemplate = """"prop" = "value";\n""".encode("utf-16")
        propexpectedstrings = """"prop" = "ṽḁḽṻḝ";\n"""
        propfile = self.merge2prop(
            proptemplate, posource, personality="strings", encoding="utf-16"
        )
        assert propfile == propexpectedstrings

    def test_merging_untranslated_simple(self):
        """check merging untranslated entries in two 1) use English 2) drop key, value pair"""
        posource = """#: prop\nmsgid "value"\nmsgstr ""\n"""
        proptemplate = """prop = value\n"""
        propfile = self.merge2prop(proptemplate, posource)
        print(propfile)
        assert propfile == proptemplate  # We use the existing values
        propfile = self.merge2prop(proptemplate, posource, remove_untranslated=True)
        print(propfile)
        assert propfile == ""  # We drop the key

    def test_merging_untranslated_multiline(self):
        """check merging untranslated entries with multiline values"""
        posource = """#: prop\nmsgid "value1 value2"\nmsgstr ""\n"""
        proptemplate = """prop = value1 \\
    value2
"""
        propexpected = """prop = value1 value2\n"""
        propfile = self.merge2prop(proptemplate, posource)
        print(propfile)
        assert propfile == propexpected  # We use the existing values
        propfile = self.merge2prop(proptemplate, posource, remove_untranslated=True)
        print(propfile)
        assert propfile == ""  # We drop the key

    def test_merging_untranslated_multiline2(self):
        """check merging untranslated entries with multiline values"""
        posource = """
#: legal_text_and_links3
msgid "By using {{clientShortname}} you agree to the {{terms_of_use}} and {{privacy_notice}}."
msgstr ""
"""
        proptemplate = r"""legal_text_and_links3=By using {{clientShortname}} you agree to the {{terms_of_use}} \\
  and {{privacy_notice}}.
"""
        propexpected = """legal_text_and_links3=By using {{clientShortname}} you agree to the {{terms_of_use}} and {{privacy_notice}}.\n"""
        propfile = self.merge2prop(proptemplate, posource)
        print(propfile)
        assert propfile == propexpected  # We use the existing values
        propfile = self.merge2prop(proptemplate, posource, remove_untranslated=True)
        print(propfile)
        assert propfile == ""  # We drop the key

    def test_merging_untranslated_comments(self):
        """check merging untranslated entries with comments"""
        posource = """#: prop\nmsgid "value"\nmsgstr ""\n"""
        proptemplate = """# A comment\nprop = value\n"""
        propexpected = "# A comment\nprop = value\n"
        propfile = self.merge2prop(proptemplate, posource)
        print(propfile)
        assert propfile == propexpected  # We use the existing values
        propfile = self.merge2prop(proptemplate, posource, remove_untranslated=True)
        print(propfile)
        # FIXME ideally we should drop the comment as well as the unit
        assert propfile == "# A comment\n"  # We drop the key

    def test_merging_untranslated_unchanged(self):
        """check removing untranslated entries but keeping unchanged ones"""
        posource = """#: prop
msgid "value"
msgstr ""

#: prop2
msgid "value2"
msgstr "value2"
"""
        proptemplate = """prop=value
prop2=value2
"""

        propexpected = """prop2=value2\n"""
        propfile = self.merge2prop(proptemplate, posource, remove_untranslated=True)
        print(propfile)
        assert propfile == propexpected

    def test_merging_blank(self):
        """We always merge in a blank translation for a blank source"""
        posource = """#: prop
msgctxt "prop"
msgid ""
msgstr "value"

#: prop2
msgctxt "prop2"
msgid ""
msgstr ""
"""
        proptemplate = """prop=
prop2=
"""

        propexpected = """prop=value
prop2=
"""

        propfile = self.merge2prop(proptemplate, posource, remove_untranslated=False)
        print(propfile)
        assert propfile == propexpected
        propfile = self.merge2prop(proptemplate, posource, remove_untranslated=True)
        print(propfile)
        assert propfile == propexpected

    def test_gaia_plurals(self):
        """Test back conversion of gaia plural units."""
        proptemplate = """
message-multiedit-header={[ plural(n) ]}
message-multiedit-header[zero]=Edit
message-multiedit-header[one]={{ n }} selected
message-multiedit-header[two]={{ n }} selected
message-multiedit-header[few]={{ n }} selected
message-multiedit-header[many]={{ n }} selected
message-multiedit-header[other]={{ n }} selected
"""
        posource = r"""#: message-multiedit-header[zero]
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
"""
        propexpected = """
message-multiedit-header={[ plural(n) ]}
message-multiedit-header[zero]=Redigeer
message-multiedit-header[one]={{ n }} gekies
message-multiedit-header[two]={{ n }} gekies
message-multiedit-header[few]={{ n }} gekies
message-multiedit-header[many]={{ n }} gekies
message-multiedit-header[other]={{ n }} gekies
"""
        propfile = self.merge2prop(proptemplate, posource, personality="gaia")
        assert propfile == propexpected

    def test_duplicates(self):
        """Test back conversion of properties with duplicate units."""
        # Test entries with same key and value.
        proptemplate = """
key=value
key=value
"""
        posource = r"""#: key
msgid "value"
msgstr "Waarde"
"""
        propexpected = """
key=Waarde
key=Waarde
"""
        propfile = self.merge2prop(proptemplate, posource, personality="mozilla")
        assert propfile == propexpected

        # Test entries with same key and different value, and single
        # corresponding entry in PO.
        proptemplate = """
key=value
key=another value
"""
        posource = r"""#: key
msgid "value"
msgstr "Waarde"
"""
        propexpected = """
key=Waarde
key=Waarde
"""
        propfile = self.merge2prop(proptemplate, posource, personality="mozilla")
        assert propfile == propexpected

        # Test entries with same key and different value, and two different
        # corresponding entries in PO.
        proptemplate = """
key=value
key=another value
"""
        posource = r"""#: key
msgid "value"
msgstr "Valor"

#: key
msgid "another value"
msgstr "Outro valor"
"""
        propexpected = """
key=Valor
key=Valor
"""
        propfile = self.merge2prop(proptemplate, posource, personality="mozilla")
        assert propfile == propexpected

        # Test entries with same key and different value.
        proptemplate = """
key1=value
key2=value
"""
        posource = r"""#: key1
msgctxt "key1"
msgid "value"
msgstr "Waarde"

#: key2
msgctxt "key2"
msgid "value"
msgstr "Waarde"
"""
        propexpected = """
key1=Waarde
key2=Waarde
"""
        propfile = self.merge2prop(proptemplate, posource, personality="mozilla")
        assert propfile == propexpected

    def test_gwt_plurals(self):
        """Test back conversion of gwt plural units."""
        proptemplate = """
message-multiedit-header={0,number} selected
message-multiedit-header[none]=Edit
message-multiedit-header[one]={0,number} selected
message-multiedit-header[two]={0,number} selected
message-multiedit-header[few]={0,number} selected
message-multiedit-header[many]={0,number} selected
"""
        posource = r"""#: message-multiedit-header
msgctxt "message-multiedit-header"
msgid "Edit"
msgid_plural "{0,number} selected"
msgstr[0] "Redigeer"
msgstr[1] "{0,number} gekies"
msgstr[2] "{0,number} gekies"
msgstr[3] "{0,number} gekies"
msgstr[4] "{0,number} gekies"
msgstr[5] "{0,number} gekies"
"""
        propexpected = """
message-multiedit-header={0,number} gekies
message-multiedit-header[none]=Redigeer
message-multiedit-header[one]={0,number} gekies
message-multiedit-header[two]={0,number} gekies
message-multiedit-header[few]={0,number} gekies
message-multiedit-header[many]={0,number} gekies
"""
        propfile = self.merge2prop(proptemplate, posource, personality="gwt")
        assert propfile == propexpected


class TestPO2PropCommand(test_convert.TestConvertCommand, TestPO2Prop):
    """Tests running actual po2prop commands on files"""

    convertmodule = po2prop
    defaultoptions = {"progress": "none"}
    expected_options = [
        "-t TEMPLATE, --template=TEMPLATE",
        "--fuzzy",
        "--threshold=PERCENT",
        "--personality=TYPE",
        "--encoding=ENCODING",
        "--removeuntranslated",
        "--nofuzzy",
    ]
