# -*- coding: utf-8 -*-

from translate.convert import l20n2po, test_convert
from translate.misc import wStringIO
from translate.storage import po, l20n


class TestL20n2PO(object):

    def l20n2po(self, l20n_source, l20n_template=None):
        """helper that converts .ftl (l20n) source to po source without requiring files"""
        inputfile = wStringIO.StringIO(l20n_source)
        input_l20n = l20n.l20nfile(inputfile)
        convertor = l20n2po.l20n2po()
        if l20n_template:
            templatefile = wStringIO.StringIO(l20n_template)
            template_l20n = l20n.l20nfile(templatefile)
            outputpo = convertor.merge_stores(template_l20n, input_l20n)
        else:
            outputpo = convertor.convert_store(input_l20n)
        return outputpo

    def convert_l20n(self, l20n_source):
        """call the convert_l20n, return the outputfile"""
        inputfile = wStringIO.StringIO(l20n_source)
        outputfile = wStringIO.StringIO()
        templatefile = None
        assert l20n2po.convertl20n(inputfile, outputfile, templatefile)
        return outputfile.getvalue()

    def singleelement(self, pofile):
        """checks that the pofile contains a single non-header element, and returns it"""
        assert len(pofile.units) == 2
        assert pofile.units[0].isheader()
        return pofile.units[1]

    def countelements(self, pofile):
        """counts the number of non-header entries"""
        assert pofile.units[0].isheader()
        return len(pofile.units) - 1

    def test_simpleentry(self):
        """checks that a simple l20n entry converts l20n to a po entry"""
        l20n_source = 'l20n-string-id = Hello, L20n!\n'
        pofile = self.l20n2po(l20n_source)
        pounit = self.singleelement(pofile)
        assert pounit.source == "Hello, L20n!"
        assert pounit.target == ""

    def test_convertl20n(self):
        """checks that the convertprop function is working"""
        l20n_source = 'l20n-string-id = Hello, L20n!\n'
        posource = self.convert_l20n(l20n_source)
        pofile = po.pofile(wStringIO.StringIO(posource))
        pounit = self.singleelement(pofile)
        assert pounit.source == "Hello, L20n!"
        assert pounit.target == ""

    def test_tab_at_start_of_value(self):
        """check that tabs in a property are ignored where appropriate"""
        propsource = r"property	=	value"
        pofile = self.l20n2po(propsource)
        pounit = self.singleelement(pofile)
        assert pounit.getlocations()[0] == "property"
        assert pounit.source == "value"

    def test_multiline_escaping(self):
        """checks that multiline enties can be parsed"""
        l20n_source = r"""description =
  | Loki is a simple micro-blogging
  | app written entirely in <i>HTML5</i>.
  | It uses L20n to implement localization."""
        pofile = self.l20n2po(l20n_source)
        assert self.countelements(pofile) == 1

    def test_comments(self):
        """test to ensure that we take comments from .properties and place them in .po"""
        l20n_source = r"""# Comment
l20n-string-id = Hello, L20n!\n"""
        pofile = self.l20n2po(l20n_source)
        pounit = self.singleelement(pofile)
        assert pounit.getnotes("developer") == "Comment"

    def test_multiline_comments(self):
        """test to ensure that we handle multiline comments well"""
        l20n_source = """# Comment
# Comment 2
l20n-string-id = Hello, L20n!\n"""

        pofile = self.l20n2po(l20n_source)
        pounit = self.singleelement(pofile)
        assert pounit.getnotes("developer") == "Comment\nComment 2"

    def test_plurals(self):
        """Test conversion of plural unit."""
        l20n_source = """new-notifications = { PLURAL($num) ->
  [0] No new notifications.
  [1] One new notification.
  [2] Two new notifications.
 *[other] { $num } new notifications.
}
"""
        pofile = self.l20n2po(l20n_source)
        pounit = self.singleelement(pofile)
        assert pounit.getlocations() == [u'new-notifications']
        assert pounit.source == """{ PLURAL($num) ->
  [0] No new notifications.
  [1] One new notification.
  [2] Two new notifications.
 *[other] { $num } new notifications.
}"""


class TestL20n2POCommand(test_convert.TestConvertCommand, TestL20n2PO):
    """Tests running actual prop2po commands on files"""
    convertmodule = l20n2po
    defaultoptions = {"progress": "none"}

    def test_help(self):
        """tests getting help"""
        options = test_convert.TestConvertCommand.test_help(self)
        options = self.help_check(options, "-P, --pot")
        options = self.help_check(options, "-t TEMPLATE, --template=TEMPLATE")
