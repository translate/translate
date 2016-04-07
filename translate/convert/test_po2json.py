# -*- coding: utf-8 -*-
import sys

from translate.convert import po2json
from translate.misc import wStringIO
from translate.storage import po


class TestPO2JSON(object):

    def po2json(self, po_source, json_template):
        """helper that converts po source to json source without requiring files"""
        input_file = wStringIO.StringIO(po_source)
        json_file = wStringIO.StringIO(json_template)
        input_po = po.pofile(input_file)
        convertor = po2json.rejson(json_template, input_po)
        output_json = convertor.convertstore()
        return output_json.decode('utf-8')

    def test_basic(self):
        """test a basic po to json conversion"""
        json_template = '''{ "text": "A simple string"}'''
        input_po = u'''#: .text
msgid "A simple string"
msgstr "Du texte simple"
'''
        expected_json = '''{
    "text": "Du texte simple"
}
'''
        json_out = self.po2json(input_po, json_template)
        assert json_out == expected_json

    def test_ordering_serialize(self):
        json_template = '''{
    "foo": "foo",
    "bar": "bar",
    "baz": "baz"
}'''
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
        expected_json = '''{
    "foo": "oof",
    "bar": "rab",
    "baz": "zab"
}
'''
        json_out = self.po2json(input_po, json_template)
        assert json_out == expected_json
