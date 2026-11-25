from io import BytesIO

import pytest

from translate.convert import po2yaml, yaml2po
from translate.storage import po, yaml

from . import test_convert


class TestPO2YAML:
    ConverterClass = po2yaml.po2yaml

    def _convert(
        self,
        input_string,
        template_string=None,
        include_fuzzy=False,
        output_threshold=None,
        success_expected=True,
    ):
        """Helper that converts to target format without using files."""
        input_file = BytesIO(input_string.encode())
        output_file = BytesIO()
        template_file = None
        if template_string:
            template_file = BytesIO(template_string.encode())
        expected_result = 1 if success_expected else 0
        converter = self.ConverterClass(
            input_file, output_file, template_file, include_fuzzy, output_threshold
        )
        assert converter.run() == expected_result
        return converter.target_store, output_file

    def _convert_to_store(self, *args, **kwargs):
        """Helper that converts to target format store without using files."""
        return self._convert(*args, **kwargs)[0]

    def _convert_to_string(self, *args, **kwargs):
        """Helper that converts to target format string without using files."""
        return self._convert(*args, **kwargs)[1].getvalue().decode("utf-8")

    def test_convert_empty_PO(self) -> None:
        """Check converting empty PO returns no output."""
        assert self._convert_to_string("", "{}") == "{}\n"

    def test_convert_no_templates(self) -> None:
        """Check converter doesn't allow to pass no templates."""
        with pytest.raises(ValueError):
            self._convert_to_store("")

    def test_simple_output(self) -> None:
        """Check that a simple single entry PO converts valid YAML output."""
        input_string = """
#: key
msgid "Hello, World!"
msgstr ""
"""
        template_string = 'key: "Hello, World!"'
        expected_output = """key: Hello, World!
"""
        assert expected_output == self._convert_to_string(input_string, template_string)

    def test_keeps_float_and_date_values(self) -> None:
        input_string = """
#: site->title
msgid "My Blog"
msgstr "Mon blog"

#: 404
msgid "Not found"
msgstr "Introuvable"
"""
        template_string = """site:
  title: My Blog
  version: 2.1
  updated: 2026-01-15
config:
  ratio: 0.5
404: Not found
"""
        expected_output = """site:
  title: Mon blog
  version: 2.1
  updated: 2026-01-15
config:
  ratio: 0.5
'404': Introuvable
"""
        assert expected_output == self._convert_to_string(input_string, template_string)

    def test_simple(self) -> None:
        """Check that a simple single entry PO converts to a YAML unit."""
        input_string = """
#: key
msgid "Hello, World!"
msgstr ""
"""
        template_string = 'key: "Hello, World!"'
        target_store = self._convert_to_store(input_string, template_string)
        target_unit = target_store.units[0]
        assert len(target_store.units) == 1
        assert target_unit.getid() == "key"
        assert target_unit.source == "Hello, World!"
        assert target_unit.target == "Hello, World!"

    def test_translated(self) -> None:
        """Check that a simple translated PO converts to a translated YAML."""
        input_string = """
#: key
msgid "Hello, World!"
msgstr "Ola mundo!"
"""
        template_string = 'key: "Hello, World!"'
        target_store = self._convert_to_store(input_string, template_string)
        target_unit = target_store.units[0]
        assert len(target_store.units) == 1
        assert target_unit.getid() == "key"
        assert target_unit.source == "Ola mundo!"
        assert target_unit.target == "Ola mundo!"

    def test_no_fuzzy(self) -> None:
        """Check that a simple fuzzy PO converts to a translated YAML."""
        input_string = """
#: key
#, fuzzy
msgid "Hello, World!"
msgstr "Ola mundo!"
"""
        template_string = 'key: "Hello, World!"'
        target_store = self._convert_to_store(input_string, template_string)
        target_unit = target_store.units[0]
        assert len(target_store.units) == 1
        assert target_unit.getid() == "key"
        assert target_unit.source == "Hello, World!"
        assert target_unit.target == "Hello, World!"

    def test_allow_fuzzy(self) -> None:
        """Check that a simple fuzzy PO converts to a translated YAML."""
        input_string = """
#: key
#, fuzzy
msgid "Hello, World!"
msgstr "Ola mundo!"
"""
        template_string = 'key: "Hello, World!"'
        target_store = self._convert_to_store(
            input_string, template_string, include_fuzzy=True
        )
        target_unit = target_store.units[0]
        assert len(target_store.units) == 1
        assert target_unit.getid() == "key"
        assert target_unit.source == "Ola mundo!"
        assert target_unit.target == "Ola mundo!"

    def test_nested(self) -> None:
        """Check converting to nested YAML."""
        input_string = """
#: foo->bar
msgid "bar"
msgstr ""

#: foo->baz->boo
msgid "booo"
msgstr ""

#: foo->
msgid "bar2"
msgstr ""

#: eggs
msgid "spam"
msgstr ""
"""
        template_string = """
foo:
    bar: bar
    '': bar2
    baz:
        boo: booo
eggs: spam
"""
        target_store = self._convert_to_store(input_string, template_string)
        assert len(target_store.units) == 4
        assert target_store.units[0].getlocations() == ["foo->bar"]
        assert target_store.units[0].source == "bar"
        assert target_store.units[0].target == "bar"
        assert target_store.units[1].getlocations() == ["foo->"]
        assert target_store.units[1].source == "bar2"
        assert target_store.units[1].target == "bar2"
        assert target_store.units[2].getlocations() == ["foo->baz->boo"]
        assert target_store.units[2].source == "booo"
        assert target_store.units[2].target == "booo"
        assert target_store.units[3].getlocations() == ["eggs"]
        assert target_store.units[3].source == "spam"
        assert target_store.units[3].target == "spam"

    def test_convert_completion_below_threshold(self) -> None:
        """Check no conversion if input completion is below threshold."""
        input_string = """
#: key
msgid "Hello, World!"
msgstr ""
"""
        template_string = 'key: "Hello, World!"'
        expected_output = ""
        # Input completion is 0% so with a 70% threshold it should not output.
        output = self._convert_to_string(
            input_string, template_string, output_threshold=70, success_expected=False
        )
        assert output == expected_output

    def test_convert_completion_above_threshold(self) -> None:
        """Check no conversion if input completion is above threshold."""
        input_string = """
#: key
msgid "Hello, World!"
msgstr "Ola mundo!"
"""
        template_string = 'key: "Hello, World!"'
        expected_output = """key: Ola mundo!
"""
        # Input completion is 100% so with a 70% threshold it should output.
        output = self._convert_to_string(
            input_string, template_string, output_threshold=70
        )
        assert output == expected_output

    @pytest.mark.parametrize("separator", [" ", "\n#: "])
    def test_duplicates_merge(self, separator) -> None:
        """Check that PO files created with --duplicates=merge are handled."""
        # A single PO unit with two locations (result of yaml2po --duplicates=merge)
        input_string = f"""
#: navbar-%3Eabout{separator}footer-%3Eabout_aboutus
msgid "About us"
msgstr "Über uns"
"""
        template_string = """navbar:
  about: About us
footer:
  about_aboutus: About us
"""
        target_store = self._convert_to_store(input_string, template_string)
        assert len(target_store.units) == 2
        assert target_store.units[0].getlocations() == ["navbar->about"]
        assert target_store.units[0].source == "Über uns"
        assert target_store.units[1].getlocations() == ["footer->about_aboutus"]
        assert target_store.units[1].source == "Über uns"

    @pytest.mark.parametrize("separator", [" ", "\n#: "])
    def test_duplicates_merge_untranslated(self, separator) -> None:
        """Check that untranslated PO with multiple locations copies source."""
        input_string = f"""
#: navbar-%3Eabout{separator}footer-%3Eabout_aboutus
msgid "About us"
msgstr ""
"""
        template_string = """navbar:
  about: About us
footer:
  about_aboutus: About us
"""
        target_store = self._convert_to_store(input_string, template_string)
        assert len(target_store.units) == 2
        assert target_store.units[0].getlocations() == ["navbar->about"]
        assert target_store.units[0].source == "About us"
        assert target_store.units[1].getlocations() == ["footer->about_aboutus"]
        assert target_store.units[1].source == "About us"


