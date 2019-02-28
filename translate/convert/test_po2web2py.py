# -*- coding: utf-8 -*-

from translate.convert import po2web2py
from translate.misc import wStringIO
from translate.storage import po

import six
import pytest


class TestPO2WEB2PY(object):

    def po2web2py(self, po_source):
        """helper that converts po source to web2py source without requiring files"""
        input_file = wStringIO.StringIO(po_source)
        input_po = po.pofile(input_file)
        convertor = po2web2py.po2pydict()
        output_web2py = convertor.convertstore(input_po, False)
        return output_web2py.read()

    def test_basic(self):
        """test a basic po to web2py conversion"""
        input_po = '''#: .text
msgid "A simple string"
msgstr "Du texte simple"
'''
        expected_web2py = '''# -*- coding: utf-8 -*-
{
'A simple string': 'Du texte simple',
}
'''
        web2py_out = self.po2web2py(input_po)
        assert web2py_out == expected_web2py

    @pytest.mark.skipif(six.PY2, reason='Skipping unicode tests on PY2')
    def test_unicode(self):
        """test a po to web2py conversion with unicode"""
        input_po = '''#: .text
msgid "Foobar"
msgstr "Fúbär"
'''
        expected_web2py = '''# -*- coding: utf-8 -*-
{
'Foobar': 'Fúbär',
}
'''
        web2py_out = self.po2web2py(input_po)
        assert web2py_out == expected_web2py

    def test_ordering_serialize(self):
        """test alphabetic ordering in po to web2py conversion"""
        input_po = '''
#: .foo
msgid "foo"
msgstr "oof"

#: .bar
msgid "bar"
msgstr "rab"

#: .baz
msgid "baz"
msgstr "zab"
'''
        expected_web2py = '''# -*- coding: utf-8 -*-
{
'bar': 'rab',
'baz': 'zab',
'foo': 'oof',
}
'''
        web2py_out = self.po2web2py(input_po)
        assert web2py_out == expected_web2py
