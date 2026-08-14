"""Tests for the punctuation checks."""

from tests.translate.filters.checks.helpers import fails, passes
from translate.filters import checks


def test_startpunc() -> None:
    """Tests startpunc."""
    stdchecker = checks.StandardChecker()
    assert passes(stdchecker.startpunc, "<< Previous", "<< Correct")
    assert fails(stdchecker.startpunc, " << Previous", "Wrong")
    assert fails(stdchecker.startpunc, "Question", "\u2026Wrong")

    assert passes(
        stdchecker.startpunc, "<fish>hello</fish> world", "world <fish>hello</fish>"
    )

    # The inverted Spanish question mark should be accepted
    stdchecker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="es"))
    assert passes(
        stdchecker.startpunc,
        "Do you want to reload the file?",
        "¿Quiere recargar el archivo?",
    )

    # The Afrikaans indefinite article should be accepted
    stdchecker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="af"))
    assert passes(stdchecker.startpunc, "A human?", "'n Mens?")


def test_endpunc() -> None:
    """Tests endpunc."""
    stdchecker = checks.StandardChecker()
    assert passes(stdchecker.endpunc, "Question?", "Correct?")
    assert fails(stdchecker.endpunc, " Question?", "Wrong ?")
    # Newlines must not mask end punctuation
    assert fails(
        stdchecker.endpunc,
        "Exit change recording mode?\n\n",
        "Phuma esimeni sekugucula kubhalisa.\n\n",
    )
    mozillachecker = checks.MozillaChecker()
    assert passes(
        mozillachecker.endpunc,
        "Upgrades an existing $ProductShortName$ installation.",
        "Ku antswisiwa ka ku nghenisiwa ka $ProductShortName$.",
    )
    # Real examples
    assert passes(
        stdchecker.endpunc,
        "A nickname that identifies this publishing site (e.g.: 'MySite')",
        "Vito ro duvulela leri tirhisiwaka ku kuma sayiti leri ro kandziyisa (xik.: 'Sayiti ra Mina')",
    )
    assert fails(stdchecker.endpunc, "Question", "Wrong\u2026")
    # Making sure singlequotes don't confuse things
    assert passes(
        stdchecker.endpunc,
        "Pseudo-elements can't be negated '%1$S'.",
        "Pseudo-elemente kan nie '%1$S' ontken word nie.",
    )

    stdchecker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="km"))
    assert passes(
        stdchecker.endpunc,
        "In this new version, there are some minor conversion improvements on complex style in Openoffice.org Writer.",
        "នៅ\u200bក្នុង\u200bកំណែ\u200bថ្មីនេះ មាន\u200bការ\u200bកែសម្រួល\u200bមួយ\u200bចំនួន\u200bតូច\u200bទាក់\u200bទង\u200bនឹង\u200bការ\u200bបំលែង\u200bពុម្ពអក្សរ\u200bខ្មែរ\u200b ក្នុង\u200bកម្មវិធី\u200bការិយាល័យ\u200b ស្លឹករឹត ដែល\u200bមាន\u200bប្រើ\u200bប្រាស់\u200bរចនាប័ទ្មស្មុគស្មាញច្រើន\u00a0។",
    )

    stdchecker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="zh"))
    assert passes(
        stdchecker.endpunc,
        "To activate your account, follow this link:\n",
        "要啟用戶口，請瀏覽這個鏈結：\n",
    )

    stdchecker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="vi"))
    assert passes(
        stdchecker.endpunc,
        "Do you want to delete the XX dialog?",
        "Bạn có muốn xoá hộp thoại XX không?",
    )

    stdchecker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="fr"))
    assert passes(stdchecker.endpunc, "Header:", "En-tête :")
    assert passes(stdchecker.endpunc, "Header:", "En-tête\u00a0:")


def test_puncspacing() -> None:
    """Tests spacing after punctuation."""
    stdchecker = checks.StandardChecker()
    assert passes(
        stdchecker.puncspacing, "One, two, three.", "Kunye, kubili, kuthathu."
    )
    assert passes(
        stdchecker.puncspacing, "One, two, three. ", "Kunye, kubili, kuthathu."
    )
    assert fails(stdchecker.puncspacing, "One, two, three. ", "Kunye, kubili,kuthathu.")
    assert passes(
        stdchecker.puncspacing, "One, two, three!?", "Kunye, kubili, kuthathu?"
    )

    # Some languages have padded puntuation marks
    frchecker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="fr"))
    assert passes(frchecker.puncspacing, 'Do "this"', "Do « this »")
    assert passes(frchecker.puncspacing, 'Do "this"', "Do «\u00a0this\u00a0»")
    assert fails(frchecker.puncspacing, 'Do "this"', "Do «this»")

    # Handle Bidi markers as non-characters
    hechecker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="he"))
    assert passes(hechecker.puncspacing, "hi. there", "שלום.\u200f לך")  # RLM
    assert passes(hechecker.puncspacing, "hi. there", "שלום.\u200e לך")  # LRM
    assert passes(hechecker.puncspacing, "hi. there", "שלום.\u202b לך")  # RLE
    assert passes(hechecker.puncspacing, "hi. there", "שלום.\u202a לך")  # LRE
    assert passes(hechecker.puncspacing, "hi. there", "שלום.\u202e לך")  # RLO
    assert passes(hechecker.puncspacing, "hi. there", "שלום.\u202d לך")  # LRO
    assert passes(hechecker.puncspacing, "hi. there", "שלום.\u202c לך")  # PDF
    assert passes(hechecker.puncspacing, "hi. there", "שלום.\u2069 לך")  # PDI
    assert passes(hechecker.puncspacing, "hi. there", "שלום.\u2068 לך")  # FSI
    assert passes(hechecker.puncspacing, "hi. there", "שלום.\u2067 לך")  # RLI
    assert passes(hechecker.puncspacing, "hi. there", "שלום.\u2066 לך")  # LRI

    # ZWJ and ZWNJ handling as non-characters
    archecker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="ar"))
    assert passes(archecker.puncspacing, "hi. there", "السلام.\u200d عليكم")  # ZWJ
    assert passes(archecker.puncspacing, "hi. there", "السلام.\u200c عليكم")  # ZWNJ


def test_purepunc() -> None:
    """Tests messages containing only punctuation."""
    stdchecker = checks.StandardChecker()
    assert passes(stdchecker.purepunc, ".", ".")
    assert passes(stdchecker.purepunc, "", "")
    assert fails(stdchecker.purepunc, ".", " ")
    assert fails(stdchecker.purepunc, "Find", "'")
    assert fails(stdchecker.purepunc, "'", "Find")
    assert passes(stdchecker.purepunc, "year measurement template|2000", "2000")


def test_brackets() -> None:
    """Tests brackets."""
    stdchecker = checks.StandardChecker()
    assert passes(stdchecker.brackets, "N number(s)", "N getal(le)")
    assert fails(stdchecker.brackets, "For {sic} numbers", "Vier getalle")
    assert fails(stdchecker.brackets, "For }sic{ numbers", "Vier getalle")
    assert fails(stdchecker.brackets, "For [sic] numbers", "Vier getalle")
    assert fails(stdchecker.brackets, "For ]sic[ numbers", "Vier getalle")
    assert passes(stdchecker.brackets, "{[(", "[({")
