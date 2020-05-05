# -*- coding: utf-8 -*-
from io import BytesIO
from translate.convert import po2json
from translate.storage import po


class TestPO2JSON:

    def po2json(self, po_source, json_template):
        """helper that converts po source to json source without requiring files"""
        input_file = BytesIO(po_source.encode())
        json_file = BytesIO(json_template.encode())
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
