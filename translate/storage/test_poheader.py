import os
import time
from collections import OrderedDict
from io import BytesIO

from translate.storage import po, poheader, poxliff


def test_parseheaderstring():
    """test for the header parsing function"""
    source = r"""item1: one
item2: two:two
this item must get ignored because there is no colon sign in it
item3: three
"""
    d = poheader.parseheaderstring(source)
    print(type(d))
    assert len(d) == 3
    assert d["item1"] == "one"
    assert d["item2"] == "two:two"
    assert d["item3"] == "three"


def test_update():
    """test the update function"""
    # do we really add nothing if add==False ?
    d = poheader.update({}, test="hello")
    assert len(d) == 0
    # do we add if add==True ?
    d = poheader.update({}, add=True, Test="hello")
    assert len(d) == 1
    assert d["Test"] == "hello"
    # do we really update ?
    d = poheader.update({"Test": "hello"}, add=True, Test="World")
    assert len(d) == 1
    assert d["Test"] == "World"
    # does key rewrite work ?
    d = poheader.update({}, add=True, test_me="hello")
    assert d["Test-Me"] == "hello"
    # is the order correct ?
    d = OrderedDict()
    d["Project-Id-Version"] = "abc"
    d["POT-Creation-Date"] = "now"
    d = poheader.update(d, add=True, Test="hello", Report_Msgid_Bugs_To="bugs@list.org")
    assert list(d.keys()) == [
        "Project-Id-Version",
        "Report-Msgid-Bugs-To",
        "POT-Creation-Date",
        "Test",
    ]


def poparse(posource):
    """helper that parses po source without requiring files"""
    dummyfile = BytesIO(posource.encode())
    return po.pofile(dummyfile)


def poxliffparse(posource):
    """helper that parses po source into poxliffFile"""
    poxli = poxliff.PoXliffFile()
    poxli.parse(posource)
    return poxli


def check_po_date(datestring):
    """Check the validity of a PO date.

    The datestring must be in the format: 2007-06-08 10:08+0200
    """

    # We don't include the timezone offset as part of our format,
    # because time.strptime() does not recognize %z
    # The use of %z is deprecated in any case.
    date_format = "%Y-%m-%d %H:%M"

    # Get the timezone offset (last 4 digits):
    tz = datestring[-4:]
    assert type(int(tz)) is int

    # Strip the timezone from the string, typically something like "+0200".
    # This is to make the datestring conform to the specified format,
    # we can't add %z to the format.
    datestring = datestring[0:-5]

    # Check that the date can be parsed
    assert type(time.strptime(datestring, date_format)) is time.struct_time


def test_po_dates():
    pofile = po.pofile()
    headerdict = pofile.makeheaderdict(po_revision_date=True)
    check_po_date(headerdict["POT-Creation-Date"])
    check_po_date(headerdict["PO-Revision-Date"])

    headerdict = pofile.makeheaderdict(
        pot_creation_date=time.localtime(), po_revision_date=time.localtime()
    )
    check_po_date(headerdict["POT-Creation-Date"])
    check_po_date(headerdict["PO-Revision-Date"])


def test_timezones():
    # The following will only work on Unix because of tzset() and %z
    if "tzset" in time.__dict__:
        os.environ["TZ"] = "Asia/Kabul"
        time.tzset()
        assert time.timezone == -16200
        # Typically "+0430"
        assert poheader.tzstring() == time.strftime("%z")

        os.environ["TZ"] = "Asia/Seoul"
        time.tzset()
        assert time.timezone == -32400
        # Typically "+0900"
        assert poheader.tzstring() == time.strftime("%z")

        os.environ["TZ"] = "Africa/Johannesburg"
        time.tzset()
        assert time.timezone == -7200
        # Typically "+0200"
        assert poheader.tzstring() == time.strftime("%z")

        os.environ["TZ"] = "UTC"
        time.tzset()
        assert time.timezone == 0
        # Typically "+0000"
        assert poheader.tzstring() == time.strftime("%z")


