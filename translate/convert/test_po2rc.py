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
    CTEXT           "My very good program",IDC_STATIC1,56,21,109,19,SS_SUNKEN
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
"""


class TestPO2RCCommand(test_convert.TestConvertCommand):
    """Tests running actual po2rc commands on files"""

    convertmodule = po2rc
    defaultoptions = {"progress": "none"}

    def test_help(self, capsys):
        """tests getting help"""
        options = super().test_help(capsys)
        options = self.help_check(options, "-t TEMPLATE, --template=TEMPLATE")
        options = self.help_check(options, "-l LANG, --lang=LANG")

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
