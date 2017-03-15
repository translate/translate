# -*- coding: utf-8 -*-

import sys
from io import BytesIO

import pytest

from translate.storage import yaml, test_monolingual, base


class TestYAMLResourceUnit(test_monolingual.TestMonolingualUnit):
    UnitClass = yaml.YAMLUnit


class TestYAMLResourceStore(test_monolingual.TestMonolingualStore):
    StoreClass = yaml.YAMLFile

    def test_serialize(self):
        store = yaml.YAMLFile()
        store.parse('key: value')
        out = BytesIO()
        store.serialize(out)

        assert out.getvalue() == b'key: value\n'

    def test_edit(self):
        store = yaml.YAMLFile()
        store.parse('key: value')

        store.units[0].settarget('second')

        out = BytesIO()
        store.serialize(out)

        assert out.getvalue() == b'key: second\n'

    def test_edit_unicode(self):
        store = yaml.YAMLFile()
        store.parse('key: value')

        store.units[0].settarget(u'zkouška')

        out = BytesIO()
        store.serialize(out)

        assert out.getvalue() == u'key: zkouška\n'.encode('utf-8')

    def test_parse_unicode_list(self):
        store = yaml.YAMLFile()
        store.parse(u'list:\n- zkouška')

        out = BytesIO()
        store.serialize(out)

        assert out.getvalue() == u'list:\n- zkouška\n'.encode('utf-8')

    def test_ordering(self):
        store = yaml.YAMLFile()
        store.parse('''
foo: foo
bar: bar
baz: baz
''')

        assert store.units[0].source == 'foo'
        assert store.units[2].source == 'baz'

    def test_nested(self):
        store = yaml.YAMLFile()
        store.parse('''
foo:
    bar: bar
    baz:
        boo: booo
''')

        assert store.units[0].getid() == 'foo / bar'
        assert store.units[0].source == 'bar'
        assert store.units[1].getid() == 'foo / baz / boo'
        assert store.units[1].source == 'booo'

        out = BytesIO()
        store.serialize(out)

        assert out.getvalue() == b'''foo:
  bar: bar
  baz:
    boo: booo
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
        store = yaml.RubyYAMLFile()
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
        store = yaml.RubyYAMLFile()
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
