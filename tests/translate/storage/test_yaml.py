import pytest
from ruamel.yaml.comments import CommentedMap

from translate.misc.multistring import multistring
from translate.storage import base, jsonl10n, yaml

from . import test_monolingual


class TestYAMLResourceUnit(test_monolingual.TestMonolingualUnit):
    UnitClass = yaml.YAMLUnit

    def test_getlocations(self) -> None:
        unit = self.UnitClass("teststring")
        unit.setid("some-key")
        assert unit.getlocations() == ["some-key"]


class TestYAMLResourceStore(test_monolingual.TestMonolingualStore):
    StoreClass = yaml.YAMLFile

    @staticmethod
    def alias_chain(depth: int, leaf: str = "value") -> str:
        return f"a0: &a0 [{leaf}]\n" + "".join(
            f"a{index}: &a{index} [*a{index - 1}, *a{index - 1}]\n"
            for index in range(1, depth + 1)
        )

    def test_alias_unit_limit(self) -> None:
        store = self.StoreClass(max_yaml_nodes=None, max_yaml_units=10)
        with pytest.raises(base.ParseError, match="10 unit extraction limit"):
            store.parse(self.alias_chain(6))

    def test_default_alias_limit(self) -> None:
        with pytest.raises(base.ParseError, match="extraction limit"):
            self.StoreClass(self.alias_chain(16))

    def test_alias_node_limit_without_units(self) -> None:
        store = self.StoreClass(max_yaml_nodes=10, max_yaml_units=None)
        with pytest.raises(base.ParseError, match="10 node extraction limit"):
            store.parse(self.alias_chain(6, leaf=""))

    def test_alias_limits_can_be_disabled(self) -> None:
        store = self.StoreClass(
            self.alias_chain(4), max_yaml_nodes=None, max_yaml_units=None
        )
        assert len(store.units) == 31

    def test_cyclic_collection(self) -> None:
        store = self.StoreClass()
        data = CommentedMap()
        data["loop"] = [data]
        with pytest.raises(base.ParseError, match="cyclic collection"):
            list(store._flatten(data))

    def test_serialize(self) -> None:
        store = self.StoreClass()
        store.parse("key: value")
        assert bytes(store) == b"key: value\n"

    def test_empty(self) -> None:
        store = self.StoreClass()
        store.parse("{}")
        assert bytes(store) == b"{}\n"

    def test_edit(self) -> None:
        store = self.StoreClass()
        store.parse("key: value")
        store.units[0].target = "second"
        assert bytes(store) == b"key: second\n"

    def test_edit_unicode(self) -> None:
        store = self.StoreClass()
        store.parse("key: value")
        store.units[0].target = "zkouška"
        assert bytes(store) == "key: zkouška\n".encode()

    def test_parse_unicode_list(self) -> None:
        data = """list:
- zkouška
"""
        store = self.StoreClass()
        store.parse(data)
        assert bytes(store).decode("utf-8") == data
        store.units[0].target = "změna"
        assert bytes(store).decode("utf-8") == data.replace("zkouška", "změna")

    def test_ordering(self) -> None:
        store = self.StoreClass()
        store.parse(
            """
foo: foo
bar: bar
baz: baz
"""
        )
        assert len(store.units) == 3
        assert store.units[0].source == "foo"
        assert store.units[2].source == "baz"

    def test_initial_comments(self) -> None:
        data = """# Hello world.

foo: bar
"""
        store = self.StoreClass()
        store.parse(data)
        assert len(store.units) == 1
        assert store.units[0].getid() == "foo"
        assert store.units[0].source == "bar"
        assert bytes(store).decode("ascii") == data

    def test_string_key(self) -> None:
        data = """"yes": Oficina
"""
        store = self.StoreClass()
        store.parse(data)
        assert len(store.units) == 1
        assert store.units[0].getid() == "yes"
        assert store.units[0].source == "Oficina"
        assert bytes(store).decode("ascii") == data

    def test_nested(self) -> None:
        data = """foo:
  bar: bar
  baz:
    boo: booo


eggs: spam
"""
        store = self.StoreClass()
        store.parse(data)
        assert len(store.units) == 3
        assert store.units[0].getid() == "foo->bar"
        assert store.units[0].source == "bar"
        assert store.units[1].getid() == "foo->baz->boo"
        assert store.units[1].source == "booo"
        assert store.units[2].getid() == "eggs"
        assert store.units[2].source == "spam"
        assert bytes(store).decode("ascii") == data

    def test_multiline(self) -> None:
        """These are used in Discourse and Diaspora* translation."""
        data = """invite: |-
  Ola!
  Recibiches unha invitación para unirte!


eggs: spam
"""
        store = self.StoreClass()
        store.parse(data)
        assert len(store.units) == 2
        assert store.units[0].getid() == "invite"
        assert (
            store.units[0].source
            == """Ola!
Recibiches unha invitación para unirte!"""
        )
        assert store.units[1].getid() == "eggs"
        assert store.units[1].source == "spam"
        assert bytes(store).decode("utf-8") == data

    def test_boolean(self) -> None:
        store = self.StoreClass()
        store.parse(
            """
foo: True
"""
        )
        assert len(store.units) == 1
        assert store.units[0].getid() == "foo"
        assert store.units[0].source == "True"
        assert (
            bytes(store)
            == b"""foo: 'True'
"""
        )

    def test_integer(self) -> None:
        store = self.StoreClass()
        store.parse(
            """
foo: 1
"""
        )
        assert len(store.units) == 1
        assert store.units[0].getid() == "foo"
        assert store.units[0].source == "1"
        assert (
            bytes(store)
            == b"""foo: '1'
"""
        )

    def test_no_quote_strings(self) -> None:
        """These are used in OpenStreeMap translation."""
        store = self.StoreClass()
        store.parse(
            """
eggs: No quoting at all
"""
        )
        assert len(store.units) == 1
        assert store.units[0].getid() == "eggs"
        assert store.units[0].source == "No quoting at all"
        assert (
            bytes(store)
            == b"""eggs: No quoting at all
"""
        )

    def test_double_quote_strings(self) -> None:
        """These are used in OpenStreeMap translation."""
        store = self.StoreClass()
        store.parse(
            """
bar: "quote, double"
"""
        )
        assert len(store.units) == 1
        assert store.units[0].getid() == "bar"
        assert store.units[0].source == "quote, double"
        assert (
            bytes(store)
            == b"""bar: "quote, double"
"""
        )

    def test_single_quote_strings(self) -> None:
        """These are used in OpenStreeMap translation."""
        store = self.StoreClass()
        store.parse(
            """
foo: 'quote, single'
"""
        )
        assert len(store.units) == 1
        assert store.units[0].getid() == "foo"
        assert store.units[0].source == "quote, single"
        assert (
            bytes(store)
            == b"""foo: 'quote, single'
"""
        )

    def test_avoid_escaping_double_quote_strings(self) -> None:
        """These are used in OpenStreeMap translation."""
        store = self.StoreClass()
        store.parse(
            """
spam: 'avoid escaping "double quote"'
"""
        )
        assert len(store.units) == 1
        assert store.units[0].getid() == "spam"
        assert store.units[0].source == 'avoid escaping "double quote"'
        assert (
            bytes(store)
            == b"""spam: 'avoid escaping "double quote"'
"""
        )

    def test_avoid_escaping_single_quote_strings(self) -> None:
        """Test avoid escaping single quotes."""
        store = self.StoreClass()
        store.parse(
            """
spam: "avoid escaping 'single quote'"
"""
        )
        assert len(store.units) == 1
        assert store.units[0].getid() == "spam"
        assert store.units[0].source == "avoid escaping 'single quote'"
        assert (
            bytes(store)
            == b"""spam: "avoid escaping 'single quote'"
"""
        )

    def test_escaped_double_quotes(self) -> None:
        """These are used in OpenStreeMap translation."""
        store = self.StoreClass()
        store.parse(
            r"""
foo: "Hello \"World\"."
"""
        )
        assert len(store.units) == 1
        assert store.units[0].getid() == "foo"
        assert store.units[0].source == 'Hello "World".'
        assert (
            bytes(store)
            == rb"""foo: "Hello \"World\"."
"""
        )

    def test_newlines(self) -> None:
        """These are used in OpenStreeMap translation."""
        store = self.StoreClass()
        store.parse(
            r"""
foo: "Hello \n World."
"""
        )
        assert len(store.units) == 1
        assert store.units[0].getid() == "foo"
        assert store.units[0].source == "Hello \n World."
        assert (
            bytes(store)
            == rb"""foo: "Hello \n World."
"""
        )

    def test_abbreviated_list(self) -> None:
        """These are used in Redmine and Discourse translation."""
        data = """day_names: [Domingo, Luns, Martes, Mércores, Xoves, Venres, Sábado]
"""
        store = self.StoreClass()
        store.parse(data)
        assert len(store.units) == 7
        assert store.units[0].getid() == "day_names->[0]"
        assert store.units[0].source == "Domingo"
        assert store.units[1].getid() == "day_names->[1]"
        assert store.units[1].source == "Luns"
        assert store.units[2].getid() == "day_names->[2]"
        assert store.units[2].source == "Martes"
        assert store.units[3].getid() == "day_names->[3]"
        assert store.units[3].source == "Mércores"
        assert store.units[4].getid() == "day_names->[4]"
        assert store.units[4].source == "Xoves"
        assert store.units[5].getid() == "day_names->[5]"
        assert store.units[5].source == "Venres"
        assert store.units[6].getid() == "day_names->[6]"
        assert store.units[6].source == "Sábado"
        assert bytes(store).decode("utf-8") == data

    def test_abbreviated_dictionary(self) -> None:
        """Test abbreviated dictionary syntax."""
        data = """martin: {name: Martin D'vloper, job: Developer, skill: Elite}
"""
        store = self.StoreClass()
        store.parse(data)
        assert len(store.units) == 3
        assert store.units[0].getid() == "martin->name"
        assert store.units[0].source == "Martin D'vloper"
        assert store.units[1].getid() == "martin->job"
        assert store.units[1].source == "Developer"
        assert store.units[2].getid() == "martin->skill"
        assert store.units[2].source == "Elite"
        assert bytes(store).decode("ascii") == data

    def test_key_nesting(self) -> None:
        store = self.StoreClass()
        unit = self.StoreClass.UnitClass("teststring")
        unit.setid("key")
        store.addunit(unit)
        unit = self.StoreClass.UnitClass("teststring2")
        unit.setid("key->value")
        store.addunit(unit)
        assert (
            bytes(store)
            == b"""key:
  value: teststring2
"""
        )

    def test_add_to_mepty(self) -> None:
        store = self.StoreClass()
        store.parse("")
        unit = self.StoreClass.UnitClass("teststring")
        unit.setid("key")
        store.addunit(unit)
        unit = self.StoreClass.UnitClass("teststring2")
        unit.setid("key->value")
        store.addunit(unit)
        assert (
            bytes(store).decode("utf-8")
            == """key:
  value: teststring2
"""
        )

    def test_empty_key(self) -> None:
        yaml_source = b"""'': Jedna
foo:
  '': Dve
"""
        store = self.StoreClass()
        store.parse(yaml_source)
        assert len(store.units) == 2
        assert store.units[0].getid() == ""
        assert store.units[0].source == "Jedna"
        assert store.units[1].getid() == "foo->"
        assert store.units[1].source == "Dve"
        assert bytes(store) == yaml_source

    def test_dict_in_list(self) -> None:
        data = """e1:
- s1: Subtag 1
"""
        store = self.StoreClass()
        store.parse(data)
        assert len(store.units) == 1
        assert bytes(store) == data.encode("ascii")

    def test_dump_args(self) -> None:
        data = """e1:
- s1: Subtag 1
"""
        store = self.StoreClass()
        store.dump_args["line_break"] = "\r\n"  # ty:ignore[invalid-assignment]
        store.parse(data)
        assert len(store.units) == 1
        assert bytes(store) == data.replace("\n", "\r\n").encode("ascii")

    def test_anchors(self) -> None:
        data = """location: &location_attributes
  title: Location
  temporary_question: Temporary?
  temporary: Temporary
location_batch:
  <<: *location_attributes
  label: Label
  prefix: Prefix
"""
        store = self.StoreClass()
        store.parse(data)
        assert len(store.units) == 5
        assert bytes(store).decode("ascii") == data

    def test_tagged_scalar(self) -> None:
        store = self.StoreClass()
        store.parse("key: =")
        assert store.units[0].target == "="
        store.units[0].target = "second"
        assert bytes(store) == b"key: second\n"

    def test_numeric(self) -> None:
        data = """error:
  404: Not found
  server: Server error
"""
        store = self.StoreClass()
        store.parse(data)
        assert len(store.units) == 2
        assert bytes(store).decode() == data
        store.units[0].target = "Missing"
        assert (
            bytes(store).decode()
            == """error:
  404: Missing
  server: Server error
"""
        )

    def test_remove(self) -> None:
        data = """test:
  1:
    one: one
    two: two
  2:
    three: three
    four: four
"""
        store = self.StoreClass()
        store.parse(data)
        assert len(store.units) == 4
        assert bytes(store).decode() == data
        store.removeunit(store.units[0])
        assert (
            bytes(store).decode()
            == """test:
  1:
    two: two
  2:
    three: three
    four: four
"""
        )
        store.removeunit(store.units[0])
        assert (
            bytes(store).decode()
            == """test:
  2:
    three: three
    four: four
"""
        )
        store.removeunit(store.units[-1])
        assert (
            bytes(store).decode()
            == """test:
  2:
    three: three
"""
        )

    def test_special(self) -> None:
        store = self.StoreClass()
        with pytest.raises(base.ParseError):
            store.parse("key: other\x08string")

    def test_deep_nesting(self) -> None:
        content = "root:\n" + "\n".join(
            f"{'  ' * (level + 1)}-" for level in range(512)
        )
        content = f"{content} value\n"

        with pytest.raises(base.ParseError):
            self.StoreClass().parse(content)

    def test_quotes_roundtrip(self) -> None:
        data = """locales:
  quoted: "Quoted"
  plain: Plain
  single: 'Single'
"""
        store = self.StoreClass()
        store.parse(data)
        assert len(store.units) == 3
        assert bytes(store).decode() == data
        store.units[0].target = "Changed"
        assert bytes(store).decode() == data.replace("Quoted", "Changed")

    def test_comment_extraction_simple(self) -> None:
        """Test extracting simple comments from YAML."""
        data = """# This is a comment for key1
key1: value1

# This is a comment for key2
key2: value2
"""
        store = self.StoreClass()
        store.parse(data)
        assert len(store.units) == 2
        assert store.units[0].getnotes() == "This is a comment for key1"
        assert store.units[1].getnotes() == "This is a comment for key2"

    def test_comment_extraction_multiline(self) -> None:
        """Test extracting multi-line comments from YAML."""
        data = """# This is a comment for key1
# with multiple lines
# explaining the key
key1: value1

# Another comment
# for key2
key2: value2
"""
        store = self.StoreClass()
        store.parse(data)
        assert len(store.units) == 2
        expected_note1 = (
            "This is a comment for key1\nwith multiple lines\nexplaining the key"
        )
        assert store.units[0].getnotes() == expected_note1
        expected_note2 = "Another comment\nfor key2"
        assert store.units[1].getnotes() == expected_note2

    def test_comment_extraction_nested(self) -> None:
        """Test extracting comments from nested structures."""
        data = """# Comment for parent
parent:
  # Comment for child
  child: value
"""
        store = self.StoreClass()
        store.parse(data)
        assert len(store.units) == 1
        assert store.units[0].getid() == "parent->child"
        assert store.units[0].getnotes() == "Comment for child"

    def test_comment_extraction_mixed(self) -> None:
        """Test YAML with some keys having comments and some not."""
        data = """# Comment for key1
key1: value1

key2: value2

# Comment for key3
key3: value3
"""
        store = self.StoreClass()
        store.parse(data)
        assert len(store.units) == 3
        assert store.units[0].getnotes() == "Comment for key1"
        assert store.units[1].getnotes() == ""
        assert store.units[2].getnotes() == "Comment for key3"

    def test_no_comment_backwards_compat(self) -> None:
        """Test that YAML without comments still works."""
        data = """key1: value1
key2: value2
"""
        store = self.StoreClass()
        store.parse(data)
        assert len(store.units) == 2
        assert store.units[0].getnotes() == ""
        assert store.units[1].getnotes() == ""

    def test_sibling_keys_are_indexed_once(self) -> None:
        """Comment extraction should not scan all sibling keys per value."""

        class CountingCommentedMap(CommentedMap):
            def __init__(self, *args, **kwargs) -> None:
                self.keys_calls = 0
                super().__init__(*args, **kwargs)

            def keys(self):
                self.keys_calls += 1
                return super().keys()

        data = CountingCommentedMap(
            (f"key_{index}", f"value_{index}") for index in range(10)
        )

        list(self.StoreClass()._flatten(data))

        assert data.keys_calls == 1

    def test_multiline_literal_format(self) -> None:
        """Test that multiline strings use literal format (|) for better readability."""
        # Test 1: New file with multiline content
        store = self.StoreClass()
        store.parse("")
        unit = self.StoreClass.UnitClass("")
        unit.setid("example_code")
        store.addunit(unit)
        unit.target = "Line 1\nLine 2\nLine 3"
        result = bytes(store).decode()
        # Should use | format, not quoted with \n
        assert "|-" in result or "|" in result
        assert "Line 1\\n" not in result

        # Test 2: Editing existing | format preserves it
        original = """example_code: |
  Original line 1
  Original line 2
"""
        store2 = self.StoreClass()
        store2.parse(original)
        store2.units[0].target = "New line 1\nNew line 2"
        result2 = bytes(store2).decode()
        assert "|-" in result2 or "|" in result2
        assert "New line 1\\n" not in result2

        # Test 3: Quoted strings preserve their format
        quoted = r"""key: "Text\nwith\nescapes"
"""
        store3 = self.StoreClass()
        store3.parse(quoted)
        store3.units[0].target = "New\ntext"
        result3 = bytes(store3).decode()
        # Should stay quoted
        assert '"' in result3
        assert "New\\n" in result3

        # Test 4: LiteralScalarString preserved even without newlines
        literal_single = """key: |
  Single line
"""
        store4 = self.StoreClass()
        store4.parse(literal_single)
        store4.units[0].target = "Different single line"
        result4 = bytes(store4).decode()
        # Should preserve literal format even though new value has no newlines
        assert "|-" in result4 or "|" in result4
        assert "Different single line" in result4


