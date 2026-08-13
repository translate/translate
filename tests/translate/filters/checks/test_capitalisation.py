"""Tests for the capitalisation checks."""

from tests.translate.filters.checks.helpers import fails, passes
from translate.filters import checks


def test_startcaps() -> None:
    """Tests starting capitals."""
    stdchecker = checks.StandardChecker()
    assert passes(stdchecker.startcaps, "Find", "Vind")
    assert passes(stdchecker.startcaps, "find", "vind")
    assert fails(stdchecker.startcaps, "Find", "vind")
    assert fails(stdchecker.startcaps, "find", "Vind")
    assert passes(stdchecker.startcaps, "'", "'")
    assert passes(
        stdchecker.startcaps,
        "\\.,/?!`'\"[]{}()@#$%^&*_-;:<>Find",
        "\\.,/?!`'\"[]{}()@#$%^&*_-;:<>Vind",
    )
    # With leading whitespace
    assert passes(stdchecker.startcaps, " Find", " Vind")
    assert passes(stdchecker.startcaps, " find", " vind")
    assert fails(stdchecker.startcaps, " Find", " vind")
    assert fails(stdchecker.startcaps, " find", " Vind")
    # Leading punctuation
    assert passes(stdchecker.startcaps, "'Find", "'Vind")
    assert passes(stdchecker.startcaps, "'find", "'vind")
    assert fails(stdchecker.startcaps, "'Find", "'vind")
    assert fails(stdchecker.startcaps, "'find", "'Vind")
    # Unicode
    assert passes(stdchecker.startcaps, "Find", "Šind")
    assert passes(stdchecker.startcaps, "find", "šind")
    assert fails(stdchecker.startcaps, "Find", "šind")
    assert fails(stdchecker.startcaps, "find", "Šind")
    # Unicode further down the Unicode tables
    assert passes(
        stdchecker.startcaps, "A text enclosed...", "Ḽiṅwalwa ḽo katelwaho..."
    )
    assert fails(stdchecker.startcaps, "A text enclosed...", "ḽiṅwalwa ḽo katelwaho...")
    # Accelerators
    stdchecker = checks.StandardChecker(checks.CheckerConfig(accelmarkers="&"))
    assert passes(stdchecker.startcaps, "&Find", "Vi&nd")
    # Numbers - we really can't tell what should happen with numbers, so ignore
    # source or target that start with a number
    assert passes(stdchecker.startcaps, "360 degrees", "Grade 360")
    assert passes(stdchecker.startcaps, "360 degrees", "grade 360")

    # Language specific stuff
    afchecker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="af"))
    assert passes(afchecker.startcaps, "A cow", "'n Koei")
    assert passes(afchecker.startcaps, "A list of ", "'n Lys van ")
    # should pass:
    # assert passes(afchecker.startcaps, "A 1k file", "'n 1k-lêer")
    assert passes(afchecker.startcaps, "'Do it'", "'Doen dit'")
    assert fails(afchecker.startcaps, "'Closer than'", "'nader as'")
    assert passes(afchecker.startcaps, "List", "Lys")
    assert passes(afchecker.startcaps, "a cow", "'n koei")
    assert fails(afchecker.startcaps, "a cow", "'n Koei")
    assert passes(afchecker.startcaps, "(A cow)", "('n Koei)")
    assert fails(afchecker.startcaps, "(a cow)", "('n Koei)")


def test_simplecaps() -> None:
    """Tests simple caps."""
    # Simple caps is a very vauge test so the checks here are mostly for obviously fixable problem
    # or for checking obviously correct situations that are triggering a failure.
    stdchecker = checks.StandardChecker()
    assert passes(
        stdchecker.simplecaps,
        "MB of disk space for the cache.",
        "MB yendzawo yediski etsala.",
    )
    # We should squash 'I' in the source text as it messes with capital detection
    assert passes(stdchecker.simplecaps, "if you say I want", "as jy se ek wil")
    assert passes(
        stdchecker.simplecaps, "sentence. I want more.", "sin. Ek wil meer he."
    )
    assert passes(
        stdchecker.simplecaps,
        "Where are we? I can't see where we are going.",
        "Waar is ons? Ek kan nie sien waar ons gaan nie.",
    )
    ## We should remove variables before checking
    stdchecker = checks.StandardChecker(checks.CheckerConfig(varmatches=[("%", 1)]))
    assert passes(
        stdchecker.simplecaps, "Could not load %s", "A swi koteki ku panga %S"
    )
    assert passes(
        stdchecker.simplecaps,
        'The element "%S" is not recognized.',
        'Elemente "%S" a yi tiveki.',
    )
    stdchecker = checks.StandardChecker(checks.CheckerConfig(varmatches=[("&", ";")]))
    assert passes(
        stdchecker.simplecaps,
        "Determine how &brandShortName; connects to the Internet.",
        "Kuma &brandShortName; hlanganisa eka Internete.",
    )
    ## If source is ALL CAPS then we should just check that target is also ALL CAPS
    assert passes(stdchecker.simplecaps, "COUPDAYS", "COUPMALANGA")
    # Just some that at times have failed but should always pass
    assert passes(
        stdchecker.simplecaps,
        "Create a query  entering an SQL statement directly.",
        "Yakha sibuti singena SQL inkhomba yesitatimende.",
    )
    ooochecker = checks.OpenOfficeChecker()
    assert passes(
        ooochecker.simplecaps,
        "SOLK (%PRODUCTNAME Link)",
        "SOLK (%PRODUCTNAME Thumanyo)",
    )
    assert passes(
        ooochecker.simplecaps, "%STAROFFICE Image", "Tshifanyiso tsha %STAROFFICE"
    )
    lochecker = checks.LibreOfficeChecker()
    assert passes(
        lochecker.simplecaps, "SOLK (%PRODUCTNAME Link)", "SOLK (%PRODUCTNAME Thumanyo)"
    )
    assert passes(
        lochecker.simplecaps, "%STAROFFICE Image", "Tshifanyiso tsha %STAROFFICE"
    )
    assert passes(
        stdchecker.simplecaps,
        "Flies, flies, everywhere! Ack!",
        "Vlieë, oral vlieë! Jig!",
    )
