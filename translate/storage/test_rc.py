from translate.storage import rc


def test_escaping():
    """test escaping Windows Resource files to Python strings"""
    assert rc.escape_to_python('''First line \
second line''') == "First line second line"
    assert rc.escape_to_python("A newline \\n in a string") == "A newline \n in a string"
    assert rc.escape_to_python("A tab \\t in a string") == "A tab \t in a string"
    assert rc.escape_to_python("A backslash \\\\ in a string") == "A backslash \\ in a string"
    assert rc.escape_to_python(r'''First line " \
 "second line''') == "First line second line"


def test_parse_comments(tmpdir):
    """test parsing a symple rc string format with comments

    This test method create a temporal simple and know file to be parsed
    with comments that must be ignored.
    """

    # Create a test file to be loaded in the temporary directory.

    testfile = tmpdir.join('test.rc')

    testfile.write("""

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

    """)

    rcreaded = rc.rcfile(testfile.open())


    #============================================================
    # Finally test that nothing is collected.
    #============================================================

    assert not rcreaded.getunits()


def test_parse_textinclude(tmpdir):
    """test parsing a symple rc string format with TEXTINCLUDE blocks

    This test method create a temporal simple and know file to be parsed
    with a TEXTINCLUDE block that must be ignored.
    """

    # Create a test file to be loaded in the temporary directory.

    testfile = tmpdir.join('test_textinclude.rc')

    testfile.write("""

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

    """)

    rcreaded = rc.rcfile(testfile.open())

    #============================================================
    # Finally test that nothing is collected.
    #============================================================

    assert not rcreaded.getunits()


def test_parse_dialog(tmpdir):
    """test parsing a symple rc with a DIALOG block

    This test method create a temporal simple and know file to be parsed with a
    dialog which strings must be extracted.
    """

    # Create a test file to be loaded in the temporary directory.

    testfile = tmpdir.join('test.rc')

    testfile.write("""

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

    """)

    rcreaded = rc.rcfile(testfile.open())

    #=====================================================
    # Declare the names and values that must be created.
    #=====================================================

    names = [
            'DIALOGEX.IDD_REGGHC_DIALOG.CAPTION',
            'DIALOGEX.IDD_REGGHC_DIALOG.PUSHBUTTON.ID_HELP',
            'DIALOGEX.IDD_REGGHC_DIALOG.PUSHBUTTON.IDCANCEL',
            'DIALOGEX.IDD_REGGHC_DIALOG.PUSHBUTTON.IDC_BUTTON1',
            'DIALOGEX.IDD_REGGHC_DIALOG.CTEXT.IDC_STATIC1',
            'DIALOGEX.IDD_REGGHC_DIALOG.CTEXT.IDC_STATIC',
            'DIALOGEX.IDD_REGGHC_DIALOG.PUSHBUTTON.IDC_OFFLINE',
            'DIALOGEX.IDD_REGGHC_DIALOG.PUSHBUTTON.IDC_LICENCIA',
            'DIALOGEX.IDD_REGGHC_DIALOG.RTEXT.IDC_STATIC',
            'DIALOGEX.IDD_REGGHC_DIALOG.CTEXT.IDC_ACTIVADA'
            ]

    values = [
            "License dialog",
            "Help",
            "Close",
            "Activate instalation",
            "My very good program",
            "You can use it without registering it",
            "Offline",
            "See license",
            "If you don't have internet, please use magic.",
            "Use your finger to activate the program."
            ]

    #============================================================
    # Finally test that all that must be collected is collected.
    #============================================================

    for i, unit in enumerate(rcreaded.getunits()):
        assert unit.name == names[i]
        assert unit.getsource() == values[i]


def test_parse_stringtable(tmpdir):
    """test parsing a symple rc string format with a STRINGTABLE block.

    This test method create a temporal simple and know file to be parsed
    with a stringtable which texts must be extracted.
    """

    # Create a test file to be loaded in the temporary directory.

    testfile = tmpdir.join('test.rc')

    testfile.write("""

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

    """)

    rcreaded = rc.rcfile(testfile.open())

    #=====================================================
    # Declare the names and values that must be created.
    #=====================================================

    names = [
            'STRINGTABLE.IDP_REGISTRONOV',
            'STRINGTABLE.IDS_ACTIVARINSTALACION',
            'STRINGTABLE.IDS_NOREGISTRADO',
            'STRINGTABLE.IDS_REGISTRADO',
            'STRINGTABLE.IDS_ACTIVADA',
            'STRINGTABLE.IDS_ERRORACTIV'
            ]

    values = [
            "Data isn't valid",
            "You need to try again and again.",
            "Error when making something important",
            "All done correctly.\nThank you very much.",
            "This is what you do:\n%s",
            "Error doing things"
            ]

    #============================================================
    # Finally test that all that must be collected is collected.
    #============================================================

    for i, unit in enumerate(rcreaded.getunits()):
        assert unit.name == names[i]
        assert unit.getsource() == values[i]
