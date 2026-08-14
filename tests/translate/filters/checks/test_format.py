"""Tests for the format string checks."""

from tests.translate.filters.checks.helpers import fails, fails_serious, passes
from translate.filters import checks


def test_printf() -> None:
    """Tests printf style variables."""
    # This should really be a subset of the variable checks
    # Ideally we should be able to adapt based on #, directives also
    stdchecker = checks.StandardChecker()
    assert passes(stdchecker.printf, "I am %s", "Ek is %s")
    assert fails(stdchecker.printf, "I am %s", "Ek is %d")
    assert passes(stdchecker.printf, "I am %#100.50hhf", "Ek is %#100.50hhf")
    assert fails(stdchecker.printf, "I am %#100s", "Ek is %10s")
    assert fails(
        stdchecker.printf,
        "... for user %.100s on %.100s:",
        "... lomuntu osebenzisa i-%. I-100s e-100s:",
    )
    assert passes(stdchecker.printf, "%dMB", "%d MG")
    # Reordering
    assert passes(
        stdchecker.printf, "String %s and number %d", "String %1$s en nommer %2$d"
    )
    assert passes(
        stdchecker.printf, "String %1$s and number %2$d", "String %1$s en nommer %2$d"
    )
    assert passes(
        stdchecker.printf, "String %s and number %d", "Nommer %2$d and string %1$s"
    )
    assert passes(
        stdchecker.printf,
        "String %s and real number %f and number %d",
        "String %1$s en nommer %3$d en reële getal %2$f",
    )
    assert passes(
        stdchecker.printf,
        "String %1$s and real number %2$f and number %3$d",
        "String %1$s en nommer %3$d en reële getal %2$f",
    )
    assert passes(
        stdchecker.printf,
        "Real number %2$f and string %1$s and number %3$d",
        "String %1$s en nommer %3$d en reële getal %2$f",
    )
    assert fails(
        stdchecker.printf, "String %s and number %d", "Nommer %1$d and string %2$s"
    )
    assert fails(
        stdchecker.printf,
        "String %s and real number %f and number %d",
        "String %1$s en nommer %3$d en reële getal %2$d",
    )
    assert fails(
        stdchecker.printf,
        "String %s and real number %f and number %d",
        "String %1$s en nommer %3$d en reële getal %4$f",
    )
    assert fails(
        stdchecker.printf,
        "String %s and real number %f and number %d",
        "String %2$s en nommer %3$d en reële getal %2$f",
    )
    assert fails(
        stdchecker.printf,
        "Real number %2$f and string %1$s and number %3$d",
        "String %1$f en nommer %3$d en reële getal %2$f",
    )
    # checking python format strings
    assert passes(
        stdchecker.printf,
        "String %(1)s and number %(2)d",
        "Nommer %(2)d en string %(1)s",
    )
    assert passes(
        stdchecker.printf,
        "String %(str)s and number %(num)d",
        "Nommer %(num)d en string %(str)s",
    )
    assert fails(
        stdchecker.printf,
        "String %(str)s and number %(num)d",
        "Nommer %(nommer)d en string %(str)s",
    )
    assert fails(
        stdchecker.printf,
        "String %(str)s and number %(num)d",
        "Nommer %(num)d en string %s",
    )
    # checking POSIX thousands separator flag %'d
    assert passes(stdchecker.printf, "delete %'d items", "supprimer %'d éléments")
    assert fails(stdchecker.printf, "delete %'d items", "supprimer éléments")
    assert fails(stdchecker.printf, "delete %'d items", "supprimer %d éléments")
    # checking omitted plural format string placeholder %.0s
    stdchecker.hasplural = 1
    assert passes(stdchecker.printf, "%d plurals", "%.0s plural")
    # checking POSIX thousands separator flag with plural
    assert passes(stdchecker.printf, "delete %'d items", "supprimer %'d éléments")
    assert fails(stdchecker.printf, "delete %'d items", "supprimer éléments")
    # checking Objective-C %@ format specification
    assert fails(stdchecker.printf, "I am %@", "Ek is @%")  # typo
    assert fails(
        stdchecker.printf, "Object %@ and object %@", "String %1$@ en string %3$@"
    )  # out of bounds
    assert fails(stdchecker.printf, "I am %@", "Ek is %s")  # wrong specification
    assert passes(
        stdchecker.printf, "Object %@ and string %s", "Object %1$@ en string %2$s"
    )  # correct sentence
    # Checking boost format.
    # Boost classic printf.
    assert passes(
        stdchecker.printf,
        "writing %1%,  x=%2% : %3%-th try",
        "escribindo %1%,  x=%2% : %3%-esimo intento",
    )
    # Reordering boost.
    assert passes(stdchecker.printf, "%1% %2% %3% %2% %1%", "%1% %2% %3% %2% %1%")
    # Boost posix format.
    assert passes(
        stdchecker.printf, "(x,y) = (%1$+5d,%2$+5d)", "(x,y) = (%1$+5d,%2$+5d)"
    )
    # Boost several ways to express the same.
    assert passes(stdchecker.printf, "(x,y) = (%+5d,%+5d)", "(x,y) = (%+5d,%+5d)")
    assert passes(stdchecker.printf, "(x,y) = (%|+5|,%|+5|)", "(x,y) = (%|+5|,%|+5|)")
    assert passes(
        stdchecker.printf, "(x,y) = (%1$+5d,%2$+5d)", "(x,y) = (%1$+5d,%2$+5d)"
    )
    assert passes(
        stdchecker.printf, "(x,y) = (%|1$+5|,%|2$+5|)", "(x,y) = (%|1$+5|,%|2$+5|)"
    )
    # Boost using manipulators.
    assert passes(
        stdchecker.printf, "_%1$+5d_ %1$d", "_%1$+5d_ %1$d"
    )  # This is failing.
    assert passes(stdchecker.printf, "_%1%_ %1%", "_%1%_ %1%")
    # Boost absolute tabulations.
    assert passes(stdchecker.printf, "%1%, %2%, %|40t|%3%", "%1%, %2%, %|40t|%3%")


