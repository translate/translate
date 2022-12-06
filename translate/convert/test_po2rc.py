from translate.convert import po2rc, test_convert
from translate.storage.rc import rcfile


RC_SOURCE = r"""
#include "other_file.h" // This must be ignored

LANGUAGE LANG_ENGLISH, SUBLANG_DEFAULT

/////////////////////////////////////////////////////////////////////////////
//
// Dialog
//

IDD_REGGHC_DIALOG DIALOGEX 0, 0, 211, 191
STYLE DS_SETFONT | DS_MODALFRAME | DS_FIXEDSYS | WS_POPUP | WS_VISIBLE | WS_CAPTION | WS_SYSMENU
EXSTYLE WS_EX_APPWINDOW
CAPTION "License dialog"
FONT 8, "MS Shell Dlg", 0, 0, 0x1
BEGIN
    PUSHBUTTON      "Help",ID_HELP,99,162,48,15
    PUSHBUTTON      "Close",IDCANCEL,151,162,48,15
    PUSHBUTTON      "Activate instalation",IDC_BUTTON1,74,76,76,18
    CTEXT           "My very" " good program",IDC_STATIC1,56,21,109,19,SS_SUNKEN
    CTEXT           "You can use it without registering it",IDC_STATIC,35,131,128,19,SS_SUNKEN
    PUSHBUTTON      "Offline",IDC_OFFLINE,149,108,42,13
    PUSHBUTTON      "See license",IDC_LICENCIA,10,162,85,15
    RTEXT           "If you don't have internet, please use magic.",IDC_STATIC,23,105,120,18
    ICON            IDR_MAINFRAME,IDC_STATIC,44,74,20,20
    CTEXT           "Use your finger to activate the program.",IDC_ACTIVADA,17,50,175,17
    ICON            IDR_MAINFRAME1,IDC_STATIC6,18,19,20,20
END

MainMenu MENU
{
    POPUP "&Debug"
    {
        MENUITEM "&Memory usage", ID_MEMORY
        POPUP
        {
            MENUITEM SEPARATOR
            MENUITEM "&Walk data heap", ID_WALK_HEAP
        }
    }
}

STRINGTABLE
BEGIN
ID_T_1 "Hello"
END
"""

POFILE = """
#: DIALOGEX.IDD_REGGHC_DIALOG.CAPTION
msgid "License dialog"
msgstr "Licenční dialog"

#: DIALOGEX.IDD_REGGHC_DIALOG.CTEXT.IDC_STATIC1
msgid "My very good program"
msgstr "Mój bardzo dobry program"
"""


