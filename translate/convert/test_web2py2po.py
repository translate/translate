from translate.convert import web2py2po
from translate.storage import po
from translate.storage.test_base import first_translatable, headerless_len


class TestWEB2PY2PO:
    @staticmethod
    def web2py2po(web2py_source):
        """helper that converts po source to web2py source without requiring files"""
        input_web2py = eval(web2py_source)
        new_pofile = po.pofile()
        convertor = web2py2po.web2py2po(new_pofile)
        return convertor.convertstore(input_web2py)

    @staticmethod
    def singleelement(storage):
        """checks that the pofile contains a single non-header element, and returns it"""
        assert headerless_len(storage.units) == 1
        return first_translatable(storage)

    def test_basic(self):
        """test a basic web2py to po conversion"""
        input_web2py = """# -*- coding: utf-8 -*-
{
'A simple string': 'Du texte simple',
}
"""

        po_out = self.web2py2po(input_web2py)
        pounit = self.singleelement(po_out)
        assert pounit.source == "A simple string"
        assert pounit.target == "Du texte simple"

    def test_unicode(self):
        """test a web2py to po conversion with unicode"""
        input_web2py = """# -*- coding: utf-8 -*-
{
'Foobar': 'Fúbär',
}
"""

        po_out = self.web2py2po(input_web2py)
        pounit = self.singleelement(po_out)
        assert pounit.source == "Foobar"
        assert pounit.target == "Fúbär"

    def test_markmin(self):
        """test removal of @markmin in po to web2py conversion"""
        input_web2py = """# -*- coding: utf-8 -*-
{
'@markmin\\x01Hello **world**!': 'Hello **world**!',
}
"""

        po_out = self.web2py2po(input_web2py)
        pounit = self.singleelement(po_out)
        assert pounit.source == "@markmin\x01Hello **world**!"
        assert pounit.target == ""
