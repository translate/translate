from translate.convert import rc2po, test_convert
from translate.storage.po import pofile


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
"""


class TestRC2POCommand(test_convert.TestConvertCommand):
    """Tests running actual rc2po commands on files"""

    convertmodule = rc2po
    defaultoptions = {"progress": "none"}
    expected_options = [
        "-t TEMPLATE, --template=TEMPLATE",
        "-l LANG, --lang=LANG",
        "-P, --pot",
        "--charset=CHARSET",
        "--sublang=SUBLANG",
        "--duplicates=DUPLICATESTYLE",
    ]

    def test_convert(self):
        """Tests the conversion to a po file"""
        self.create_testfile("simple.rc", RC_SOURCE)
        self.run_command(i="simple.rc", o="simple.po")
        po_result = pofile(self.open_testfile("simple.po"))
        assert len(po_result.units) == 23
        # first unit is PO file header
        assert po_result.units[1].source == "License dialog"
        assert po_result.units[11].source == "&Debug"
        assert po_result.units[12].source == "&Memory usage"
        assert po_result.units[13].source == "&Walk data heap"
        assert po_result.units[14].source == "Hello"
        assert po_result.units[15].source == "&File"
        assert po_result.units[15].getlocations() == [
            "MENU.IDR_MAINFRAME.POPUP.CAPTION"
        ]

    def test_convert_encoding_utf16(self):
        self.create_testfile("simple.rc", RC_SOURCE.encode("utf-16"))
        self.run_command(i="simple.rc", o="simple.po", charset="utf-16")
        po_result = pofile(self.open_testfile("simple.po"))
        assert len(po_result.units) == 23

    def test_convert_encoding_wrong(self):
        self.create_testfile("simple.rc", RC_SOURCE.encode("utf-8"))
        self.run_command(i="simple.rc", o="simple.po", charset="utf-16x")
        po_result = pofile(self.open_testfile("simple.po"))
        assert len(po_result.units) == 0
        self.run_command(i="simple.rc", o="simple.po", charset="utf-16")
        po_result = pofile(self.open_testfile("simple.po"))
        assert len(po_result.units) == 0

    def test_convert_encoding_utf8(self):
        self.create_testfile("simple.rc", RC_SOURCE.encode("utf-8"))
        self.run_command(i="simple.rc", o="simple.po", charset="utf-8")
        po_result = pofile(self.open_testfile("simple.po"))
        assert len(po_result.units) == 23

    def test_menuex(self):
        source = """
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
        self.create_testfile("simple.rc", source.encode("utf-8"))
        self.run_command(i="simple.rc", o="simple.po", charset="utf-8")
        po_result = pofile(self.open_testfile("simple.po"))
        assert len(po_result.units) == 5
