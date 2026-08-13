"""Tests for the escape, newline and tab checks."""

from tests.translate.filters.checks.helpers import fails, fails_serious, passes
from translate.filters import checks


def test_escapes() -> None:
    """Tests escapes."""
    stdchecker = checks.StandardChecker()
    assert passes(stdchecker.escapes, r"""A sentence""", "I'm correct.")
    assert passes(stdchecker.escapes, "A file\n", "'n Leer\n")
    assert fails_serious(stdchecker.escapes, r"blah. A file", r"bleah.\n'n leer")
    assert passes(stdchecker.escapes, r"A tab\t", r"'n Tab\t")
    assert fails_serious(stdchecker.escapes, r"A tab\t", r"'n Tab")
    assert passes(stdchecker.escapes, r"An escape escape \\", r"Escape escape \\")
    assert fails_serious(stdchecker.escapes, r"An escape escape \\", "Escape escape")
    assert passes(stdchecker.escapes, r"A double quote \"", r"Double quote \"")
    assert fails_serious(stdchecker.escapes, r"A double quote \"", "Double quote")
    # Escaped escapes
    assert passes(stdchecker.escapes, "An escaped newline \\n", "Escaped newline \\n")
    assert fails_serious(
        stdchecker.escapes, "An escaped newline \\n", "Escaped newline \n"
    )
    # Real example
    ooochecker = checks.OpenOfficeChecker()
    assert passes(
        ooochecker.escapes,
        ",\t44\t;\t59\t:\t58\t{Tab}\t9\t{space}\t32",
        ",\t44\t;\t59\t:\t58\t{Tab}\t9\t{space}\t32",
    )
    lochecker = checks.LibreOfficeChecker()
    assert passes(
        lochecker.escapes,
        ",\t44\t;\t59\t:\t58\t{Tab}\t9\t{space}\t32",
        ",\t44\t;\t59\t:\t58\t{Tab}\t9\t{space}\t32",
    )


def test_newlines() -> None:
    """Tests newlines."""
    stdchecker = checks.StandardChecker()
    assert passes(stdchecker.newlines, "Nothing to see", "Niks te sien")
    assert passes(stdchecker.newlines, "Correct\n", "Korrek\n")
    assert passes(stdchecker.newlines, "Correct\r", "Korrek\r")
    assert passes(stdchecker.newlines, "Correct\r\n", "Korrek\r\n")
    assert fails(stdchecker.newlines, "A file\n", "'n Leer")
    assert fails(stdchecker.newlines, "A file", "'n Leer\n")
    assert fails(stdchecker.newlines, "A file\r", "'n Leer")
    assert fails(stdchecker.newlines, "A file", "'n Leer\r")
    assert fails(stdchecker.newlines, "A file\n", "'n Leer\r\n")
    assert fails(stdchecker.newlines, "A file\r\n", "'n Leer\n")
    assert fails(stdchecker.newlines, "blah.\nA file", "bleah. 'n leer")
    # msgfmt errors
    assert fails(stdchecker.newlines, "One two\n", "Een\ntwee")
    assert fails(stdchecker.newlines, "\nOne two", "Een\ntwee")
    # Real example
    ooochecker = checks.OpenOfficeChecker()
    assert fails(
        ooochecker.newlines,
        "The arrowhead was modified without saving.\nWould you like to save the arrowhead now?",
        "Ṱhoho ya musevhe yo khwinifhadzwa hu si na u seiva.Ni khou ṱoda u seiva thoho ya musevhe zwino?",
    )
    lochecker = checks.LibreOfficeChecker()
    assert fails(
        lochecker.newlines,
        "The arrowhead was modified without saving.\nWould you like to save the arrowhead now?",
        "Ṱhoho ya musevhe yo khwinifhadzwa hu si na u seiva.Ni khou ṱoda u seiva thoho ya musevhe zwino?",
    )


def test_tabs() -> None:
    """Tests tabs."""
    stdchecker = checks.StandardChecker()
    assert passes(stdchecker.tabs, "Nothing to see", "Niks te sien")
    assert passes(stdchecker.tabs, "Correct\t", "Korrek\t")
    assert passes(stdchecker.tabs, "Correct\tAA", "Korrek\tAA")
    assert fails_serious(stdchecker.tabs, "A file\t", "'n Leer")
    assert fails_serious(stdchecker.tabs, "A file", "'n Leer\t")
    ooochecker = checks.OpenOfficeChecker()
    assert passes(
        ooochecker.tabs,
        ",\t44\t;\t59\t:\t58\t{Tab}\t9\t{space}\t32",
        ",\t44\t;\t59\t:\t58\t{Tab}\t9\t{space}\t32",
    )
    lochecker = checks.LibreOfficeChecker()
    assert passes(
        lochecker.tabs,
        ",\t44\t;\t59\t:\t58\t{Tab}\t9\t{space}\t32",
        ",\t44\t;\t59\t:\t58\t{Tab}\t9\t{space}\t32",
    )