def test_header_blank():
    """test header functionality"""

    def compare(pofile):
        print(pofile)
        assert len(pofile.units) == 1
        header = pofile.header()
        assert header.isheader()
        assert not header.isblank()

        headeritems = pofile.parseheader()
        assert headeritems["Project-Id-Version"] == "PACKAGE VERSION"
        assert headeritems["Report-Msgid-Bugs-To"] == ""
        check_po_date(headeritems["POT-Creation-Date"])
        assert headeritems["PO-Revision-Date"] == "YEAR-MO-DA HO:MI+ZONE"
        assert headeritems["Last-Translator"] == "FULL NAME <EMAIL@ADDRESS>"
        assert headeritems["Language-Team"] == "LANGUAGE <LL@li.org>"
        assert headeritems["MIME-Version"] == "1.0"
        assert headeritems["Content-Type"] == "text/plain; charset=UTF-8"
        assert headeritems["Content-Transfer-Encoding"] == "8bit"
        assert headeritems["Plural-Forms"] == "nplurals=INTEGER; plural=EXPRESSION;"

    posource = r"""# other comment\n
msgid ""
msgstr ""
"Project-Id-Version: PACKAGE VERSION\n"
"Report-Msgid-Bugs-To: \n"
"POT-Creation-Date: 2006-03-08 17:30+0200\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\n"
"Language-Team: LANGUAGE <LL@li.org>\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Plural-Forms: nplurals=INTEGER; plural=EXPRESSION;\n"
"""
    pofile = poparse(posource)
    compare(pofile)


## TODO: enable this code if PoXliffFile is able to parse a header
##
##    poxliffsource = r'''<?xml version="1.0" encoding="utf-8"?>
##<xliff version="1.1" xmlns="urn:oasis:names:tc:xliff:document:1.1">
##
##<file datatype="po" original="test.po" source-language="en-US"><body><trans-unit approved="no" id="1" restype="x-gettext-domain-header" xml:space="preserve"><source>Project-Id-Version: PACKAGE VERSION
##Report-Msgid-Bugs-To:
##POT-Creation-Date: 2006-03-08 17:30+0200
##PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE
##Last-Translator: FULL NAME <ph id="1">&lt;EMAIL@ADDRESS&gt;</ph>
##Language-Team: LANGUAGE <ph id="2">&lt;LL@li.org&gt;</ph>
##MIME-Version: 1.0
##Content-Type: text/plain; charset=UTF-8
##Content-Transfer-Encoding: 8bit
##Plural-Forms: nplurals=INTEGER; plural=EXPRESSION;
##</source><target>Project-Id-Version: PACKAGE VERSION
##Report-Msgid-Bugs-To:
##POT-Creation-Date: 2006-03-08 17:30+0200
##PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE
##Last-Translator: FULL NAME <ph id="1">&lt;EMAIL@ADDRESS&gt;</ph>
##Language-Team: LANGUAGE <ph id="2">&lt;LL@li.org&gt;</ph>
##MIME-Version: 1.0
##Content-Type: text/plain; charset=UTF-8
##Content-Transfer-Encoding: 8bit
##Plural-Forms: nplurals=INTEGER; plural=EXPRESSION;
##</target><context-group name="po-entry" purpose="information"><context context-type="x-po-trancomment">other comment\n</context></context-group><note from="po-translator">other comment\n</note></trans-unit></body></file></xliff>
##'''
##    pofile = poparse(poxliffsource)
##    compare(pofile)


def test_plural_equation():
    """
    test that we work with the equation even is the last semicolon is left out, since gettext
    tools don't seem to mind
    """
    posource = r"""msgid ""
msgstr ""
"Plural-Forms: nplurals=2; plural=(n != 1)%s\n"
"""
    for colon in ("", ";"):
        pofile = poparse(posource % colon)
        print(pofile)
        assert len(pofile.units) == 1
        header = pofile.units[0]
        assert header.isheader()
        assert not header.isblank()

        pofile.parseheader()
        nplural, plural = pofile.getheaderplural()
        assert nplural == "2"
        assert plural == "(n != 1)"


##    TODO: add the same test for PoXliffFile