def test_pythonbraceformat() -> None:
    """Tests python brace format placeholder."""
    stdchecker = checks.StandardChecker()
    # anonymous formats
    assert passes(
        stdchecker.pythonbraceformat,
        "String {} and number {}",
        "String {} en nommer {}",
    )
    assert passes(stdchecker.pythonbraceformat, "String {1}", "Nommer {} en string {}")
    assert passes(
        stdchecker.pythonbraceformat,
        "String {1} and number {0}",
        "Nommer {0} en string {1}",
    )
    assert fails(stdchecker.pythonbraceformat, "String {}, {}", "String {}")
    assert fails_serious(
        stdchecker.pythonbraceformat, "String {}", "String {} en nommer {}"
    )
    assert fails_serious(stdchecker.pythonbraceformat, "String {}", "Nommer {1}")
    assert fails_serious(stdchecker.pythonbraceformat, "String {0}", "Nommer {1}")
    assert fails_serious(stdchecker.pythonbraceformat, "String {0} {}", "Nommer {1}")
    lochecker = checks.LibreOfficeChecker()
    assert passes(
        lochecker.pythonbraceformat,
        "Time remaining: {[1] minutes }{[2] seconds}",
        "Tenpo che'l resta: {[1] minuti}{[2] secondi}",
    )

    # Named formats
    assert passes(
        stdchecker.pythonbraceformat,
        "String {str} and number {num}",
        "Nommer {num} en string {str}",
    )
    # TODO: check for a mixture of substitution techniques
    assert fails(
        stdchecker.pythonbraceformat,
        "String {str} and number {num}",
        "Nommer {num} en string %s",
    )
    assert fails_serious(
        stdchecker.pythonbraceformat,
        "String {str} and number {num}",
        "Nommer {onbekend} en string {str}",
    )
