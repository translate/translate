from io import BytesIO

from translate.convert import po2json
from translate.storage import po


class TestPO2JSON:
    example_json_template = """{
    "foo": "foo",
    "bar": "bar",
    "baz": "baz",
    "qux": "qux"
}"""

    example_input_po = """
#: .foo
msgid "foo"
msgstr "oof"

#: .bar
#, fuzzy
msgid "bar"
msgstr "rab"

#: .baz
#, fuzzy
msgid "baz"
msgstr ""

#: .qux
msgid "qux"
msgstr ""
"""

    @staticmethod
    def po2json(
        po_source, json_template, includefuzzy=False, remove_untranslated=False
    ):
        """helper that converts po source to json source without requiring files"""
        input_file = BytesIO(po_source.encode())
        input_po = po.pofile(input_file)
        convertor = po2json.rejson(json_template, input_po)
        output_json = convertor.convertstore(includefuzzy, remove_untranslated)
        return output_json.decode("utf-8")

    def test_basic(self):
        """test a basic po to json conversion"""
        json_template = """{ "text": "A simple string"}"""
        input_po = """#: .text
msgid "A simple string"
msgstr "Du texte simple"
"""
        expected_json = """{
    "text": "Du texte simple"
}
"""
        json_out = self.po2json(input_po, json_template)
        assert json_out == expected_json

    def test_ordering_serialize(self):
        json_template = """{
    "foo": "foo",
    "bar": "bar",
    "baz": "baz"
}"""
        input_po = """
#: .foo
msgid "foo"
msgstr "oof"

#: .bar
msgid "bar"
msgstr "rab"

#: .baz
msgid "baz"
msgstr "zab"
"""
        expected_json = """{
    "foo": "oof",
    "bar": "rab",
    "baz": "zab"
}
"""
        json_out = self.po2json(input_po, json_template)
        assert json_out == expected_json

    def test_dont_use_empty_translation(self):
        """Don't use empty translation in output"""
        json_template = """{
    "foo": "foo"
}"""
        input_po = """
#: .foo
msgid "foo"
msgstr ""
"""
        expected_json = """{
    "foo": "foo"
}
"""
        json_out = self.po2json(input_po, json_template)
        assert json_out == expected_json

    def test_includefuzzy_false_remove_untranslated_false(self):
        """When includefuzzy is False and remove_untranslated is False"""

        expected_json = """{
    "foo": "oof",
    "bar": "bar",
    "baz": "baz",
    "qux": "qux"
}
"""
        json_out = self.po2json(
            self.example_input_po,
            self.example_json_template,
            includefuzzy=False,
            remove_untranslated=False,
        )
        assert json_out == expected_json

    def test_includefuzzy_false_remove_untranslated_true(self):
        """When includefuzzy is False and remove_untranslated is True"""

        expected_json = """{
    "foo": "oof"
}
"""
        json_out = self.po2json(
            self.example_input_po,
            self.example_json_template,
            includefuzzy=False,
            remove_untranslated=True,
        )
        assert json_out == expected_json

    def test_includefuzzy_true_remove_untranslated_false(self):
        """When includefuzzy is True and remove_untranslated is False"""

        expected_json = """{
    "foo": "oof",
    "bar": "rab",
    "baz": "baz",
    "qux": "qux"
}
"""
        json_out = self.po2json(
            self.example_input_po,
            self.example_json_template,
            includefuzzy=True,
            remove_untranslated=False,
        )
        assert json_out == expected_json

    def test_includefuzzy_true_remove_untranslated_true(self):
        """When includefuzzy is True and remove_untranslated is True"""

        expected_json = """{
    "foo": "oof"
}
"""
        json_out = self.po2json(
            self.example_input_po,
            self.example_json_template,
            includefuzzy=True,
            remove_untranslated=True,
        )
        assert json_out == expected_json
