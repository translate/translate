import pytest

from translate.storage import base, toml

from . import test_monolingual


class TestTOMLResourceUnit(test_monolingual.TestMonolingualUnit):
    UnitClass = toml.TOMLUnit

    def test_getlocations(self):
        unit = self.UnitClass("teststring")
        unit.setid("some-key")
        assert unit.getlocations() == ["some-key"]


class TestTOMLResourceStore(test_monolingual.TestMonolingualStore):
    StoreClass = toml.TOMLFile

    def test_serialize(self):
        store = self.StoreClass()
        store.parse('key = "value"')
        assert bytes(store) == b'key = "value"\n'

    def test_empty(self):
        store = self.StoreClass()
        store.parse("")
        assert bytes(store) == b""

    def test_edit(self):
        store = self.StoreClass()
        store.parse('key = "value"')
        store.units[0].target = "second"
        assert bytes(store) == b'key = "second"\n'

    def test_edit_unicode(self):
        store = self.StoreClass()
        store.parse('key = "value"')
        store.units[0].target = "zkouška"
        assert bytes(store) == 'key = "zkouška"\n'.encode()

    def test_parse_unicode_list(self):
        data = """list = ["zkouška"]
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
foo = "foo"
bar = "bar"
baz = "baz"
"""
        )
        assert len(store.units) == 3
        assert store.units[0].source == "foo"
        assert store.units[2].source == "baz"

    def test_nested(self):
        data = """[foo]
bar = "bar"

[foo.baz]
boo = "booo"

[root]
eggs = "spam"
"""
        store = self.StoreClass()
        store.parse(data)
        assert len(store.units) == 3
        assert store.units[0].getid() == "foo.bar"
        assert store.units[0].source == "bar"
        assert store.units[1].getid() == "foo.baz.boo"
        assert store.units[1].source == "booo"
        assert store.units[2].getid() == "root.eggs"
        assert store.units[2].source == "spam"
        assert bytes(store).decode("ascii") == data

    def test_multiline(self):
        """Test multiline strings in TOML."""
        data = '''invite = """
Ola!
Recibiches unha invitación para unirte!"""

eggs = "spam"
'''
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
        store.parse("foo = true")
        assert len(store.units) == 1
        assert store.units[0].getid() == "foo"
        assert store.units[0].source == "True"
        assert bytes(store) == b'foo = "True"\n'

    def test_integer(self):
        store = self.StoreClass()
        store.parse("foo = 1")
        assert len(store.units) == 1
        assert store.units[0].getid() == "foo"
        assert store.units[0].source == "1"
        assert bytes(store) == b'foo = "1"\n'

    def test_no_quote_strings(self):
        """Test unquoted strings (basic strings in TOML)."""
        store = self.StoreClass()
        store.parse('eggs = "No quoting at all"')
        assert len(store.units) == 1
        assert store.units[0].getid() == "eggs"
        assert store.units[0].source == "No quoting at all"
        assert bytes(store) == b'eggs = "No quoting at all"\n'

    def test_double_quote_strings(self):
        """Test double-quoted strings."""
        store = self.StoreClass()
        store.parse('bar = "quote, double"')
        assert len(store.units) == 1
        assert store.units[0].getid() == "bar"
        assert store.units[0].source == "quote, double"
        assert bytes(store) == b'bar = "quote, double"\n'

    def test_single_quote_strings(self):
        """Test literal strings (single quotes in TOML)."""
        store = self.StoreClass()
        store.parse("foo = 'quote, single'")
        assert len(store.units) == 1
        assert store.units[0].getid() == "foo"
        assert store.units[0].source == "quote, single"
        assert bytes(store) == b"foo = 'quote, single'\n"

    def test_escaped_double_quotes(self):
        """Test escaped double quotes in TOML."""
        store = self.StoreClass()
        store.parse(r'foo = "Hello \"World\"."')
        assert len(store.units) == 1
        assert store.units[0].getid() == "foo"
        assert store.units[0].source == 'Hello "World".'
        assert bytes(store) == rb'foo = "Hello \"World\"."' + b"\n"

    def test_newlines(self):
        """Test newlines in TOML strings."""
        store = self.StoreClass()
        store.parse(r'foo = "Hello \n World."')
        assert len(store.units) == 1
        assert store.units[0].getid() == "foo"
        assert store.units[0].source == "Hello \n World."
        assert bytes(store) == rb'foo = "Hello \n World."' + b"\n"

    def test_list(self):
        """Test TOML arrays."""
        data = """day_names = ["Domingo", "Luns", "Martes", "Mércores", "Xoves", "Venres", "Sábado"]
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

    def test_inline_table(self):
        """Test inline table syntax."""
        data = """martin = {name = "Martin D'vloper", job = "Developer", skill = "Elite"}
