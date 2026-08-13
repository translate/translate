"""Tests for the variables check, per project configuration."""

from tests.translate.filters.checks.helpers import fails_serious, passes
from translate.filters import checks


def test_variables_kde() -> None:
    """Tests variables in KDE translations."""
    # GNOME variables
    kdechecker = checks.KdeChecker()
    assert passes(
        kdechecker.variables,
        "%d files of type %s saved.",
        "%d leers van %s tipe gestoor.",
    )
    assert fails_serious(
        kdechecker.variables,
        "%d files of type %s saved.",
        "%s leers van %s tipe gestoor.",
    )


def test_variables_gnome() -> None:
    """Tests variables in GNOME translations."""
    # GNOME variables
    gnomechecker = checks.GnomeChecker()
    assert passes(
        gnomechecker.variables,
        "%d files of type %s saved.",
        "%d leers van %s tipe gestoor.",
    )
    assert fails_serious(
        gnomechecker.variables,
        "%d files of type %s saved.",
        "%s leers van %s tipe gestoor.",
    )
    assert passes(gnomechecker.variables, "Save $(file)", "Stoor $(file)")
    assert fails_serious(gnomechecker.variables, "Save $(file)", "Stoor $(leer)")


def test_variables_mozilla() -> None:
    """Tests variables in Mozilla translations."""
    # Mozilla variables
    mozillachecker = checks.MozillaChecker()
    assert passes(
        mozillachecker.variables,
        "Use the &brandShortname; instance.",
        "Gebruik die &brandShortname; weergawe.",
    )
    assert fails_serious(
        mozillachecker.variables,
        "Use the &brandShortname; instance.",
        "Gebruik die &brandKortnaam; weergawe.",
    )
    assert passes(mozillachecker.variables, "Save %file%", "Stoor %file%")
    assert fails_serious(mozillachecker.variables, "Save %file%", "Stoor %leer%")
    assert passes(mozillachecker.variables, "Save $file$", "Stoor $file$")
    assert fails_serious(mozillachecker.variables, "Save $file$", "Stoor $leer$")
    assert passes(
        mozillachecker.variables,
        "%d files of type %s saved.",
        "%d leers van %s tipe gestoor.",
    )
    assert fails_serious(
        mozillachecker.variables,
        "%d files of type %s saved.",
        "%s leers van %s tipe gestoor.",
    )
    assert passes(mozillachecker.variables, "Save $file", "Stoor $file")
    assert fails_serious(mozillachecker.variables, "Save $file", "Stoor $leer")
    assert passes(mozillachecker.variables, "About $ProgramName$", "Oor $ProgramName$")
    assert fails_serious(
        mozillachecker.variables, "About $ProgramName$", "Oor $NaamVanProgam$"
    )
    assert passes(mozillachecker.variables, "About $_CLICK", "Oor $_CLICK")
    assert fails_serious(mozillachecker.variables, "About $_CLICK", "Oor $_KLIK")
    assert passes(
        mozillachecker.variables, "About $_CLICK and more", "Oor $_CLICK en meer"
    )
    assert fails_serious(
        mozillachecker.variables, "About $_CLICK and more", "Oor $_KLIK en meer"
    )
    assert passes(mozillachecker.variables, "About $(^NameDA)", "Oor $(^NameDA)")
    assert fails_serious(mozillachecker.variables, "About $(^NameDA)", "Oor $(^NaamDA)")
    assert passes(
        mozillachecker.variables,
        "Open {{pageCount}} pages",
        "Make {{pageCount}} bladsye oop",
    )
    assert fails_serious(
        mozillachecker.variables,
        "Open {{pageCount}} pages",
        "Make {{bladTelling}} bladsye oop",
    )
    # Double variable problem
    assert fails_serious(
        mozillachecker.variables, "Create In &lt;&lt;", "Etsa ka Ho &lt;lt;"
    )
    # Variables at the end of a sentence
    assert fails_serious(
        mozillachecker.variables,
        "...time you start &brandShortName;.",
        "...lekgetlo le latelang ha o qala &LebitsoKgutshwane la kgwebo;.",
    )
    # Ensure that we can detect two variables of the same name with one faulty
    assert fails_serious(
        mozillachecker.variables,
        "&brandShortName; successfully downloaded and installed updates. You will have to restart &brandShortName; to complete the update.",
        "&brandShortName; ḽo dzhenisa na u longela khwinifhadzo zwavhuḓi. Ni ḓo tea u thoma hafhu &DzinaḼipfufhi ḽa pfungavhuṇe; u itela u fhedzisa khwinifha dzo.",
    )
    # We must detect entities in their fullform, ie with fullstop in the middle.
    assert fails_serious(
        mozillachecker.variables,
        "Welcome to the &pluginWizard.title;",
        "Wamkelekile kwi&Sihloko Soncedo lwe-plugin;",
    )
    # Variables that are missing in quotes should be detected
    assert fails_serious(
        mozillachecker.variables,
        '"%S" is an executable file.... Are you sure you want to launch "%S"?',
        '.... Uyaqiniseka ukuthi ufuna ukuqalisa I"%S"?',
    )
    # False positive $ style variables
    assert passes(
        mozillachecker.variables,
        "for reporting $ProductShortName$ crash information",
        "okokubika ukwaziswa kokumosheka kwe-$ProductShortName$",
    )
    # We shouldn't mask variables within variables.  This should highlight &brandShortName as missing and &amp as extra
    assert fails_serious(
        mozillachecker.variables, "&brandShortName;", "&amp;brandShortName;"
    )