class TestRubyPO2YAML(TestPO2YAML):
    """Tests for po2yaml with Ruby personality."""

    def _convert(
        self,
        input_string,
        template_string=None,
        include_fuzzy=False,
        output_threshold=None,
        success_expected=True,
    ):
        """Helper that converts using Ruby personality."""
        input_file = BytesIO(input_string.encode())
        output_file = BytesIO()
        template_file = None
        if template_string:
            template_file = BytesIO(template_string.encode())
        expected_result = 1 if success_expected else 0
        converter = self.ConverterClass(
            input_file,
            output_file,
            template_file,
            include_fuzzy,
            output_threshold,
            personality="ruby",
        )
        assert converter.run() == expected_result
        return converter.target_store, output_file

    def test_convert_empty_PO(self) -> None:
        """Check converting empty PO returns no output."""
        assert self._convert_to_string("", "en: {}") == "en: {}\n"

    def test_simple_output(self) -> None:
        """Check that a simple single entry PO converts valid Ruby YAML output."""
        input_string = """
#: key
msgid "Hello, World!"
msgstr ""
"""
        template_string = """en:
  key: "Hello, World!"
"""
        output = self._convert_to_string(input_string, template_string)
        assert "key: Hello, World!" in output

    def test_convert_completion_above_threshold(self) -> None:
        """Check conversion with completion above threshold."""
        input_string = """
#: key
msgid "Hello, World!"
msgstr "Ola mundo!"
"""
        template_string = """en:
  key: "Hello, World!"
"""
        output = self._convert_to_string(
            input_string, template_string, output_threshold=70
        )
        assert "key: Ola mundo!" in output

    def test_empty_included_fuzzy_plural_uses_source(self) -> None:
        catalog = '\n#: count\n#, fuzzy\nmsgid "item"\nmsgid_plural "items"\nmsgstr[0] ""\nmsgstr[1] ""\n'
        store, output = self._convert(
            catalog, "en: {count: {one: item, other: items}}", include_fuzzy=True
        )
        assert type(store).parsestring(output.getvalue()).units[0].plural_forms == {
            "one": "item",
            "other": "items",
        }

    def test_partial_plural_keeps_empty_slot_untranslated(self) -> None:
        catalog = '\n#: count\nmsgid "item"\nmsgid_plural "items"\nmsgstr[0] "translated"\nmsgstr[1] ""\n'
        store, output = self._convert(catalog, "en: {count: {one: item, other: items}}")
        parsed = type(store).parsestring(output.getvalue())
        assert parsed.units[0].plural_forms == {"one": "translated"}

    def test_untranslated_source_in_single_form_locale(self) -> None:
        catalog = 'msgid ""\nmsgstr "Language: ja\\n"\n\n#: count\nmsgid "item"\nmsgid_plural "items"\nmsgstr[0] ""\n'
        output = self._convert_to_string(
            catalog, "en: {count: {one: item, other: items}}"
        )
        assert "one: item" in output
        assert "other: items" in output

    def test_declared_locale_headers(self) -> None:
        for locale, header, values in [
            ("en", "plural=(n != 1); nplurals=2;", ["one", "other"]),
            ("ckb", "nplurals= 2; plural=n != 1;", ["one", "other"]),
            (
                "mk",
                "nplurals=2; plural=n%10==1 && n%100!=11 ? 0 : 1;",
                ["one", "other"],
            ),
            ("is", "nplurals=2; plural=(n%10!=1 || n%100==11);", ["one", "other"]),
            (
                "cy",
                "nplurals=6; plural=n==0?5:n==1?4:n==2?3:n==3?2:n==6?1:0;",
                ["other", "many", "few", "two", "one", "zero"],
            ),
            ("cy", "nplurals=2; plural=n==2;", ["other", "two"]),
            ("zh", "nplurals=1; plural=0;", ["other"]),
            ("pt_PT", "nplurals=2; plural=(n != 1);", ["one", "other"]),
        ]:
            catalog = f'msgid ""\nmsgstr ""\n"Language: {locale}\\n"\n"Plural-Forms: {header}\\n"\n\n#: count\nmsgid "item"\nmsgid_plural "items"\n'
            catalog += "".join(
                f'msgstr[{i}] "{value}"\n' for i, value in enumerate(values)
            )
            output = self._convert_to_string(
                catalog, "en: {count: {one: item, other: items}}"
            )
            for value in values:
                assert f"{value}: {value}" in output

    def test_declared_french_plural_order(self) -> None:
        catalog = 'msgid ""\nmsgstr ""\n"Language: fr\\n"\n"Plural-Forms: nplurals=3; plural=n<=1 ? 2 : n%1000000==0 ? 0 : 1;\\n"\n\n#: count\nmsgid "item"\nmsgid_plural "items"\nmsgstr[0] "millions"\nmsgstr[1] "rest"\nmsgstr[2] "single"\n'
        output = self._convert_to_string(
            catalog, "en: {count: {one: item, other: items}}"
        )
        assert "many: millions" in output
        assert "other: rest" in output
        assert "one: single" in output

    def test_plural_import_uses_target_locale(self) -> None:
        catalog = '\n#: count\nmsgid "item"\nmsgid_plural "items"\nmsgstr[0] "single"\nmsgstr[1] "several"\nmsgstr[2] "rest"\n'
        for header, template_lang in [
            ("", "cs"),
            ('msgid ""\nmsgstr "Language: cs\\n"\n', "en"),
        ]:
            output = self._convert_to_string(
                header + catalog,
                f"{template_lang}: {{count: {{one: item, other: items}}}}",
            )
            assert "cs:" in output
            assert "one: single" in output
            assert "few: several" in output
            assert "other: rest" in output

    def test_ruby_roundtrip(self) -> None:
        """Check PO converts back to Ruby YAML with language root key."""
        input_string = """
#: greeting
msgid "Hello!"
msgstr "Hola!"

#: farewell
msgid "Goodbye!"
msgstr "Adéu!"
"""
        template_string = """en:
  greeting: Hello!
  farewell: Goodbye!
"""
        output = self._convert_to_string(input_string, template_string)
        assert "greeting: Hola!" in output
        assert "farewell: Adéu!" in output

    def test_keeps_float_and_date_values(self) -> None:
        input_string = """msgid ""
msgstr ""
"Language: fr\\n"

#: greeting
msgid "Hello!"
msgstr "Bonjour !"
"""
        template_string = """en:
  version: 2.1
  greeting: Hello!
  updated: 2026-01-15
"""
        expected_output = """fr:
  version: 2.1
  greeting: Bonjour !
  updated: 2026-01-15
"""
        assert expected_output == self._convert_to_string(input_string, template_string)

    def test_ruby_nested_roundtrip(self) -> None:
        """Check PO converts back to nested Ruby YAML."""
        input_string = """
#: messages->welcome
msgid "Welcome!"
msgstr "Benvingut!"

#: messages->error
msgid "Something went wrong"
msgstr "Alguna cosa ha anat malament"
"""
        template_string = """en:
  messages:
    welcome: Welcome!
    error: Something went wrong
"""
        output = self._convert_to_string(input_string, template_string)
        assert "welcome: Benvingut!" in output
        assert "error: Alguna cosa ha anat malament" in output


