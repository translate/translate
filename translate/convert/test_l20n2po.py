# -*- coding: utf-8 -*-

from translate.convert import l20n2po, test_convert
from translate.misc import wStringIO
from translate.storage import po


class TestL20n2PO(object):

    def l20n2po(self, input_string, l20n_template=None, blank_msgstr=False,
                duplicate_style="msgctxt", success_expected=True):
        """helper that converts .ftl (l20n) source to po source without requiring files"""
        inputfile = wStringIO.StringIO(input_string)
        outputfile = wStringIO.StringIO()
        templatefile = None
        if l20n_template:
            templatefile = wStringIO.StringIO(l20n_template)
        expected_result = 1 if success_expected else 0
        result = l20n2po.convertl20n(inputfile, outputfile, templatefile,
                                     blank_msgstr, duplicate_style)
        assert result == expected_result
        return po.pofile(wStringIO.StringIO(outputfile.getvalue()))

    def _single_element(self, po_store):
        """Helper to check PO file has one non-header unit, and return it."""
        assert len(po_store.units) == 2
        assert po_store.units[0].isheader()
        return po_store.units[1]

    def _count_elements(self, po_store):
        """Helper that counts the number of non-header units."""
        assert po_store.units[0].isheader()
        return len(po_store.units) - 1

    def test_convert_empty(self):
        """Check converting empty input file returns no output."""
        target_store = self.l20n2po("# Comment", success_expected=False)
        assert len(target_store.units) == 0

    def test_simpleentry(self):
        """checks that a simple l20n entry converts l20n to a po entry"""
        input_string = """l20n-string-id = Hello, L20n!"""
        target_store = self.l20n2po(input_string)
        target_unit = self._single_element(target_store)
        assert target_unit.source == "Hello, L20n!"
        assert target_unit.target == ""

    def test_convertl20n(self):
        """checks that the convertprop function is working"""
        input_string = """l20n-string-id = Hello, L20n!"""
        target_store = self.l20n2po(input_string)
        target_unit = self._single_element(target_store)
        assert target_unit.source == "Hello, L20n!"
        assert target_unit.target == ""

    def test_tab_at_start_of_value(self):
        """check that tabs in a property are ignored where appropriate"""
        input_string = "property\t=\tvalue"
        target_store = self.l20n2po(input_string)
        target_unit = self._single_element(target_store)
        assert target_unit.getlocations()[0] == "property"
        assert target_unit.source == "value"

    def test_multiline_escaping(self):
        """checks that multiline enties can be parsed"""
        input_string = """description =
  | Loki is a simple micro-blogging
  | app written entirely in <i>HTML5</i>.
  | It uses L20n to implement localization.
"""
        target_store = self.l20n2po(input_string)
        assert self._count_elements(target_store) == 1

    def test_comments(self):
        """test to ensure that we take comments from .properties and place them in .po"""
        input_string = """# Comment
l20n-string-id = Hello, L20n!
"""
        target_store = self.l20n2po(input_string)
        target_unit = self._single_element(target_store)
        assert target_unit.getnotes("developer") == "Comment"

    def test_multiline_comments(self):
        """test to ensure that we handle multiline comments well"""
        input_string = """# Comment
# Comment 2
l20n-string-id = Hello, L20n!
"""
        target_store = self.l20n2po(input_string)
        target_unit = self._single_element(target_store)
        assert target_unit.getnotes("developer") == "Comment\nComment 2"

    def test_plurals(self):
        """Test conversion of plural unit."""
        input_string = """new-notifications = { PLURAL($num) ->
  [0] No new notifications.
  [1] One new notification.
  [2] Two new notifications.
 *[other] { $num } new notifications.
}
"""
        expected_output = """{ PLURAL($num) ->
  [0] No new notifications.
  [1] One new notification.
  [2] Two new notifications.
 *[other] { $num } new notifications.
}"""
        target_store = self.l20n2po(input_string)
        target_unit = self._single_element(target_store)
        assert target_unit.getlocations() == ['new-notifications']
        assert target_unit.source == expected_output


class TestL20n2POCommand(test_convert.TestConvertCommand, TestL20n2PO):
    """Tests running actual prop2po commands on files"""
    convertmodule = l20n2po
    defaultoptions = {"progress": "none"}

    def test_help(self, capsys):
        """tests getting help"""
        options = test_convert.TestConvertCommand.test_help(self, capsys)
        options = self.help_check(options, "-P, --pot")
        options = self.help_check(options, "-t TEMPLATE, --template=TEMPLATE")
