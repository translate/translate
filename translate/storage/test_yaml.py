import pytest
import ruamel.yaml

from translate.storage import base, test_monolingual, yaml


class TestYAMLResourceUnit(test_monolingual.TestMonolingualUnit):
    UnitClass = yaml.YAMLUnit

    def test_getlocations(self):
        unit = self.UnitClass("teststring")
        unit.setid("some-key")
        assert unit.getlocations() == ["some-key"]


class TestYAMLResourceStore(test_monolingual.TestMonolingualStore):
    StoreClass = yaml.YAMLFile

    def test_serialize(self):
        store = self.StoreClass()
        store.parse("key: value")
        assert bytes(store) == b"key: value\n"

    def test_empty(self):
        store = self.StoreClass()
        store.parse("{}")
        assert bytes(store) == b"{}\n"

    def test_edit(self):
        store = self.StoreClass()
        store.parse("key: value")
        store.units[0].target = "second"
        assert bytes(store) == b"key: second\n"

    def test_edit_unicode(self):
        store = self.StoreClass()
        store.parse("key: value")
        store.units[0].target = "zkouška"
        assert bytes(store) == "key: zkouška\n".encode()

    def test_parse_unicode_list(self):
        data = """list:
- zkouška
"""
        store = self.StoreClass()
        store.parse(data)
        assert bytes(store).decode("utf-8") == data
        store.units[0].target = "změna"
        assert bytes(store).decode("utf-8") == data.replace("zkouška", "změna")

    def test_ordering(self):
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

    def test_initial_comments(self):
        data = """# Hello world.

foo: bar
"""
        store = self.StoreClass()
        store.parse(data)
        assert len(store.units) == 1
        assert store.units[0].getid() == "foo"
        assert store.units[0].source == "bar"
        assert bytes(store).decode("ascii") == data

    def test_string_key(self):
        data = """"yes": Oficina
"""
        store = self.StoreClass()
        store.parse(data)
        assert len(store.units) == 1
        assert store.units[0].getid() == "yes"
        assert store.units[0].source == "Oficina"
        assert bytes(store).decode("ascii") == data

    def test_nested(self):
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

    def test_multiline(self):
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

    def test_boolean(self):
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

    def test_integer(self):
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

    def test_no_quote_strings(self):
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

    def test_double_quote_strings(self):
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

    def test_single_quote_strings(self):
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

    def test_avoid_escaping_double_quote_strings(self):
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

    def test_avoid_escaping_single_quote_strings(self):
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

    def test_escaped_double_quotes(self):
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

    def test_newlines(self):
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

    def test_abbreviated_list(self):
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

    def test_abbreviated_dictionary(self):
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

    def test_key_nesting(self):
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

    def test_add_to_mepty(self):
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

    @pytest.mark.skipif(
        ruamel.yaml.version_info < (0, 16, 6),
        reason="Empty keys serialization broken in ruamel.yaml<0.16.6",
    )
    def test_empty_key(self):
        yaml_souce = b"""'': Jedna
foo:
  '': Dve
"""
        store = self.StoreClass()
        store.parse(yaml_souce)
        assert len(store.units) == 2
        assert store.units[0].getid() == ""
        assert store.units[0].source == "Jedna"
        assert store.units[1].getid() == "foo->"
        assert store.units[1].source == "Dve"
        assert bytes(store) == yaml_souce

    def test_dict_in_list(self):
        data = """e1:
- s1: Subtag 1
"""
        store = self.StoreClass()
        store.parse(data)
        assert len(store.units) == 1
        assert bytes(store) == data.encode("ascii")

    def test_dump_args(self):
        data = """e1:
- s1: Subtag 1
"""
        store = self.StoreClass()
        store.dump_args["line_break"] = "\r\n"
        store.parse(data)
        assert len(store.units) == 1
        assert bytes(store) == data.replace("\n", "\r\n").encode("ascii")

    def test_anchors(self):
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

    def test_tagged_scalar(self):
        store = self.StoreClass()
        store.parse("key: =")
        assert store.units[0].target == "="
        store.units[0].target = "second"
        assert bytes(store) == b"key: second\n"

    def test_numeric(self):
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

    def test_remove(self):
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

    def test_special(self):
        store = self.StoreClass()
        with pytest.raises(base.ParseError):
            store.parse("key: other\x08string")


class TestRubyYAMLResourceStore(test_monolingual.TestMonolingualStore):
    StoreClass = yaml.RubyYAMLFile

    def test_ruby_list(self):
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

    def test_ruby(self):
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

    @staticmethod
    def test_invalid_value():
        store = yaml.YAMLFile()
        with pytest.raises(base.ParseError):
            store.parse('val: "\\u string"')

    def test_ruby_plural(self):
        data = """en:
  message:
    one: There is one message
    other: There are %{count} messages
"""
        store = self.StoreClass()
        store.parse(data)
        assert len(store.units) == 1
        assert bytes(store) == data.encode("ascii")

    def test_empty(self):
        store = self.StoreClass()
        store.parse("{}")
        assert bytes(store) == b"{}\n"

    def test_anchors(self):
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

    def test_type_change(self):
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

    def test_add(self):
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