class TestPO2YAMLCommand(test_convert.TestConvertCommand, TestPO2YAML):
    """Tests running actual po2yaml commands on files."""

    convertmodule = po2yaml
    defaultoptions = {"progress": "none"}
    expected_options = [
        "-t TEMPLATE, --template=TEMPLATE",
        "--threshold=PERCENT",
        "--fuzzy",
        "--nofuzzy",
        "--personality=TYPE",
    ]

    @pytest.mark.parametrize("translation", ["", "Začít"])
    def test_duplicates_merge_roundtrip(self, translation) -> None:
        """Preserve every YAML key through merged POT extraction and PO import."""
        self.create_testfile(
            "en.yaml",
            """section1:
  tile1_button: Get Started
  tile2_button: Get Started
  tile3_button: Get Started
""",
        )
        yaml2po.main(
            [
                "--input",
                self.get_testfilename("en.yaml"),
                "--output",
                self.get_testfilename("messages.pot"),
                "--duplicates=merge",
                "--pot",
                "--progress=none",
            ]
        )
        with self.open_testfile("messages.pot") as pot_file:
            store = po.pofile(pot_file)
        units = [unit for unit in store.units if not unit.isheader()]
        assert len(units) == 1
        unit = units[0]
        locations = [f"section1->tile{i}_button" for i in range(1, 4)]
        assert unit.getlocations() == locations
        assert unit.source == "Get Started"
        assert unit.target == ""
        unit.target = translation
        with self.open_testfile("messages.po", "wb") as po_file:
            store.serialize(po_file)

        self.run_command(
            input="messages.po", output="translated.yaml", template="en.yaml"
        )

        with self.open_testfile("translated.yaml") as yaml_file:
            result = yaml.YAMLFile(yaml_file)
        assert len(result.units) == 3
        assert {unit.getid(): unit.source for unit in result.units} == dict.fromkeys(
            locations, translation or "Get Started"
        )