class TestRubyYAMLResourceStore(test_monolingual.TestMonolingualStore):
    StoreClass = yaml.RubyYAMLFile

    @pytest.mark.parametrize("edited", [0, 1])
    def test_edit_aliased_plural(self, edited) -> None:
        data = b"en:\n  first: &items\n    one: |-\n      original\n    other: items\n  second: *items\n"
        store = self.StoreClass()
        store.parse(data)
        assert bytes(store) == data
        store.units[edited].update_plural_forms({"one": "line 1\nline 2"})
        result = bytes(store)
        assert result.count(b"one: |-") == 2
        parsed = self.StoreClass()
        parsed.parse(result)
        assert parsed.units[edited].plural_forms["one"] == "line 1\nline 2"
        assert parsed.units[1 - edited].plural_forms["one"] == "original"
        assert bytes(parsed) == result

    @pytest.mark.parametrize("positional", [False, True])
    def test_delete_inherited_plural(self, positional) -> None:
        data = b"en:\n  defaults: &base {one: item, other: items}\n  message:\n    <<: *base\n"
        store = self.StoreClass()
        store.parse(data)
        assert bytes(store) == data
        unit = store.units[1]
        if positional:
            unit.target = multistring(["item"])
        else:
            unit.update_plural_forms({"other": None})
        parsed = self.StoreClass()
        parsed.parse(bytes(store))
        assert parsed.units[0].plural_forms == {"one": "item", "other": "items"}
        assert parsed.units[1].plural_forms == {"one": "item"}

    def test_project_nonempty_fractional_form(self) -> None:
        store = self.StoreClass()
        data = b"cs: {message: {other: '', many: fraction}}\n"
        store.parse(data)
        unit = store.units[0]
        assert str(unit.target) == "fraction"
        assert unit.plural_forms == {"other": "", "many": "fraction"}
        assert bytes(store) == data

    @pytest.mark.parametrize("reassign", [False, True])
    def test_append_to_sparse_projection(self, reassign) -> None:
        store = self.StoreClass()
        store.parse("en: {message: {one: item}}")
        unit = store.units[0]
        unit.target.extra_strings.append("items")
        if reassign:
            unit.target = unit.target
        parsed = self.StoreClass()
        parsed.parse(bytes(store))
        assert parsed.units[0].plural_forms == {"one": "item", "other": "items"}

    def test_bind_detached_append(self) -> None:
        store = self.StoreClass()
        store.parse("cs: {k: {one: one}}")
        unit = store.units[0].copy()
        unit.target.extra_strings.append("few")
        destination = self.StoreClass()
        destination.settargetlanguage("en")
        destination.addunit(unit)
        assert unit.plural_forms == {"one": "one", "few": "few"}

    def test_rich_edit_after_append(self) -> None:
        store = self.StoreClass()
        store.parse("en: {k: {other: items}}")
        unit = store.units[0]
        assert len(unit.rich_target) == 1
        unit.target.extra_strings.append("item")
        unit.rich_target = unit.rich_target
        assert unit.plural_forms == {"other": "items", "one": "item"}

    def test_replace_nonplural_mapping(self) -> None:
        store = self.StoreClass()
        store.parse("en:\n  message: {old: null}\n")
        unit = store.UnitClass(multistring(["one", "other"]))
        unit.setid("message")
        store.addunit(unit)
        parsed = self.StoreClass()
        parsed.parse(bytes(store))
        assert len(parsed.units) == 1
        assert parsed.units[0].plural_forms == {"one": "one", "other": "other"}

    def test_merge_foreign_plural_categories(self) -> None:
        store = self.StoreClass()
        store.settargetlanguage("cs")
        store.parse("cs: {k: {one: '1', many: fraction, other: '5'}}")
        unit = store.units[0]
        donor = jsonl10n.I18NextV4File()
        donor.settargetlanguage("cs")
        donor.parse('{"k_one":"single","k_few":"several","k_other":"rest"}')
        unit.merge(donor.units[0], overwrite=True)
        assert unit.plural_forms == {"one": "single", "few": "several", "other": "rest"}
        assert (
            type(store).parsestring(bytes(store)).units[0].plural_forms
            == unit.plural_forms
        )

    def test_foreign_scalar_merge(self) -> None:
        store = self.StoreClass()
        store.parse("en: {k: {one: one, other: rest}}")
        unit = store.units[0]
        donor = base.TranslationUnit()
        donor.target = "replacement"
        store.settargetlanguage("cs")
        unit.merge(donor, overwrite=True)
        assert unit.plural_forms["other"] == "replacement"
        unit.rich_target = unit.rich_target
        assert unit.plural_forms["other"] == "replacement"

    def test_named_forms(self) -> None:
        store = self.StoreClass()
        data = """cs:
  days:
    many: fraction  # keep
    few:
    other: ''
"""
        store.parse(data)
        unit = store.units[0]
        assert unit.plural_forms == {"many": "fraction", "other": ""}
        assert bytes(store).decode() == data
        unit.update_plural_forms({"one": "new"})
        unit.update_plural_forms({"other": None})
        with pytest.raises(ValueError):
            unit.plural_forms = {}
        result = bytes(store)
        assert b"    few:\n" in result
        assert b"# keep" in result
        reparsed = self.StoreClass()
        reparsed.parse(result)
        assert reparsed.units[0].plural_forms == {"many": "fraction", "one": "new"}

    def test_alias_node_limit(self) -> None:
        store = self.StoreClass(max_yaml_nodes=10, max_yaml_units=None)
        data = "en:\n" + "".join(
            f"  a{index}: &a{index} [*a{index - 1}, *a{index - 1}]\n"
            if index
            else "  a0: &a0 []\n"
            for index in range(6)
        )
        with pytest.raises(base.ParseError, match="10 node extraction limit"):
            store.parse(data)

    def test_ruby_list(self) -> None:
        data = """en-US:
  date:
    formats:
      default: '%Y-%m-%d'
      short: '%b %d'
      long: '%B %d, %Y'
    day_names:
    - Sunday
    - Monday
    - Tuesday
    - Wednesday
    - Thursday
    - Friday
    - Saturday
"""
        store = self.StoreClass()
        store.parse(data)
        assert bytes(store).decode("ascii") == data

    def test_ruby(self) -> None:
        data = """en:
  language_name: English
  language_name_english: English
  message:
    unsubscribe: Unsubscribe from our emails
    from_app: from %{app_name}
"""
        store = self.StoreClass()
        store.parse(data)
        assert bytes(store) == data.encode("ascii")

    def test_plural_tags_only_resolved_for_plural_mappings(self, monkeypatch) -> None:
        store = self.StoreClass()
        get_plural_tags = store.get_plural_tags
        get_plural_tags_calls = 0

        def counting_get_plural_tags(target=None):
            nonlocal get_plural_tags_calls
            get_plural_tags_calls += 1
            return get_plural_tags(target)

        monkeypatch.setattr(store, "get_plural_tags", counting_get_plural_tags)
        data = "en:\n" + "".join(
            f"  group_{index}:\n    message: Value {index}\n" for index in range(100)
        )

        store.parse(data)

        assert len(store.units) == 100
        assert get_plural_tags_calls == 0

    def test_ruby_wrong(self) -> None:
        data = """no_data: No data
"""
        store = self.StoreClass()
        store.parse(data)
        assert bytes(store) == data.encode("ascii")

    def test_invalid_value(self) -> None:
        store = yaml.YAMLFile()
        with pytest.raises(base.ParseError):
            store.parse('val: "\\u string"')

    def test_ruby_plural(self) -> None:
        data = """en:
  message:
    one: There is one message
    other: There are %{count} messages
"""
        store = self.StoreClass()
        store.parse(data)
        assert len(store.units) == 1
        assert store.units[0].target == multistring(
            ["There is one message", "There are %{count} messages"]
        )
        assert bytes(store) == data.encode("ascii")

    def test_empty(self) -> None:
        store = self.StoreClass()
        store.parse("{}")
        assert bytes(store) == b"{}\n"

    def test_anchors(self) -> None:
        data = """en:
  location: &location_attributes
    title: Location
    temporary_question: Temporary?
    temporary: Temporary
  location_batch:
    <<: *location_attributes
    label: Label
    prefix: Prefix
"""
        store = self.StoreClass()
        store.parse(data)
        assert len(store.units) == 5
        assert bytes(store).decode("ascii") == data

    def test_type_change(self) -> None:
        original = """en:
  days_on: '["Sunday", "Monday"]'
"""
        changed = """en:
  days_on:
  - Sunday
  - Monday
"""
        store = self.StoreClass()
        store.parse(original)
        update = self.StoreClass()
        update.parse(changed)
        for unit in update.units:
            store.addunit(unit)
        assert bytes(store).decode("ascii") == changed

    def test_add(self) -> None:
        original = """en:
"""
        changed = """en:
  days_on:
  - Sunday
  - Monday
"""
        store = self.StoreClass()
        store.parse(original)
        unit = self.StoreClass.UnitClass("Sunday")
        unit.setid("days_on[0]")
        store.addunit(unit)
        unit = self.StoreClass.UnitClass("Monday")
        unit.setid("days_on[1]")
        store.addunit(unit)
        assert bytes(store).decode("ascii") == changed

    def test_ruby_plural_blank(self) -> None:
        data = """en:
  string:
  message:
    one:
    other:
"""
        store = self.StoreClass()
        store.parse(data)
        assert len(store.units) == 0
        assert bytes(store).decode() == data

    def test_ruby_plural_partial(self) -> None:
        data = """en:
  string:
  message:
    one: hello
    other:
"""
        store = self.StoreClass()
        store.parse(data)
        assert store.units[0].target == multistring(["hello", ""])
        assert len(store.units) == 1
        assert bytes(store).decode() == data

    def test_ruby_plural_pt_br(self) -> None:
        data = """pt_br:
  string:
  message:
    one: hello1
    many: hello2
    other: hello3
"""
        store = self.StoreClass()
        store.parse(data)
        assert store.units[0].target == multistring(["hello1", "hello2", "hello3"])
        assert len(store.units) == 1
        assert bytes(store).decode() == data

    def test_bug_ruby_remove_zero_few_and_mix_others(self) -> None:
        data = """en:
  string:
  message:
    one: value 1
    other: value 2
    zero: value 3
    few: value 4
"""
        store = self.StoreClass()
        store.parse(data)
        assert len(store.units) == 1
        assert store.units[0].target == multistring(["value 1", "value 2"])
        assert bytes(store).decode() == data