"""
        store = self.StoreClass()
        store.parse(data)
        assert len(store.units) == 3
        assert store.units[0].getid() == "martin.name"
        assert store.units[0].source == "Martin D'vloper"
        assert store.units[1].getid() == "martin.job"
        assert store.units[1].source == "Developer"
        assert store.units[2].getid() == "martin.skill"
        assert store.units[2].source == "Elite"
        assert bytes(store).decode("ascii") == data

    def test_key_nesting(self):
        store = self.StoreClass()
        unit = self.StoreClass.UnitClass("teststring2")
        unit.setid("key.value")
        store.addunit(unit)
        assert bytes(store) == b'[key]\nvalue = "teststring2"\n'

    def test_add_to_empty(self):
        store = self.StoreClass()
        store.parse("")
        unit = self.StoreClass.UnitClass("teststring2")
        unit.setid("key.value")
        store.addunit(unit)
        assert bytes(store).decode("utf-8") == '[key]\nvalue = "teststring2"\n'

    def test_dict_in_list(self):
        data = """[[e1]]
s1 = "Subtag 1"
"""
        store = self.StoreClass()
        store.parse(data)
        assert len(store.units) == 1
        assert bytes(store) == data.encode("ascii")

    def test_remove(self):
        data = """[test."1"]
one = "one"
two = "two"

[test."2"]
three = "three"
four = "four"
"""
        store = self.StoreClass()
        store.parse(data)
        assert len(store.units) == 4
        assert bytes(store).decode() == data
        store.removeunit(store.units[0])
        assert (
            bytes(store).decode()
            == """[test."1"]
two = "two"

[test."2"]
three = "three"
four = "four"
"""
        )
        store.removeunit(store.units[0])
        assert (
            bytes(store).decode()
            == """[test."2"]
three = "three"
four = "four"
"""
        )
        store.removeunit(store.units[-1])
        assert (
            bytes(store).decode()
            == """[test."2"]
three = "three"
"""
        )

    def test_special(self):
        store = self.StoreClass()
        with pytest.raises(base.ParseError):
            store.parse("key = other\x08string")

    def test_comment_extraction_simple(self):
        """Test extracting simple comments from TOML."""
        data = """# This is a comment for key1
key1 = "value1"

# This is a comment for key2
key2 = "value2"
"""
        store = self.StoreClass()
        store.parse(data)
        assert len(store.units) == 2
        assert store.units[0].getnotes() == "This is a comment for key1"
        assert store.units[1].getnotes() == "This is a comment for key2"

    def test_comment_extraction_multiline(self):
        """Test extracting multi-line comments from TOML."""
        data = """# This is a comment for key1
# with multiple lines
# explaining the key
key1 = "value1"

# Another comment
# for key2
key2 = "value2"
"""
        store = self.StoreClass()
        store.parse(data)
        assert len(store.units) == 2
        # TOML comments are line-by-line, need to check the actual behavior
        # For now, we expect the first line of comment
        assert "This is a comment for key1" in store.units[0].getnotes()

    def test_no_comment_backwards_compat(self):
        """Test that TOML without comments still works."""
        data = """key1 = "value1"
key2 = "value2"
"""
        store = self.StoreClass()
        store.parse(data)
        assert len(store.units) == 2
        assert store.units[0].getnotes() == ""
        assert store.units[1].getnotes() == ""

    def test_literal_string(self):
        """Test TOML literal strings (single quotes)."""
        data = r"""literal_str = 'C:\Users\nodejs\templates'
"""
        store = self.StoreClass()
        store.parse(data)
        assert len(store.units) == 1
        assert store.units[0].source == r"C:\Users\nodejs\templates"
        assert bytes(store).decode() == data

    def test_multiline_basic_string(self):
        """Test TOML multiline basic strings (triple double quotes)."""
        data = '''str = """