def test_plural_equation_across_lines():
    """test that we work if the plural equation spans more than one line"""
    posource = r"""msgid ""
msgstr ""
"Plural-Forms:  nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%"
"10<=4 && (n%100<10 || n%100>=20) ? 1 : 2);\n"
"""
    pofile = poparse(posource)
    print(pofile)
    assert len(pofile.units) == 1
    header = pofile.units[0]
    assert header.isheader()
    assert not header.isblank()

    pofile.parseheader()
    nplural, plural = pofile.getheaderplural()
    assert nplural == "3"
    assert (
        plural
        == "(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2)"
    )


##    TODO: add the same test for PoXliffFile


def test_updatecontributor():
    """Test that we can update contributor information in the header comments."""
    posource = r"""msgid ""
msgstr ""
"MIME-Version: 1.0"
"""
    pofile = poparse(posource)
    pofile.updatecontributor("Grasvreter")
    assert "# Grasvreter, 20" in bytes(pofile).decode("utf-8")

    pofile.updatecontributor("Koeivreter", "monster@grasveld.moe")
    assert "# Koeivreter <monster@grasveld.moe>, 20" in bytes(pofile).decode("utf-8")

    pofile.header().addnote("Khaled Hosny <khaledhosny@domain.org>, 2006, 2007, 2008.")
    pofile.updatecontributor("Khaled Hosny", "khaledhosny@domain.org")
    print(bytes(pofile))
    assert (
        "# Khaled Hosny <khaledhosny@domain.org>, 2006, 2007, 2008, %s."
        % time.strftime("%Y")
        in bytes(pofile).decode("utf-8")
    )


def test_updatecontributor_header():
    """Test preserving empty lines in comments"""
    posource = r"""# Japanese translation of ibus.
# Copyright (C) 2015-2019 Takao Fujiwara <takao.fujiwara1@gmail.com>
# This file is distributed under the same license as the ibus package.
#
# Translators:
# Takao Fujiwara <takao.fujiwara1@gmail.com>, 2012
msgid ""
msgstr ""
"MIME-Version: 1.0"
"""
    pofile = poparse(posource)

    # Add contributor
    pofile.updatecontributor("Grasvreter")

    # Manually build expected output
    expected = posource.replace(
        "msgid", "# Grasvreter, %s.\nmsgid" % time.strftime("%Y")
    )
    assert bytes(pofile).decode("utf-8") == expected


def test_language():
    """Test that we can get a language from the relevant headers."""
    posource = r"""msgid ""
msgstr ""
"MIME-Version: 1.0\n"
"""

    pofile = poparse(posource)
    assert pofile.gettargetlanguage() is None

    posource += '"Language-Team: translate-discuss-af@lists.sourceforge.net\\n"\n'
    pofile = poparse(posource)
    assert pofile.gettargetlanguage() == "af"

    posource += '"X-Poedit-Language: German\\n"\n'
    pofile = poparse(posource)
    assert pofile.gettargetlanguage() == "de"

    posource += '"Language: fr_CA\\n"\n'
    pofile = poparse(posource)
    assert pofile.gettargetlanguage() == "fr_CA"


def test_project():
    """Test that we can get a project from the relevant headers."""
    posource = r"""msgid ""
msgstr ""
"MIME-Version: 1.0\n"
"""

    pofile = poparse(posource)
    assert pofile.getprojectstyle() is None

    posource += '"X-Accelerator-Marker: ~\\n"\n'
    pofile = poparse(posource)
    assert pofile.getprojectstyle() == "openoffice"

    posource += '"Report-Msgid-Bugs-To: http://bugzilla.gnome.org/enter_bug.cgi?product=system-\\n"\n'
    pofile = poparse(posource)
    assert pofile.getprojectstyle() == "gnome"

    posource += '"X-Project-Style: drupal\\n"\n'
    pofile = poparse(posource)
    assert pofile.getprojectstyle() == "drupal"

    pofile.setprojectstyle("kde")
    assert pofile.getprojectstyle() == "kde"

    pofile.setprojectstyle("complete-rubbish")
    assert pofile.getprojectstyle() == "complete-rubbish"
