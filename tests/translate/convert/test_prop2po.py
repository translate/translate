from io import BytesIO

from translate.convert import prop2po, test_convert
from translate.storage import po, properties


class TestProp2PO:
    @staticmethod
    def prop2po(propsource, proptemplate=None, personality="java"):
        """helper that converts .properties source to po source without requiring files"""
        inputfile = BytesIO(propsource.encode())
        inputprop = properties.propfile(inputfile, personality=personality)
        convertor = prop2po.prop2po(personality=personality)
        if proptemplate:
            templatefile = BytesIO(proptemplate.encode())
            templateprop = properties.propfile(templatefile)
            outputpo = convertor.mergestore(templateprop, inputprop)
        else:
            outputpo = convertor.convertstore(inputprop)
        return outputpo

    @staticmethod
    def convertprop(propsource):
        """call the convertprop, return the outputfile"""
        inputfile = BytesIO(propsource.encode())
        outputfile = BytesIO()
        templatefile = None
        assert prop2po.convertprop(inputfile, outputfile, templatefile)
        return outputfile.getvalue()

    @staticmethod
    def singleelement(pofile):
        """checks that the pofile contains a single non-header element, and returns it"""
        assert len(pofile.units) == 2
        assert pofile.units[0].isheader()
        print(pofile)
        return pofile.units[1]

    @staticmethod
    def countelements(pofile):
        """counts the number of non-header entries"""
        assert pofile.units[0].isheader()
        print(pofile)
        return len(pofile.units) - 1

    def test_simpleentry(self):
        """checks that a simple properties entry converts properly to a po entry"""
        propsource = "SAVEENTRY=Save file\n"
        pofile = self.prop2po(propsource)
        pounit = self.singleelement(pofile)
        assert pounit.source == "Save file"
        assert pounit.target == ""

    def test_convertprop(self):
        """checks that the convertprop function is working"""
        propsource = "SAVEENTRY=Save file\n"
        posource = self.convertprop(propsource)
        pofile = po.pofile(BytesIO(posource))
        pounit = self.singleelement(pofile)
        assert pounit.source == "Save file"
        assert pounit.target == ""

    def test_no_value_entry(self):
        """checks that a properties entry without value is converted"""
        propsource = "KEY = \n"
        pofile = self.prop2po(propsource)
        pounit = self.singleelement(pofile)
        assert pounit.getcontext() == "KEY"
        assert pounit.source == ""
        assert pounit.target == ""

    def test_no_separator_entry(self):
        """checks that a properties entry without separator is converted"""
        propsource = "KEY\n"
        pofile = self.prop2po(propsource)
        pounit = self.singleelement(pofile)
        assert pounit.getcontext() == "KEY"
        assert pounit.source == ""
        assert pounit.target == ""

    def test_tab_at_end_of_string(self):
        """check that we preserve tabs at the end of a string"""
        propsource = r"TAB_AT_END=This setence has a tab at the end.\t"
        pofile = self.prop2po(propsource)
        pounit = self.singleelement(pofile)
        assert pounit.source == "This setence has a tab at the end.\t"

        propsource = (
            r"SPACE_THEN_TAB_AT_END=This setence has a space then tab at the end. \t"
        )
        pofile = self.prop2po(propsource)
        pounit = self.singleelement(pofile)
        assert pounit.source == "This setence has a space then tab at the end. \t"

        propsource = r"SPACE_AT_END=This setence will keep its 4 spaces at the end.    "
        pofile = self.prop2po(propsource)
        pounit = self.singleelement(pofile)
        assert pounit.source == "This setence will keep its 4 spaces at the end.    "

        propsource = (
            r"SPACE_AT_END_NO_TRIM=This setence will keep its 4 spaces at the end.\    "
        )
        pofile = self.prop2po(propsource)
        pounit = self.singleelement(pofile)
        assert pounit.source == "This setence will keep its 4 spaces at the end.    "

        propsource = r"SPACE_AT_END_NO_TRIM2=This setence will keep its 4 spaces at the end.\\    "
        pofile = self.prop2po(propsource)
        pounit = self.singleelement(pofile)
        assert pounit.source == "This setence will keep its 4 spaces at the end.\\    "

    def test_tab_at_start_of_value(self):
        """check that tabs in a property are ignored where appropriate"""
        propsource = r"property	=	value"
        pofile = self.prop2po(propsource)
        pounit = self.singleelement(pofile)
        assert pounit.getlocations()[0] == "property"
        assert pounit.source == "value"

    def test_unicode(self):
        """checks that unicode entries convert properly"""
        unistring = r"Norsk bokm\u00E5l"
        propsource = "nb = %s\n" % unistring
        pofile = self.prop2po(propsource)
        pounit = self.singleelement(pofile)
        print(repr(pofile.units[0].target))
        print(repr(pounit.source))
        assert pounit.source == "Norsk bokm\u00E5l"

    def test_multiline_escaping(self):
        """checks that multiline enties can be parsed"""
        propsource = r"""5093=Unable to connect to your IMAP server. You may have exceeded the maximum number \
of connections to this server. If so, use the Advanced IMAP Server Settings dialog to \
reduce the number of cached connections."""
        pofile = self.prop2po(propsource)
        print(repr(pofile.units[1].target))
        assert self.countelements(pofile) == 1

    def test_comments(self):
        """test to ensure that we take comments from .properties and place them in .po"""
        propsource = """# Comment
prefPanel-smime=Security"""
        pofile = self.prop2po(propsource)
        pounit = self.singleelement(pofile)
        assert pounit.getnotes("developer") == "# Comment"

    def test_multiline_comments(self):
        """test to ensure that we handle multiline comments well"""
        propsource = """# Comment
# commenty 2

## @name GENERIC_ERROR
## @loc none
prefPanel-smime=
"""
        pofile = self.prop2po(propsource)
        print(bytes(pofile))
        # header comments:
        assert b"#. # Comment\n#. # commenty 2" in bytes(pofile)
        pounit = self.singleelement(pofile)
        assert pounit.getnotes("developer") == "## @name GENERIC_ERROR\n## @loc none"

    def test_folding_accesskeys(self):
        """check that we can fold various accesskeys into their associated label (bug #115)"""
        propsource = r"""cmd_addEngine.label = Add Engines...
cmd_addEngine.accesskey = A"""
        pofile = self.prop2po(propsource, personality="mozilla")
        pounit = self.singleelement(pofile)
        assert pounit.source == "&Add Engines..."

    def test_dont_translate(self):
        """check that we know how to ignore don't translate instructions in properties files (bug #116)"""
        propsource = """# LOCALIZATION NOTE (dont): DONT_TRANSLATE.
dont=don't translate me
do=translate me
"""
        pofile = self.prop2po(propsource)
        assert self.countelements(pofile) == 1

    def test_emptyproperty(self):
        """checks that empty property definitions survive into po file, bug 15"""
        for delimiter in ["=", ""]:
            propsource = "# comment\ncredit%s" % delimiter
            pofile = self.prop2po(propsource)
            pounit = self.singleelement(pofile)
            assert pounit.getlocations() == ["credit"]
            assert pounit.getcontext() == "credit"
            assert 'msgctxt "credit"' in str(pounit)
            assert b"#. # comment" in bytes(pofile)
            assert pounit.source == ""

    def test_emptyproperty_translated(self):
        """checks that if we translate an empty property it makes it into the PO"""
        for delimiter in ["=", ""]:
            proptemplate = "credit%s" % delimiter
            propsource = "credit=Translators Names"
            pofile = self.prop2po(propsource, proptemplate)
            pounit = self.singleelement(pofile)
            assert pounit.getlocations() == ["credit"]
            # FIXME we don't seem to get a _: comment but we should
            # assert pounit.getcontext() == "credit"
            assert pounit.source == ""
            assert pounit.target == "Translators Names"

    def test_newlines_in_value(self):
        """check that we can carry newlines that appear in the property value into the PO"""
        propsource = """prop=\\nvalue\\n\n"""
        pofile = self.prop2po(propsource)
        unit = self.singleelement(pofile)
        assert unit.source == "\nvalue\n"

    def test_header_comments(self):
        """check that we can handle comments not directly associated with a property"""
        propsource = """# Header comment\n\n# Comment\n\nprop=value\n"""
        pofile = self.prop2po(propsource)
        unit = self.singleelement(pofile)
        assert unit.source == "value"
        assert unit.getnotes("developer") == "# Comment"

    def test_unassociated_comment_order(self):
        """check that we can handle the order of unassociated comments"""
        propsource = """# Header comment\n\n# 1st Unassociated comment\n\n# 2nd Connected comment\nprop=value\n"""
        pofile = self.prop2po(propsource)
        unit = self.singleelement(pofile)
        assert unit.source == "value"
        assert (
            unit.getnotes("developer")
            == "# 1st Unassociated comment\n\n# 2nd Connected comment"
        )

    def test_x_header(self):
        """Test that we correctly create the custom header entries
        (accelerators, merge criterion).
        """
        propsource = """prop=value\n"""

        outputpo = self.prop2po(propsource, personality="mozilla")
        assert b"X-Accelerator-Marker" in bytes(outputpo)
        assert b"X-Merge-On" in bytes(outputpo)

        # Even though the gaia flavour inherrits from mozilla, it should not
        # get the header
        outputpo = self.prop2po(propsource, personality="gaia")
        assert b"X-Accelerator-Marker" not in bytes(outputpo)
        assert b"X-Merge-On" not in bytes(outputpo)

    def test_gaia_plurals(self):
        """Test conversion of gaia plural units."""
        propsource = """
message-multiedit-header={[ plural(n) ]}
message-multiedit-header[zero]=Edit
message-multiedit-header[one]={{ n }} selected
message-multiedit-header[two]={{ n }} selected
message-multiedit-header[few]={{ n }} selected
message-multiedit-header[many]={{ n }} selected
message-multiedit-header[other]={{ n }} selected
"""
        outputpo = self.prop2po(propsource, personality="gaia")
        pounit = outputpo.units[-1]
        assert pounit.hasplural()
        assert pounit.getlocations() == ["message-multiedit-header"]

        print(outputpo)
        zero_unit = outputpo.units[-2]
        assert not zero_unit.hasplural()
        assert zero_unit.source == "Edit"

    def test_successive_gaia_plurals(self):
        """Test conversion of two successive gaia plural units."""
        propsource = """
message-multiedit-header={[ plural(n) ]}
message-multiedit-header[zero]=Edit
message-multiedit-header[one]={{ n }} selected
message-multiedit-header[two]={{ n }} selected
message-multiedit-header[few]={{ n }} selected
message-multiedit-header[many]={{ n }} selected
message-multiedit-header[other]={{ n }} selected

message-multiedit-header2={[ plural(n) ]}
message-multiedit-header2[zero]=Edit 2
message-multiedit-header2[one]={{ n }} selected 2
message-multiedit-header2[two]={{ n }} selected 2
message-multiedit-header2[few]={{ n }} selected 2
message-multiedit-header2[many]={{ n }} selected 2
message-multiedit-header2[other]={{ n }} selected 2
"""
        outputpo = self.prop2po(propsource, personality="gaia")
        pounit = outputpo.units[-1]
        assert pounit.hasplural()
        assert pounit.getlocations() == ["message-multiedit-header2"]

        pounit = outputpo.units[-3]
        assert pounit.hasplural()
        assert pounit.getlocations() == ["message-multiedit-header"]

        print(outputpo)
        zero_unit = outputpo.units[-2]
        assert not zero_unit.hasplural()
        assert zero_unit.source == "Edit 2"

        zero_unit = outputpo.units[-4]
        assert not zero_unit.hasplural()
        assert zero_unit.source == "Edit"

    def test_duplicate_keys(self):
        """Check that we correctly handle duplicate keys."""
        source = """
key=value
key=value
"""
        po_file = self.prop2po(source)
        assert self.countelements(po_file) == 1
        po_unit = self.singleelement(po_file)
        assert po_unit.source == "value"

        source = """
key=value
key=another value
"""
        po_file = self.prop2po(source)
        assert self.countelements(po_file) == 2
        po_unit = po_file.units[1]
        assert po_unit.source == "value"
        assert po_unit.getlocations() == ["key"]
        po_unit = po_file.units[2]
        assert po_unit.source == "another value"
        assert po_unit.getlocations() == ["key"]

        source = """
key1=value
key2=value
"""
        po_file = self.prop2po(source)
        assert self.countelements(po_file) == 2
        po_unit = po_file.units[1]
        assert po_unit.source == "value"
        assert po_unit.getlocations() == ["key1"]
        po_unit = po_file.units[2]
        assert po_unit.source == "value"
        assert po_unit.getlocations() == ["key2"]

    def test_gwt_plurals(self):
        """Test conversion of gwt plural units."""
        propsource = """
message-multiedit-header={0,number} selected
message-multiedit-header[none]=Edit
message-multiedit-header[one]={0,number} selected
message-multiedit-header[two]={0,number} selected
message-multiedit-header[few]={0,number} selected
message-multiedit-header[many]={0,number} selected
"""
        outputpo = self.prop2po(propsource, personality="gwt")
        pounit = outputpo.units[-1]
        assert pounit.getlocations() == ["message-multiedit-header"]


class TestProp2POCommand(test_convert.TestConvertCommand, TestProp2PO):
    """Tests running actual prop2po commands on files"""

    convertmodule = prop2po
    defaultoptions = {"progress": "none"}
    expected_options = [
        "-P, --pot",
        "-t TEMPLATE, --template=TEMPLATE",
        "--personality=TYPE",
        "--encoding=ENCODING",
        "--duplicates=DUPLICATESTYLE",
    ]
