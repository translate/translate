# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import sys
from io import BytesIO

import pytest

from translate.storage import yaml, test_monolingual, base


class TestYAMLResourceUnit(test_monolingual.TestMonolingualUnit):
    UnitClass = yaml.YAMLUnit

    def test_getlocations(self):
        unit = self.UnitClass("teststring")
        unit.setid('some-key')
        assert unit.getlocations() == ['some-key']


class TestYAMLResourceStore(test_monolingual.TestMonolingualStore):
    StoreClass = yaml.YAMLFile

    def test_serialize(self):
        store = self.StoreClass()
        store.parse('key: value')
        out = BytesIO()
        store.serialize(out)
        assert out.getvalue() == b'key: value\n'

    def test_edit(self):
        store = self.StoreClass()
        store.parse('key: value')
        store.units[0].settarget('second')
        out = BytesIO()
        store.serialize(out)
        assert out.getvalue() == b'key: second\n'

    def test_edit_unicode(self):
        store = self.StoreClass()
        store.parse('key: value')
        store.units[0].settarget('zkouška')
        out = BytesIO()
        store.serialize(out)
        assert out.getvalue() == 'key: zkouška\n'.encode('utf-8')

    def test_parse_unicode_list(self):
        store = self.StoreClass()
        store.parse('list:\n- zkouška')
        out = BytesIO()
        store.serialize(out)
        assert out.getvalue() == 'list:\n- zkouška\n'.encode('utf-8')

    def test_ordering(self):
        store = self.StoreClass()
        store.parse('''
foo: foo
bar: bar
baz: baz
''')
        assert len(store.units) == 3
        assert store.units[0].source == 'foo'
        assert store.units[2].source == 'baz'

    def test_initial_comments(self):
        store = self.StoreClass()
        store.parse('''
# Hello world.

foo: bar
''')
        assert len(store.units) == 1
        assert store.units[0].getid() == 'foo'
        assert store.units[0].source == 'bar'
        out = BytesIO()
        store.serialize(out)
        assert out.getvalue() == b'''foo: bar
'''

    def test_string_key(self):
        store = self.StoreClass()
        store.parse('''
"yes": Oficina
''')
        assert len(store.units) == 1
        assert store.units[0].getid() == 'yes'
        assert store.units[0].source == 'Oficina'
        out = BytesIO()
        store.serialize(out)
        assert out.getvalue() == b''''yes': Oficina
'''

    def test_nested(self):
        store = self.StoreClass()
        store.parse('''
foo:
    bar: bar
    baz:
        boo: booo


eggs: spam
''')
        assert len(store.units) == 3
        assert store.units[0].getid() == 'foo->bar'
        assert store.units[0].source == 'bar'
        assert store.units[1].getid() == 'foo->baz->boo'
        assert store.units[1].source == 'booo'
        assert store.units[2].getid() == 'eggs'
        assert store.units[2].source == 'spam'
        out = BytesIO()
        store.serialize(out)
        assert out.getvalue() == b'''foo:
  bar: bar
  baz:
    boo: booo
eggs: spam
'''

    @pytest.mark.xfail(reason="Not Implemented")
    def test_multiline(self):
        """These are used in Discourse and Diaspora* translation."""
        store = self.StoreClass()
        store.parse('''
invite: |-
        Ola!
        Recibiches unha invitación para unirte!


eggs: spam
''')
        assert len(store.units) == 2
        assert store.units[0].getid() == 'invite'
        assert store.units[0].source == """Ola!
        Recibiches unha invitación para unirte a!"""
        assert store.units[1].getid() == 'eggs'
        assert store.units[1].source == 'spam'
        out = BytesIO()
        store.serialize(out)
        assert out.getvalue() == '''invite: |-
        Ola!
        Recibiches unha invitación para unirte!
eggs: spam
'''

    @pytest.mark.xfail(reason="Not Implemented")
    def test_boolean(self):
        store = self.StoreClass()
        store.parse('''
foo: True
''')
        assert len(store.units) == 1
        assert store.units[0].getid() == 'foo'
        assert store.units[0].source == 'True'
        out = BytesIO()
        store.serialize(out)
        assert out.getvalue() == b'''foo: True
'''

    def test_no_quote_strings(self):
        """These are used in OpenStreeMap translation."""
        store = self.StoreClass()
        store.parse('''
eggs: No quoting at all
''')
        assert len(store.units) == 1
        assert store.units[0].getid() == 'eggs'
        assert store.units[0].source == 'No quoting at all'
        out = BytesIO()
        store.serialize(out)
        assert out.getvalue() == b'''eggs: No quoting at all
'''

    @pytest.mark.xfail(reason="Not Implemented")
    def test_double_quote_strings(self):
        """These are used in OpenStreeMap translation."""
        store = self.StoreClass()
        store.parse('''
bar: "quote, double"
''')
        assert len(store.units) == 1
        assert store.units[0].getid() == 'bar'
        assert store.units[0].source == 'quote, double'
        out = BytesIO()
        store.serialize(out)
        assert out.getvalue() == b'''bar: "quote, double"
'''

    @pytest.mark.xfail(reason="Not Implemented")
    def test_single_quote_strings(self):
        """These are used in OpenStreeMap translation."""
        store = self.StoreClass()
        store.parse('''
foo: 'quote, single'
''')
        assert len(store.units) == 1
        assert store.units[0].getid() == 'foo'
        assert store.units[0].source == 'quote, single'
        out = BytesIO()
        store.serialize(out)
        assert out.getvalue() == b'''foo: 'quote, single'
'''

    @pytest.mark.xfail(reason="Not Implemented")
    def test_avoid_escaping_double_quote_strings(self):
        """These are used in OpenStreeMap translation."""
        store = self.StoreClass()
        store.parse('''
spam: 'avoid escaping "double quote"'
''')
        assert len(store.units) == 1
        assert store.units[0].getid() == 'spam'
        assert store.units[0].source == 'avoid escaping "double quote"'
        out = BytesIO()
        store.serialize(out)
        assert out.getvalue() == b'''spam: 'avoid escaping "double quote"'
'''

    @pytest.mark.xfail(reason="Not Implemented")
    def test_avoid_escaping_single_quote_strings(self):
        """Test avoid escaping single quotes."""
        store = self.StoreClass()
        store.parse('''
spam: "avoid escaping 'single quote'"
''')
        assert len(store.units) == 1
        assert store.units[0].getid() == 'spam'
        assert store.units[0].source == "avoid escaping 'single quote'"
        out = BytesIO()
        store.serialize(out)
        assert out.getvalue() == b'''spam: "avoid escaping 'single quote'"
'''

    @pytest.mark.xfail(reason="Not Implemented")
    def test_escaped_double_quotes(self):
        """These are used in OpenStreeMap translation."""
        store = self.StoreClass()
        store.parse('''
foo: "Hello \"World\"."
''')
        assert len(store.units) == 1
        assert store.units[0].getid() == 'foo'
        assert store.units[0].source == 'Hello "World"'
        out = BytesIO()
        store.serialize(out)
        assert out.getvalue() == b'''foo: "Hello \"World\"."
'''

    @pytest.mark.xfail(reason="Not Implemented")
    def test_escaped_single_quotes(self):
        """Test escaping single quotes."""
        store = self.StoreClass()
        store.parse('''
foo: 'Hello \'World\'.'
''')
        assert len(store.units) == 1
        assert store.units[0].getid() == 'foo'
        assert store.units[0].source == "Hello 'World'"
        out = BytesIO()
        store.serialize(out)
        assert out.getvalue() == b'''foo: 'Hello \'World\'.'
'''

    @pytest.mark.xfail(reason="Not Implemented")
    def test_newlines(self):
        """These are used in OpenStreeMap translation."""
        store = self.StoreClass()
        store.parse('''
foo: "Hello \n World."
''')
        assert len(store.units) == 1
        assert store.units[0].getid() == 'foo'
        assert store.units[0].source == 'Hello \n World'
        out = BytesIO()
        store.serialize(out)
        assert out.getvalue() == b'''foo: "Hello \n World."
'''

    @pytest.mark.xfail(reason="Not Implemented")
    def test_abbreviated_list(self):
        """These are used in Redmine and Discourse translation."""
        store = self.StoreClass()
        store.parse('''
day_names:        [Domingo, Luns, Martes, Mércores, Xoves, Venres, Sábado]
''')
        assert len(store.units) == 7
        assert store.units[0].getid() == 'day_names->[0]'
        assert store.units[0].source == 'Domingo'
        assert store.units[1].getid() == 'day_names->[1]'
        assert store.units[1].source == 'Luns'
        assert store.units[2].getid() == 'day_names->[2]'
        assert store.units[2].source == 'Martes'
        assert store.units[3].getid() == 'day_names->[3]'
        assert store.units[3].source == 'Mércores'
        assert store.units[4].getid() == 'day_names->[4]'
        assert store.units[4].source == 'Xoves'
        assert store.units[5].getid() == 'day_names->[5]'
        assert store.units[5].source == 'Venres'
        assert store.units[6].getid() == 'day_names->[6]'
        assert store.units[6].source == 'Sábado'
        out = BytesIO()
        store.serialize(out)
        assert out.getvalue() == '''day_names: [Domingo, Luns, Martes, Mércores, Xoves, Venres, Sábado]
'''

    @pytest.mark.xfail(reason="Not Implemented")
    def test_abbreviated_dictionary(self):
        """Test abbreviated dictionary syntax."""
        store = self.StoreClass()
        store.parse('''
martin: {name: Martin D'vloper, job: Developer, skill: Elite}
''')
        assert len(store.units) == 3
        assert store.units[0].getid() == 'martin->name'
        assert store.units[0].source == "Martin D'vloper"
        assert store.units[1].getid() == 'martin->job'
        assert store.units[1].source == 'Developer'
        assert store.units[2].getid() == 'martin->skill'
        assert store.units[2].source == 'Elite'
        out = BytesIO()
        store.serialize(out)
        assert out.getvalue() == '''martin: {name: Martin D'vloper, job: Developer, skill: Elite}
'''

    def test_key_nesting(self):
        store = self.StoreClass()
        unit = self.StoreClass.UnitClass("teststring")
        unit.setid('key')
        store.addunit(unit)
        unit = self.StoreClass.UnitClass("teststring2")
        unit.setid('key->value')
        store.addunit(unit)
        out = BytesIO()
        store.serialize(out)
        assert out.getvalue() == b'''key:
  value: teststring2
'''


class TestRubyYAMLResourceStore(test_monolingual.TestMonolingualStore):
    StoreClass = yaml.RubyYAMLFile

    def test_ruby_list(self):
        data = '''en-US:
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
'''
        store = self.StoreClass()
        store.parse(data)
        out = BytesIO()
        store.serialize(out)
        assert out.getvalue() == data.encode('ascii')

    def test_ruby(self):
        data = '''en:
  language_name: English
  language_name_english: English
  message:
    unsubscribe: Unsubscribe from our emails
    from_app: from %{app_name}
'''
        store = self.StoreClass()
        store.parse(data)
        out = BytesIO()
        store.serialize(out)
        assert out.getvalue() == data.encode('ascii')

    def test_invalid_key(self):
        store = yaml.YAMLFile()
        with pytest.raises(base.ParseError):
            store.parse('yes: string')

    def test_invalid_value(self):
        store = yaml.YAMLFile()
        with pytest.raises(base.ParseError):
            store.parse('val: "\\u string"')