class TestPO2RCCommand(test_convert.TestConvertCommand):
    """Tests running actual po2rc commands on files"""

    convertmodule = po2rc
    defaultoptions = {"progress": "none"}
    expected_options = [
        "-t TEMPLATE, --template=TEMPLATE",
        "-l LANG, --lang=LANG",
        "--charset=CHARSET",
        "--sublang=SUBLANG",
        "--threshold=PERCENT",
        "--fuzzy",
        "--nofuzzy",
    ]

    def test_convert(self):
        """Tests the conversion to a po file"""
        self.create_testfile("simple.rc", RC_SOURCE)
        self.create_testfile("simple.po", POFILE)
        self.run_command(
            template="simple.rc", i="simple.po", o="output.rc", l="LANG_CZECH"
        )
        with self.open_testfile("output.rc") as handle:
            rc_result = rcfile(handle)
        assert len(rc_result.units) == 14
        assert rc_result.units[0].target == "Licenční dialog"
        assert rc_result.units[4].target == "Mój bardzo dobry program"

    def test_convert_comment(self):
        self.create_testfile(
            "simple.rc",
            """
STRINGTABLE
BEGIN
    // IDS_COMMENTED        "Comment"
    IDS_COPIED              "Copied"
    IDS_ADJACENT_STRINGS    "Line1 "
                            "Line2"
    IDS_UNTRANSLATED_STRING "This string has no translation. "
                            "It will appear verbatim in the output"
END
""",
        )
        self.create_testfile(
            "simple.po",
            """
#: STRINGTABLE.IDS_COPIED
msgid "Copied"
msgstr "Zkopirovano"
#: STRINGTABLE.IDS_ADJACENT_STRINGS
msgid ""
"Line1 "
"Line2"
msgstr ""
"Čára1 "
"Čára2"
""",
        )
        self.run_command(
            template="simple.rc", i="simple.po", o="output.rc", l="LANG_CZECH"
        )
        with self.open_testfile("output.rc") as handle:
            rc_result = rcfile(handle)
        assert len(rc_result.units) == 3
        assert rc_result.units[0].target == "Zkopirovano"
        assert rc_result.units[1].target == "Čára1 Čára2"
        assert (
            rc_result.units[2].target
            == "This string has no translation. It will appear verbatim in the output"
        )

    def test_convert_comment_dos_eol(self):
        self.create_testfile(
            "simple.rc",
            b"""\r\nSTRINGTABLE\r\nBEGIN\r\n// Comment\r\nIDS_1 "Copied"\r\nEND\r\n""",
        )
        self.create_testfile(
            "simple.po",
            """
#: STRINGTABLE.IDS_1
msgid "Copied"
msgstr "Zkopirovano"
""",
        )
        self.run_command(
            template="simple.rc", i="simple.po", o="output.rc", l="LANG_CZECH"
        )
        with self.open_testfile("output.rc", "rb") as handle:
            content = handle.read()
            assert (
                content
                == b"""\r\nSTRINGTABLE\r\nBEGIN\r\n    // Comment\r\n    IDS_1                   "Zkopirovano"\r\nEND\r\n"""
            )
        with self.open_testfile("output.rc") as handle:
            rc_result = rcfile(handle)
        assert len(rc_result.units) == 1
        assert rc_result.units[0].target == "Zkopirovano"

    def test_convert_double_string(self):
        self.create_testfile(
            "simple.rc",
            """
STRINGTABLE
BEGIN
    IDS_COPIED              "Copied"
    IDS_XCOPIED             "Copied"
END
""",
        )
        self.create_testfile(
            "simple.po",
            """
#: STRINGTABLE.IDS_COPIED
msgid "Copied"
msgstr "Zkopirovano"
""",
        )
        self.run_command(
            template="simple.rc", i="simple.po", o="output.rc", l="LANG_CZECH"
        )
        with self.open_testfile("output.rc") as handle:
            rc_result = rcfile(handle)
        assert len(rc_result.units) == 2
        assert rc_result.units[0].target == "Zkopirovano"
        assert rc_result.units[1].target == "Copied"

    def test_convert_popup(self):
        self.create_testfile(
            "simple.rc",
            """
IDR_MAINFRAME MENU
BEGIN
   POPUP "&File"
   BEGIN
       MENUITEM "&New\tCrtl+N",                ID_FILE_NEW
       MENUITEM "&Open...\tCtrl+O",            ID_FILE_OPEN
       MENUITEM "&Exit",                       ID_FILE_CLOSE
   END
   POPUP "&View"
   BEGIN
       MENUITEM "&Toolbar",                    ID_VIEW_STATUS_BAR
   END
   POPUP "&Help"
   BEGIN
       MENUITEM "&About...",                   ID_APP_ABOUT
   END
END
""",
        )
        self.create_testfile(
            "simple.po",
            """
#: MENU.IDR_MAINFRAME.POPUP.CAPTION
msgid "&Help"
msgstr "&Pomoc"
""",
        )
        self.run_command(
            template="simple.rc", i="simple.po", o="output.rc", l="LANG_CZECH"
        )
        with self.open_testfile("output.rc") as handle:
            rc_result = rcfile(handle)
        assert len(rc_result.units) == 8
        assert rc_result.units[0].target == "&File"
        assert rc_result.units[6].target == "&Pomoc"

    def test_convert_discardable(self):
        self.create_testfile(
            "simple.rc",
            """
STRINGTABLE DISCARDABLE
BEGIN

IDS_MSG1 "Hello, world!\\n"
IDS_MSG2 "Orangutan has %d banana.\\n"
IDS_MSG3 "Try Weblate at https://demo.weblate.org/!\\n"
IDS_MSG4 "Thank you for using Weblate."
END
""",
        )
        self.create_testfile(
            "simple.po",
            """
msgid "Hello, world!\\n"
msgstr "Nazdar, světe!\\n"
""",
        )
        self.run_command(
            template="simple.rc",
            i="simple.po",
            o="output.rc",
            l="LANG_CZECH",
            errorlevel="exception",
        )
        with self.open_testfile("output.rc") as handle:
            rc_result = rcfile(handle)
        assert len(rc_result.units) == 4
        assert rc_result.units[0].target == "Nazdar, světe!\n"

    def test_convert_menuex(self):
        rc_source = """
LANGUAGE LANG_ENGLISH, SUBLANG_ENGLISH_US

IDM_STARTMENU MENUEX
BEGIN
    POPUP ""
    BEGIN
        MENUITEM "", -1, MFT_SEPARATOR
        POPUP "&Programs", IDM_PROGRAMS
        BEGIN
            MENUITEM "(Empty)", -1, MFT_STRING, MFS_GRAYED
        END
        MENUITEM "Sh&ut Down...", IDM_SHUTDOWN, MFT_STRING, MFS_ENABLED
    END
END
"""
        self.create_testfile("simple.rc", rc_source)
        self.create_testfile(
            "simple.po",
            """
#: MENUEX.IDM_STARTMENU..MENUITEM.-1
msgid "(Empty)"
msgstr ""

#: MENUEX.IDM_STARTMENU.MENUITEM.IDM_SHUTDOWN
msgid "Sh&ut Down..."
msgstr "Vypnout..."
""",
        )
        self.run_command(
            template="simple.rc",
            i="simple.po",
            o="output.rc",
            l="LANG_CZECH",
            errorlevel="exception",
        )
        with self.open_testfile("output.rc") as handle:
            # Ignore whitespace changes (newlines are platform dependant)
            assert [line.strip() for line in handle.read().decode().splitlines()] == [
                line.strip()
                for line in rc_source.replace("Sh&ut Down...", "Vypnout...")
                .replace(
                    "LANG_ENGLISH, SUBLANG_ENGLISH_US", "LANG_CZECH, SUBLANG_DEFAULT"
                )
                .splitlines()
            ]
        with self.open_testfile("output.rc") as handle:
            rc_result = rcfile(handle)
        assert len(rc_result.units) == 4
        assert rc_result.units[3].target == "Vypnout..."
