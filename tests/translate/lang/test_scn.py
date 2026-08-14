import string

from tests.translate.filters.checks.helpers import fails, passes
from translate.lang.scn import SicilianChecker


def test_italianisms() -> None:
    """Test that we can detect italianisms."""
    scn_checker = SicilianChecker()
    assert passes(scn_checker.italianisms, "", "")
    assert fails(scn_checker.italianisms, "", "io")
    assert fails(scn_checker.italianisms, "", "tantu")
    assert fails(scn_checker.italianisms, "", "menu")
    assert fails(scn_checker.italianisms, "", "tantu cchiù picca")
    assert passes(scn_checker.italianisms, "io", "io")
    assert passes(scn_checker.italianisms, "", "cchiù")
    assert passes(scn_checker.italianisms, "", string.ascii_lowercase)
    assert passes(scn_checker.italianisms, "", string.ascii_uppercase)


def test_vocalism() -> None:
    """Test that we can detect vocalism issues."""
    scn_checker = SicilianChecker()
    assert passes(scn_checker.vocalism, "", "")
    assert fails(scn_checker.vocalism, "", "sale")
    assert fails(scn_checker.vocalism, "", "u vire")
    assert passes(scn_checker.vocalism, "", "me sali")
    assert passes(scn_checker.vocalism, "", "jo")
    assert passes(scn_checker.vocalism, "", "po jiri")
    assert passes(scn_checker.vocalism, "", string.ascii_lowercase)
    assert passes(scn_checker.vocalism, "", string.ascii_uppercase)


def test_suffixes() -> None:
    """Test that we can detect wrong suffixes."""
    scn_checker = SicilianChecker()
    assert passes(scn_checker.suffixes, "", "")
    assert fails(scn_checker.suffixes, "", "nazzioni")
    assert fails(scn_checker.suffixes, "", "cchiù azzioni")
    assert passes(scn_checker.suffixes, "razzioni", "razzioni")
    assert passes(scn_checker.suffixes, "", "nazziuni")
    assert passes(scn_checker.vocalism, "", string.ascii_lowercase)
    assert passes(scn_checker.vocalism, "", string.ascii_uppercase)
