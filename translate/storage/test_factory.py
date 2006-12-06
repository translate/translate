#!/usr/bin/env python
# -*- coding: utf-8 -*-

from translate.storage import factory
from translate.misc import wStringIO

def classname(filename):
    """returns the classname to ease testing"""
    classinstance = factory.getclass(filename)
    return str(classinstance.__name__).lower()

def givefile(filename, content):
    """returns a file dummy object with the given content"""
    file = wStringIO.StringIO(content)
    file.name = filename
    return file

class BaseTestFactory:
    def test_getclass(self):
        assert classname("file.po") == "pofile"
        assert classname("file.pot") == "pofile"
        assert classname("file.dtd.po") == "pofile"

        assert classname("file.tmx") == "tmxfile"
        assert classname("file.af.tmx") == "tmxfile"
        assert classname("file.tbx") == "tbxfile"
        assert classname("file.po.xliff") == "xlifffile"

        assert not classname("file.po") == "tmxfile"
        assert not classname("file.po") == "xlifffile"

    def test_getobject(self):
        """Tests that we get a valid object."""
        fileobj = givefile(self.filename, self.file_content)
        store = factory.getobject(fileobj)
        assert isinstance(store, self.expected_instance)
        assert str(store) == self.file_content

    def test_get_noname_object(self):
        """Tests that we get a valid object from a file object without a name."""
        fileobj = wStringIO.StringIO(self.file_content)
        assert not hasattr(fileobj, 'name')
        store = factory.getobject(fileobj)
        assert str(store) == self.file_content

class TestPOFactory(BaseTestFactory):
    expected_instance = factory.po.pofile
    filename = 'dummy.po'
    file_content = '''#: test.c\nmsgid "test"\nmsgstr "rest"\n'''

class TestXliffFactory(BaseTestFactory):
    expected_instance = factory.xliff.xlifffile
    filename = 'dummy.xliff'
    file_content = '''<?xml version="1.0" encoding="utf-8"?>
<xliff version="1.1" xmlns="urn:oasis:names:tc:xliff:document:1.1">
<file>
<body>
  <trans-unit restype="x-gettext-domain-header">
    <source>test</source>
    <target>rest</target>
  </trans-unit>
</body>
</file>
</xliff>'''

class TestPOXliffFactory(BaseTestFactory):
    expected_instance = factory.poxliff.PoXliffFile
    filename = 'dummy.xliff'
    file_content = '''<?xml version="1.0" encoding="utf-8"?>
<xliff version="1.1" xmlns="urn:oasis:names:tc:xliff:document:1.1">
<file datatype="po" original="file.po" source-language="en-US"><body><trans-unit approved="no" id="1" restype="x-gettext-domain-header" xml:space="preserve">
<source>MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
</source>
<target>MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
</target>
</trans-unit></body></file></xliff>'''
