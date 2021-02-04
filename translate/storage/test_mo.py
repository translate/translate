import os
import subprocess
import sys
from io import BytesIO

from translate.storage import factory, mo, test_base
from translate.tools import pocompile


class TestMOUnit(test_base.TestTranslationUnit):
    UnitClass = mo.mounit

    def test_context(self):
        unit = self.UnitClass("Message")
        unit.setcontext("context")
        assert unit.getcontext() == "context"


posources = [
    r"""
msgid ""
msgstr ""
"PO-Revision-Date: 2006-02-09 23:33+0200\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8-bit\n"
""",
    r"""
msgid ""
msgstr ""
"PO-Revision-Date: 2006-02-09 23:33+0200\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8-bit\n"

msgid "plant"
msgstr ""
""",
    # The following test is commented out, because the hash-size is different
    # compared to gettext, since we're not counting untranslated units.
    # r'''
    # msgid ""
    # msgstr ""
    # "PO-Revision-Date: 2006-02-09 23:33+0200\n"
    # "MIME-Version: 1.0\n"
    # "Content-Type: text/plain; charset=UTF-8\n"
    # "Content-Transfer-Encoding: 8-bit\n"
    #
    # msgid "plant"
    # msgstr ""
    #
    # msgid ""
    # "_: Noun\n"
    # "convert"
    # msgstr "bekeerling"
    #''',
    r"""
msgid ""
msgstr ""
"PO-Revision-Date: 2006-02-09 23:33+0200\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8-bit\n"

msgid "plant"
msgstr ""

msgid ""
"_: Noun\n"
"convert"
msgstr "bekeerling"

msgctxt "verb"
msgid ""
"convert"
msgstr "omskakel"
""",
    r"""
msgid ""
msgstr ""
"PO-Revision-Date: 2006-02-09 23:33+0200\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8-bit\n"

msgid "plant"
msgstr ""

msgid ""
"_: Noun\n"
"convert"
msgstr "bekeerling"

msgctxt "verb"
msgid ""
"convert"
msgstr "omskakel"

msgid "tree"
msgid_plural "trees"
msgstr[0] ""
""",
    r"""
msgid ""
msgstr ""
"PO-Revision-Date: 2020-12-23 22:11+0000\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"

msgid "Contains %d project"
msgstr "Obsahuje %d projekt"
""",
    r"""
msgid ""
msgstr ""
"POT-Creation-Date: 2020-12-25 09:38+0000\n"
"PO-Revision-Date: 2020-12-23 22:11+0000\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"

#: weblate/accounts/avatar.py:103
msgctxt "No known user"
msgid "None"
msgstr "Žádný"
""",
    r"""
msgid ""
msgstr ""
"PO-Revision-Date: 2020-12-23 22:11+0000\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Plural-Forms: nplurals=3; plural=(n==1) ? 0 : (n>=2 && n<=4) ? 1 : 2;\n"

#, python-format
msgid "%(count)s screenshot"
msgid_plural "%(count)s screenshots"
msgstr[0] "%(count)s obrázek"
msgstr[1] "%(count)s obrázky"
msgstr[2] "%(count)s obrázků"
""",
    r"""
msgid ""
msgstr ""
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"

msgid "0"
msgstr "0"

msgid "1"
msgstr "1"

msgid "2"
msgstr "2"

msgid "3"
msgstr "3"

msgid "4"
msgstr "4"

msgid "5"
msgstr "5"

msgid "6"
msgstr "6"

msgid "7"
msgstr "7"

msgid "8"
msgstr "8"

msgid "9"
msgstr "9"

msgid "10"
msgstr "10"

msgid "11"
msgstr "11"

msgid "12"
msgstr "12"

msgid "13"
msgstr "13"

msgid "14"
msgstr "14"

msgid "15"
msgstr "15"

msgid "16"
msgstr "16"

msgid "17"
msgstr "17"

msgid "18"
msgstr "18"

msgid "19"
msgstr "19"

msgid "20"
msgstr "20"

msgid "21"
msgstr "21"

msgid "22"
msgstr "22"

msgid "23"
msgstr "23"

msgid "24"
msgstr "24"

msgid "25"
msgstr "25"

msgid "26"
msgstr "26"

msgid "27"
msgstr "27"

msgid "28"
msgstr "28"

msgid "29"
msgstr "29"

msgid "30"
msgstr "30"

msgid "31"
msgstr "31"

msgid "32"
msgstr "32"

msgid "33"
msgstr "33"

msgid "34"
msgstr "34"

msgid "35"
msgstr "35"

msgid "36"
msgstr "36"

msgid "37"
msgstr "37"

msgid "38"
msgstr "38"

msgid "39"
msgstr "39"

msgid "40"
msgstr "40"

msgid "41"
msgstr "41"

msgid "42"
msgstr "42"

msgid "43"
msgstr "43"

msgid "44"
msgstr "44"

msgid "45"
msgstr "45"

msgid "46"
msgstr "46"

msgid "47"
msgstr "47"

msgid "48"
msgstr "48"

msgid "49"
msgstr "49"

msgid "50"
msgstr "50"

msgid "51"
msgstr "51"

msgid "52"
msgstr "52"

msgid "53"
msgstr "53"

msgid "54"
msgstr "54"

msgid "55"
msgstr "55"

msgid "56"
msgstr "56"

msgid "57"
msgstr "57"

msgid "58"
msgstr "58"

msgid "59"
msgstr "59"

msgid "60"
msgstr "60"

msgid "61"
msgstr "61"

msgid "62"
msgstr "62"

msgid "63"
msgstr "63"

msgid "64"
msgstr "64"

msgid "65"
msgstr "65"

msgid "66"
msgstr "66"

msgid "67"
msgstr "67"

msgid "68"
msgstr "68"

msgid "69"
msgstr "69"

msgid "70"
msgstr "70"

msgid "71"
msgstr "71"

msgid "72"
msgstr "72"

msgid "73"
msgstr "73"

msgid "74"
msgstr "74"

msgid "75"
msgstr "75"

msgid "76"
msgstr "76"

msgid "77"
msgstr "77"

msgid "78"
msgstr "78"

msgid "79"
msgstr "79"

msgid "80"
msgstr "80"

msgid "81"
msgstr "81"

msgid "82"
msgstr "82"

msgid "83"
msgstr "83"

msgid "84"
msgstr "84"

msgid "85"
msgstr "85"

msgid "86"
msgstr "86"

msgid "87"
msgstr "87"

msgid "88"
msgstr "88"

msgid "89"
msgstr "89"

msgid "90"
msgstr "90"

msgid "91"
msgstr "91"

msgid "92"
msgstr "92"

msgid "93"
msgstr "93"

msgid "94"
msgstr "94"

msgid "95"
msgstr "95"

msgid "96"
msgstr "96"

msgid "97"
msgstr "97"

msgid "98"
msgstr "98"

msgid "99"
msgstr "99"
""",
]