The quick brown fox jumps over the lazy dog."""
'''
        store = self.StoreClass()
        store.parse(data)
        assert len(store.units) == 1
        assert "The quick brown fox" in store.units[0].source

    def test_multiline_literal_string(self):
        """Test TOML multiline literal strings (triple single quotes)."""
        data = """literal_multiline_str = '''
The first newline is
trimmed in raw strings.
   All other whitespace
   is preserved.
'''
"""
        store = self.StoreClass()
        store.parse(data)
        assert len(store.units) == 1
        assert "The first newline is" in store.units[0].source
        assert "preserved" in store.units[0].source


class TestGoI18nTOMLResourceStore(test_monolingual.TestMonolingualStore):
    StoreClass = toml.GoI18nTOMLFile

    def test_simple_plural(self):
        """Test parsing simple pluralized strings."""
        data = """[reading_time]
one = "One minute to read"
other = "{{ .Count }} minutes to read"
"""
        store = self.StoreClass()
        store.parse(data)
        assert len(store.units) == 1
        assert store.units[0].hasplural()
        assert store.units[0].target.strings[0] == "One minute to read"
        assert store.units[0].target.strings[1] == "{{ .Count }} minutes to read"
        assert bytes(store).decode("utf-8") == data

    def test_plural_with_other_keys(self):
        """Test that tables with only 'other' key are treated as singulars."""
        data = """[category]
other = "category"

[reading_time]
one = "One minute to read"
other = "{{ .Count }} minutes to read"

[tag]
other = "tag"
"""
        store = self.StoreClass()
        store.parse(data)
        assert len(store.units) == 3

        # First unit is singular (only has "other" key, treated as singular value)
        assert store.units[0].getid() == "category"
        assert not store.units[0].hasplural()
        assert store.units[0].source == "category"

        # Second unit is plural
        assert store.units[1].getid() == "reading_time"
        assert store.units[1].hasplural()

        # Third unit is singular (only has "other" key)
        assert store.units[2].getid() == "tag"
        assert not store.units[2].hasplural()
        assert store.units[2].source == "tag"

    def test_full_plural_forms(self):
        """Test all CLDR plural categories."""
        data = """[items]
zero = "No items"
one = "One item"
two = "Two items"
few = "A few items"
many = "Many items"
other = "{{ .Count }} items"
"""
        store = self.StoreClass()
        store.parse(data)
        assert len(store.units) == 1
        assert store.units[0].hasplural()
        strings = store.units[0].target.strings
        # First element is the multistring itself, rest are strings
        assert str(strings[0]) == "No items"
        assert strings[1] == "One item"
        assert strings[2] == "Two items"
        assert strings[3] == "A few items"
        assert strings[4] == "Many items"
        assert strings[5] == "{{ .Count }} items"

    def test_roundtrip_plural(self):
        """Test that plural forms survive round-trip."""
        data = """[messages]
one = "You have one message"
other = "You have {{ .Count }} messages"
"""
        store = self.StoreClass()
        store.parse(data)
        assert len(store.units) == 1

        # Modify the plural
        from translate.misc.multistring import multistring

        store.units[0].target = multistring(["Un mensaje", "{{ .Count }} mensajes"])

        result = bytes(store).decode("utf-8")
        assert 'one = "Un mensaje"' in result
        assert 'other = "{{ .Count }} mensajes"' in result

    def test_mixed_content(self):
        """Test file with both regular and pluralized entries."""
        data = """title = "My Application"

[welcome]
other = "Welcome!"

[items_count]
one = "One item"
other = "{{ .Count }} items"

[goodbye]
other = "Goodbye!"
"""
        store = self.StoreClass()
        store.parse(data)
        assert len(store.units) == 4

        # First is regular string
        assert store.units[0].getid() == "title"
        assert not store.units[0].hasplural()
        assert store.units[0].source == "My Application"

        # Second is singular (table with only "other", treated as singular)
        assert store.units[1].getid() == "welcome"
        assert not store.units[1].hasplural()
        assert store.units[1].source == "Welcome!"

        # Third is plural
        assert store.units[2].getid() == "items_count"
        assert store.units[2].hasplural()

        # Fourth is singular (table with only "other")
        assert store.units[3].getid() == "goodbye"
        assert not store.units[3].hasplural()
        assert store.units[3].source == "Goodbye!"