def test_variables_openoffice() -> None:
    """Tests variables in OpenOffice translations."""
    # OpenOffice.org variables
    for ooochecker in (checks.OpenOfficeChecker(), checks.LibreOfficeChecker()):
        assert passes(
            ooochecker.variables,
            "Use the &brandShortname; instance.",
            "Gebruik die &brandShortname; weergawe.",
        )
        assert fails_serious(
            ooochecker.variables,
            "Use the &brandShortname; instance.",
            "Gebruik die &brandKortnaam; weergawe.",
        )
        assert passes(ooochecker.variables, "Save %file%", "Stoor %file%")
        assert fails_serious(ooochecker.variables, "Save %file%", "Stoor %leer%")
        assert passes(ooochecker.variables, "Save %file", "Stoor %file")
        assert fails_serious(ooochecker.variables, "Save %file", "Stoor %leer")
        assert passes(ooochecker.variables, "Save %1", "Stoor %1")
        assert fails_serious(ooochecker.variables, "Save %1", "Stoor %2")
        assert passes(ooochecker.variables, "Save %", "Stoor %")
        assert fails_serious(ooochecker.variables, "Save %", "Stoor")
        assert passes(ooochecker.variables, "Save $(file)", "Stoor $(file)")
        assert fails_serious(ooochecker.variables, "Save $(file)", "Stoor $(leer)")
        assert passes(ooochecker.variables, "Save $file$", "Stoor $file$")
        assert fails_serious(ooochecker.variables, "Save $file$", "Stoor $leer$")
        assert passes(ooochecker.variables, "Save ${file}", "Stoor ${file}")
        assert fails_serious(ooochecker.variables, "Save ${file}", "Stoor ${leer}")
        assert passes(ooochecker.variables, "Save #file#", "Stoor #file#")
        assert fails_serious(ooochecker.variables, "Save #file#", "Stoor #leer#")
        assert passes(ooochecker.variables, "Save #1", "Stoor #1")
        assert fails_serious(ooochecker.variables, "Save #1", "Stoor #2")
        assert passes(ooochecker.variables, "Save #", "Stoor #")
        assert fails_serious(ooochecker.variables, "Save #", "Stoor")
        assert passes(ooochecker.variables, "Save ($file)", "Stoor ($file)")
        assert fails_serious(ooochecker.variables, "Save ($file)", "Stoor ($leer)")
        assert passes(ooochecker.variables, "Save $[file]", "Stoor $[file]")
        assert fails_serious(ooochecker.variables, "Save $[file]", "Stoor $[leer]")
        assert passes(ooochecker.variables, "Save [file]", "Stoor [file]")
        assert fails_serious(ooochecker.variables, "Save [file]", "Stoor [leer]")
        assert passes(ooochecker.variables, "Save $file", "Stoor $file")
        assert fails_serious(ooochecker.variables, "Save $file", "Stoor $leer")
        assert passes(ooochecker.variables, "Use @EXTENSION@", "Gebruik @EXTENSION@")
        assert fails_serious(
            ooochecker.variables, "Use @EXTENSUION@", "Gebruik @UITBRUIDING@"
        )
        # Same variable name twice
        assert fails_serious(
            ooochecker.variables,
            r"""Start %PROGRAMNAME% as %PROGRAMNAME%""",
            "Begin %PROGRAMNAME%",
        )


def test_variables_cclicense() -> None:
    """Tests variables in Creative Commons translations."""
    checker = checks.CCLicenseChecker()
    assert passes(checker.variables, "CC-GNU @license_code@.", "CC-GNU @license_code@.")
    assert fails_serious(
        checker.variables, "CC-GNU @license_code@.", "CC-GNU @lisensie_kode@."
    )
    assert passes(
        checker.variables,
        "Deed to the @license_name_full@",
        "Akte vir die @license_name_full@",
    )
    assert fails_serious(
        checker.variables,
        "Deed to the @license_name_full@",
        "Akte vir die @volle_lisensie@",
    )
    assert passes(
        checker.variables, "The @license_name_full@ is", "Die @license_name_full@ is"
    )
    assert fails_serious(
        checker.variables, "The @license_name_full@ is", "Die @iiilicense_name_full@ is"
    )
    assert fails_serious(checker.variables, "A @ccvar@", "'n @ccvertaaldeveranderlike@")


def test_variables_ios() -> None:
    """Test variables in iOS translations."""
    ioschecker = checks.IOSChecker()
    assert passes(ioschecker.variables, "Welcome $(NAME)", "Welkom $(NAME)")
    assert fails_serious(ioschecker.variables, "Welcome $(NAME)", "Welkom $(NAAM)")
    assert fails_serious(ioschecker.variables, "Welcome $(NAME)", "Welkom")

    assert passes(ioschecker.variables, "Welcome %@", "Welkom %@")
    assert fails_serious(ioschecker.variables, "Welcome %@", "Welkom $@")
    assert fails_serious(ioschecker.variables, "Welcome %@", "Welkom")
    assert passes(
        ioschecker.variables,
        "Downloading %1$@ at %2$@ speed",
        "Downloading at %2$@ speed the file %$1@",
    )
