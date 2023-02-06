from io import BytesIO

from translate.storage import rc


def test_escaping():
    """test escaping Windows Resource files to Python strings"""
    assert (
        rc.escape_to_python(
            """First line \
second line"""
        )
        == "First line second line"
    )
    assert (
        rc.escape_to_python("A newline \\n in a string") == "A newline \n in a string"
    )
    assert (
        rc.escape_to_python("A carriage return \\r in a string")
        == "A carriage return \r in a string"
    )
    assert rc.escape_to_python("A tab \\t in a string") == "A tab \t in a string"
    assert (
        rc.escape_to_python("A backslash \\\\ in a string")
        == "A backslash \\ in a string"
    )
    assert (
        rc.escape_to_python(
            r"""First line " \
 "second line"""
        )
        == "First line second line"
    )


class TestRcFile:
    StoreClass = rc.rcfile

    def source_parse(self, source, encoding="utf-8"):
        """Helper that parses source without requiring files."""
        dummy_file = BytesIO(source.encode(encoding))
        return self.StoreClass(dummy_file)

    def source_regenerate(self, source):
        """Helper that converts source to store object and back."""
        return bytes(self.source_parse(source))

    def test_parse_only_comments(self):
        """Test parsing a RC string with only comments."""
        rc_source = r"""
/*
 * Mini test file.
 * Multiline comments.
 */

// Test file, one line comment. //

#include "other_file.h" // This must be ignored

LANGUAGE LANG_ENGLISH, SUBLANG_DEFAULT

/////////////////////////////////////////////////////////////////////////////
//
// Icon
//

// Icon with lowest ID value placed first to ensure application icon
// remains consistent on all systems.
IDR_MAINFRAME           ICON                    "res\\ico00007.ico"
IDR_MAINFRAME1          ICON                    "res\\idr_main.ico"
IDR_MAINFRAME2          ICON                    "res\\ico00006.ico"


/////////////////////////////////////////////////////////////////////////////
//
// Commented STRINGTABLE must be ignored
//

/*
STRINGTABLE
BEGIN
    IDP_REGISTRONOV         "Data isn't valid"
    IDS_ACTIVARINSTALACION  "You need to try again and again."
    IDS_NOREGISTRADO        "Error when making something important"
    IDS_REGISTRADO          "All done correctly.\nThank you very much."
    IDS_ACTIVADA            "This is what you do:\n%s"
    IDS_ERRORACTIV          "Error doing things"
END
*/

#ifndef APSTUDIO_INVOKED
/////////////////////////////////////////////////////////////////////////////
//
// Generated from the TEXTINCLUDE 3 resource.
//
#define _AFX_NO_SPLITTER_RESOURCES
#define _AFX_NO_OLE_RESOURCES
#define _AFX_NO_TRACKER_RESOURCES
#define _AFX_NO_PROPERTY_RESOURCES

#if !defined(AFX_RESOURCE_DLL) || defined(AFX_TARG_ESN)
// This will change the default language
LANGUAGE 10, 3
#pragma code_page(1252)
#include "res\regGHC.rc2"  // Recursos editados que no son de Microsoft Visual C++
#include "afxres.rc"         // Standar components
#endif

/////////////////////////////////////////////////////////////////////////////
#endif    // not APSTUDIO_INVOKED
"""
        rc_file = self.source_parse(rc_source)
        assert len(rc_file.units) == 0

    def test_parse_only_textinclude(self):
        """Test parsing a RC string with TEXTINCLUDE blocks and comments."""
        rc_source = r"""
#include "other_file.h" // This must be ignored

LANGUAGE LANG_ENGLISH, SUBLANG_DEFAULT

#ifdef APSTUDIO_INVOKED
/////////////////////////////////////////////////////////////////////////////
//
// TEXTINCLUDE
//

1 TEXTINCLUDE
BEGIN
    "resource.h\0"
END

2 TEXTINCLUDE
BEGIN
    "#include ""afxres.h""\r\n"
    "\0"
END

3 TEXTINCLUDE
BEGIN
    "LANGUAGE 10, 3\r\n"  // This language must be ignored, is a string.
    "And this strings don't need to be translated!"
END

#endif    // APSTUDIO_INVOKED
"""
        rc_file = self.source_parse(rc_source)
        assert len(rc_file.units) == 0

    def test_parse_dialog(self):
        """Test parsing a RC string with a DIALOG block."""
        rc_source = r"""
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
    CTEXT           "Use your finger to" " activate the program.",IDC_ACTIVADA,17,50,175,17
    ICON            IDR_MAINFRAME1,IDC_STATIC6,18,19,20,20
END
"""
        rc_file = self.source_parse(rc_source)
        assert len(rc_file.units) == 10
        rc_unit = rc_file.units[0]
        assert rc_unit.name == "DIALOGEX.IDD_REGGHC_DIALOG.CAPTION"
        assert rc_unit.source == "License dialog"
        rc_unit = rc_file.units[1]
        assert rc_unit.name == "DIALOGEX.IDD_REGGHC_DIALOG.PUSHBUTTON.ID_HELP"
        assert rc_unit.source == "Help"
        rc_unit = rc_file.units[2]
        assert rc_unit.name == "DIALOGEX.IDD_REGGHC_DIALOG.PUSHBUTTON.IDCANCEL"
        assert rc_unit.source == "Close"
        rc_unit = rc_file.units[3]
        assert rc_unit.name == "DIALOGEX.IDD_REGGHC_DIALOG.PUSHBUTTON.IDC_BUTTON1"
        assert rc_unit.source == "Activate instalation"
        rc_unit = rc_file.units[4]
        assert rc_unit.name == "DIALOGEX.IDD_REGGHC_DIALOG.CTEXT.IDC_STATIC1"
        assert rc_unit.source == "My very good program"
        rc_unit = rc_file.units[5]
        assert rc_unit.name == "DIALOGEX.IDD_REGGHC_DIALOG.CTEXT.IDC_STATIC"
        assert rc_unit.source == "You can use it without registering it"
        rc_unit = rc_file.units[6]
        assert rc_unit.name == "DIALOGEX.IDD_REGGHC_DIALOG.PUSHBUTTON.IDC_OFFLINE"
        assert rc_unit.source == "Offline"
        rc_unit = rc_file.units[7]
        assert rc_unit.name == "DIALOGEX.IDD_REGGHC_DIALOG.PUSHBUTTON.IDC_LICENCIA"
        assert rc_unit.source == "See license"
        rc_unit = rc_file.units[8]
        assert rc_unit.name == "DIALOGEX.IDD_REGGHC_DIALOG.RTEXT.IDC_STATIC"
        assert rc_unit.source == "If you don't have internet, please use magic."
        rc_unit = rc_file.units[9]
        assert rc_unit.name == "DIALOGEX.IDD_REGGHC_DIALOG.CTEXT.IDC_ACTIVADA"
        assert rc_unit.source == "Use your finger to activate the program."

    def test_parse_stringtable(self):
        """Test parsing a RC string with a STRINGTABLE block."""
        rc_source = r"""
#include "other_file.h" // This must be ignored

LANGUAGE LANG_ENGLISH, SUBLANG_DEFAULT

/////////////////////////////////////////////////////////////////////////////
//
// String Table
//

STRINGTABLE
BEGIN
    IDP_REGISTRONOV         "Data isn't valid"
    IDS_ACTIVARINSTALACION  "You need to try again and again."
    IDS_NOREGISTRADO        "Error when making something important"
    IDS_REGISTRADO          "All done correctly.\nThank you very much."
    IDS_ACTIVADA            "This is what you do:\n%s"
    IDS_ERRORACTIV          "Error doing things"
END
"""
        rc_file = self.source_parse(rc_source)
        assert len(rc_file.units) == 6
        rc_unit = rc_file.units[0]
        assert rc_unit.name == "STRINGTABLE.IDP_REGISTRONOV"
        assert rc_unit.source == "Data isn't valid"
        rc_unit = rc_file.units[1]
        assert rc_unit.name == "STRINGTABLE.IDS_ACTIVARINSTALACION"
        assert rc_unit.source == "You need to try again and again."
        rc_unit = rc_file.units[2]
        assert rc_unit.name == "STRINGTABLE.IDS_NOREGISTRADO"
        assert rc_unit.source == "Error when making something important"
        rc_unit = rc_file.units[3]
        assert rc_unit.name == "STRINGTABLE.IDS_REGISTRADO"
        assert rc_unit.source == "All done correctly.\nThank you very much."
        rc_unit = rc_file.units[4]
        assert rc_unit.name == "STRINGTABLE.IDS_ACTIVADA"
        assert rc_unit.source == "This is what you do:\n%s"
        rc_unit = rc_file.units[5]
        assert rc_unit.name == "STRINGTABLE.IDS_ERRORACTIV"
        assert rc_unit.source == "Error doing things"

    def test_parse_newlines_lf(self):
        """Test parsing a RC string with lf line endings."""
        rc_source = """\n\
LANGUAGE LANG_ENGLISH, SUBLANG_DEFAULT\n\
\n\
STRINGTABLE\n\
BEGIN\n\
    IDP_REGISTRONOV         "Data isn't valid"\n\
    IDS_ACTIVARINSTALACION  "You need to try again and again."\n\
END\n\
"""
        rc_file = self.source_parse(rc_source)
        assert len(rc_file.units) == 2
        rc_unit = rc_file.units[0]
        assert rc_unit.name == "STRINGTABLE.IDP_REGISTRONOV"
        assert rc_unit.source == "Data isn't valid"
        rc_unit = rc_file.units[1]
        assert rc_unit.name == "STRINGTABLE.IDS_ACTIVARINSTALACION"
        assert rc_unit.source == "You need to try again and again."

    def test_parse_newlines_crlf(self):
        """Test parsing a RC string with crlf line endings."""
        rc_source = """\r\n\
LANGUAGE LANG_ENGLISH, SUBLANG_DEFAULT\r\n\
\r\n\
STRINGTABLE\r\n\
BEGIN\r\n\
    IDP_REGISTRONOV         "Data isn't valid"\r\n\
    IDS_ACTIVARINSTALACION  "You need to try again and again."\r\n\
END\r\n\
"""
        rc_file = self.source_parse(rc_source)
        assert len(rc_file.units) == 2
        rc_unit = rc_file.units[0]
        assert rc_unit.name == "STRINGTABLE.IDP_REGISTRONOV"
        assert rc_unit.source == "Data isn't valid"
        rc_unit = rc_file.units[1]
        assert rc_unit.name == "STRINGTABLE.IDS_ACTIVARINSTALACION"
        assert rc_unit.source == "You need to try again and again."

    def test_parse_newlines_cr(self):
        """Test parsing a RC string with crlf line endings."""
        rc_source = """\r\
LANGUAGE LANG_ENGLISH, SUBLANG_DEFAULT\r\
\r\
STRINGTABLE\r\
BEGIN\r\
    IDP_REGISTRONOV         "Data isn't valid"\r\
    IDS_ACTIVARINSTALACION  "You need to try again and again."\r\
END\r\
"""
        rc_file = self.source_parse(rc_source)
        assert len(rc_file.units) == 0

    def test_parse_no_language(self):
        """Test parsing a RC string with missing language tag."""
        rc_source = """
STRINGTABLE
BEGIN
    IDP_REGISTRONOV         "Data isn't valid"
END
"""
        rc_file = self.source_parse(rc_source)
        assert len(rc_file.units) == 1
        assert rc_file.units[0].source == "Data isn't valid"

    def test_textinclude(self):
        rc_source = """
// Microsoft Visual C++ generated resource script.
//
#include "resource.h"

#define APSTUDIO_READONLY_SYMBOLS
/////////////////////////////////////////////////////////////////////////////
//
// Generated from the TEXTINCLUDE 2 resource.
//
#include "afxres.h"

/////////////////////////////////////////////////////////////////////////////
#undef APSTUDIO_READONLY_SYMBOLS

/////////////////////////////////////////////////////////////////////////////
// English (United States) resources

#if !defined(AFX_RESOURCE_DLL) || defined(AFX_TARG_ENU)
LANGUAGE LANG_ENGLISH, SUBLANG_ENGLISH_US
#pragma code_page(1252)

#ifdef APSTUDIO_INVOKED
/////////////////////////////////////////////////////////////////////////////
//
// TEXTINCLUDE
//

1 TEXTINCLUDE
BEGIN
    "resource.h\0"
END

2 TEXTINCLUDE
BEGIN
    "#include ""afxres.h""\r\n"
    "\0"
END

3 TEXTINCLUDE
BEGIN
    "#include ""res\\untranslatable.rc2""  // untranslatable strings\r\n"
    "\r\n"
    "#define _AFX_NO_SPLITTER_RESOURCES\r\n"
    "#define _AFX_NO_OLE_RESOURCES\r\n"
    "#define _AFX_NO_TRACKER_RESOURCES\r\n"
    "#define _AFX_NO_PROPERTY_RESOURCES\r\n"
    "\r\n"
    "#if !defined(AFX_RESOURCE_DLL) || defined(AFX_TARG_ENU)\r\n"
    "LANGUAGE 9, 1\r\n"
    "#pragma code_page(1252)\r\n"
    "#include ""afxres.rc""     // Standard components\r\n"
    "#include ""res\\mpc-hc.rc2""  // non-Microsoft Visual C++ edited resources\r\n"
    "#endif\0"
END

#endif    // APSTUDIO_INVOKED


/////////////////////////////////////////////////////////////////////////////
//
// Dialog
//

IDD_SELECTMEDIATYPE DIALOGEX 0, 0, 225, 47
STYLE DS_SETFONT | DS_MODALFRAME | DS_FIXEDSYS | WS_POPUP | WS_CAPTION | WS_SYSMENU
CAPTION "Select Media Type"
FONT 8, "MS Shell Dlg", 400, 0, 0x1
BEGIN
    COMBOBOX        IDC_COMBO1,5,5,215,37,CBS_DROPDOWN | WS_VSCROLL | WS_TABSTOP
    DEFPUSHBUTTON   "OK",IDOK,116,28,50,14
    PUSHBUTTON      "Cancel",IDCANCEL,170,28,50,14
END
"""
        rc_file = self.source_parse(rc_source)
        assert len(rc_file.units) == 3
        assert rc_file.units[0].source == "Select Media Type"
        assert rc_file.units[1].source == "OK"
        assert rc_file.units[2].source == "Cancel"

    def test_multiline(self):
        rc_source = r"""
LANGUAGE LANG_ENGLISH, SUBLANG_DEFAULT

STRINGTABLE
BEGIN
    IDS_ADJACENT_STRINGS    "Line1\n"
                            "Line2"
END
"""
        rc_file = self.source_parse(rc_source)
        assert len(rc_file.units) == 1
        assert rc_file.units[0].source == "Line1\nLine2"

    def test_str(self):
        rc_source = r"""
LANGUAGE LANG_ENGLISH, SUBLANG_DEFAULT

STRINGTABLE
BEGIN
    IDS_STRINGS    "Line1"
END
"""
        rc_file = self.source_parse(rc_source)
        assert len(rc_file.units) == 1
        assert str(rc_file.units[0]) == "STRINGTABLE.IDS_STRINGS=Line1\n"

    def test_empty(self):
        rc_source = """
LANGUAGE LANG_ENGLISH, SUBLANG_ENGLISH_US

IDD_DIALOG DIALOG 0, 0, 339, 179
CAPTION "Caption"
BEGIN
    CONTROL         "", IDC_HEADSEPARATOR, "Static", SS_BLACKFRAME | SS_SUNKEN, 0, 28, 339, 1
END
"""
        rc_file = self.source_parse(rc_source)
        assert len(rc_file.units) == 1

    def test_utf_8(self):
        rc_source = """#pragma code_page(65001)

STRINGTABLE
BEGIN
    IDS_COPIED              "✔ Copied"
END
"""
        rc_file = self.source_parse(rc_source)
        assert len(rc_file.units) == 1
        assert rc_file.units[0].source == "✔ Copied"

    def test_utf_16(self):
        rc_source = """
STRINGTABLE
BEGIN
    IDS_COPIED              "✔ Copied"
END
"""
        rc_file = self.source_parse(rc_source, "utf-16-le")
        assert len(rc_file.units) == 1
        assert rc_file.units[0].source == "✔ Copied"

    def test_comment(self):
        rc_source = """
STRINGTABLE
BEGIN
    // IDS_COMMENTED        "Comment"
    IDS_COPIED              "Copied"
END
"""
        rc_file = self.source_parse(rc_source)
        assert len(rc_file.units) == 1
        assert rc_file.units[0].source == "Copied"

    def test_stringtables(self):
        rc_source = """
STRINGTABLE
BEGIN
    IDS_COPIED              "Copied"
END

STRINGTABLE
BEGIN
    /* Comment */
    IDS_OTHER               "Other"
END

    //63
STRINGTABLE
BEGIN

    IDS_NEXT                "Next"

END
"""
        rc_file = self.source_parse(rc_source)
        assert len(rc_file.units) == 3
        assert rc_file.units[0].source == "Copied"
        assert rc_file.units[1].source == "Other"
        assert rc_file.units[2].source == "Next"

    def test_textinclude_appstudio(self):
        rc_source = """
LANGUAGE LANG_NEUTRAL, SUBLANG_NEUTRAL

STRINGTABLE
BEGIN
    IDS_COPIED              "Copied"
END

1 TEXTINCLUDE
BEGIN
    "#pragma code_page(1252)\r\n"
END

STRINGTABLE
BEGIN
    IDS_OTHER               "Other"
END
"""
        rc_file = self.source_parse(rc_source, encoding="utf-16")
        assert len(rc_file.units) == 2
        assert rc_file.units[0].source == "Copied"
        assert rc_file.units[1].source == "Other"

    def test_id_whitespace(self):
        rc_source = """
IDD_DIALOG DIALOG 0, 0, 340, 180
CAPTION "Caption"
BEGIN
    LTEXT           "Right",IDC_STATIC_HEADER,7,0,258,8,NOT WS_GROUP
    LTEXT           "Wrong",IDC_STATIC_HEADER2
                    ,7,0,258,8,NOT WS_GROUP
END
"""
        rc_file = self.source_parse(rc_source, encoding="utf-16")
        assert len(rc_file.units) == 3
        assert rc_file.units[0].source == "Caption"
        assert rc_file.units[0].name == "DIALOG.IDD_DIALOG.CAPTION"
        assert rc_file.units[1].source == "Right"
        assert rc_file.units[1].name == "DIALOG.IDD_DIALOG.LTEXT.IDC_STATIC_HEADER"
        assert rc_file.units[2].source == "Wrong"
        assert rc_file.units[2].name == "DIALOG.IDD_DIALOG.LTEXT.IDC_STATIC_HEADER2"

    def test_menu_comment(self):
        rc_source = """
IDR_MAINFRAME MENU
BEGIN
  POPUP "&File"
  BEGIN
    //MENUITEM "Commented.", ID_COMMENTED
    MENUITEM "Copied", ID_COPIED
    // This comment will also break rc2po
    MENUITEM "Delete", ID_DELETE
  END
END
"""
        rc_file = self.source_parse(rc_source, encoding="utf-16")
        assert len(rc_file.units) == 3
        assert rc_file.units[0].source == "&File"
        assert rc_file.units[0].name == "MENU.IDR_MAINFRAME.POPUP.CAPTION"
        assert rc_file.units[1].source == "Copied"
        assert rc_file.units[1].name == "MENU.IDR_MAINFRAME.MENUITEM.ID_COPIED"
        assert rc_file.units[2].source == "Delete"
        assert rc_file.units[2].name == "MENU.IDR_MAINFRAME.MENUITEM.ID_DELETE"

    def test_decompiled(self):
        rc_source = """
1 MENU
{
  POPUP "This is a menu."
  {
    MENUITEM "This is a menu item.",  2
  }
}

3 DIALOGEX 0, 0, 156, 50
CAPTION "This is a dialog."
{
   CONTROL "This is a button.", 4, BUTTON, BS_DEFPUSHBUTTON | WS_CHILD | WS_VISIBLE | WS_TABSTOP, 99, 7, 50, 14
}

STRINGTABLE
{
  5 	"This is a string."
}
"""
        rc_file = self.source_parse(rc_source)
        assert len(rc_file.units) == 5
        assert rc_file.units[0].source == "This is a menu."
        assert rc_file.units[0].name == "MENU.1.POPUP.CAPTION"
        assert rc_file.units[1].source == "This is a menu item."
        assert rc_file.units[1].name == "MENU.1.MENUITEM.2"
        assert rc_file.units[2].source == "This is a dialog."
        assert rc_file.units[2].name == "DIALOGEX.3.CAPTION"
        assert rc_file.units[3].source == "This is a button."
        assert rc_file.units[3].name == "DIALOGEX.3.CONTROL.4"
        assert rc_file.units[4].source == "This is a string."
        assert rc_file.units[4].name == "STRINGTABLE.5"