class TestMOFile(test_base.TestTranslationStore):
    StoreClass = mo.mofile

    def get_mo_and_po(self):
        return (
            os.path.abspath(self.filename + ".po"),
            os.path.abspath(self.filename + ".msgfmt.mo"),
            os.path.abspath(self.filename + ".pocompile.mo"),
        )

    def remove_po_and_mo(self):
        for file in self.get_mo_and_po():
            if os.path.exists(file):
                os.remove(file)

    def setup_method(self, method):
        super().setup_method(method)
        self.remove_po_and_mo()

    def teardown_method(self, method):
        super().teardown_method(method)
        self.remove_po_and_mo()

    def test_language(self):
        """Test that we can return the target language correctly."""
        store = self.StoreClass()
        store.updateheader(add=True, Language="zu")
        assert store.gettargetlanguage() == "zu"

    def test_context(self):
        store = self.StoreClass()
        unit = self.StoreClass.UnitClass("source")
        unit.target = "target"
        unit.setcontext("context")
        store.addunit(unit)
        assert b"context" in store.__bytes__()

        newstore = self.StoreClass.parsestring(store.__bytes__())
        assert len(newstore.units) == 1
        assert newstore.units[0].getcontext(), "context"

    def test_output(self):
        for posource in posources:
            print("PO source file")
            print(posource)
            if "POT-Creation-Date" in posource and os.name == "nt":
                # There is no Gettext 0.20 on Windows, so the output is different
                continue
            PO_FILE, MO_MSGFMT, MO_POCOMPILE = self.get_mo_and_po()
            posource = posource.encode("utf-8")

            with open(PO_FILE, "wb") as out_file:
                out_file.write(posource)

            subprocess.check_call(
                ["msgfmt", PO_FILE, "-o", MO_MSGFMT, "--endianness", sys.byteorder]
            )
            argv = sys.argv
            try:
                sys.argv = [
                    "pocompile",
                    "--errorlevel=traceback",
                    PO_FILE,
                    MO_POCOMPILE,
                ]
                pocompile.main()
            finally:
                sys.argv = argv

            store = factory.getobject(BytesIO(posource))
            if store.isempty() and not os.path.exists(MO_POCOMPILE):
                # pocompile doesn't create MO files for empty PO files, so we
                # can skip the checks here.
                continue

            with open(MO_MSGFMT, "rb") as mo_msgfmt_f:
                mo_msgfmt = mo_msgfmt_f.read()
            print("msgfmt output:")
            print(repr(mo_msgfmt))

            with open(MO_POCOMPILE, "rb") as mo_pocompile_f:
                mo_pocompile = mo_pocompile_f.read()
            print("pocompile output:")
            print(repr(mo_pocompile))

            assert mo_msgfmt == mo_pocompile
