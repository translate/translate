from translate.filters.test_checks import fails, passes
from translate.lang.scn import SicilianChecker


def test_italianisms():
    """Test that we can detect italianisms."""
    scn_checker = SicilianChecker()
    assert passes(scn_checker.italianisms, "", "")
    assert fails(scn_checker.italianisms, "", "io")
    assert fails(scn_checker.italianisms, "", "tantu")
    assert fails(scn_checker.italianisms, "", "menu")
    assert fails(scn_checker.italianisms, "", "tantu cchiù picca")
    assert passes(scn_checker.italianisms, "io", "io")
    assert passes(scn_checker.italianisms, "", "cchiù")
    assert passes(scn_checker.italianisms, "", "abcdefghijklmnopqrstuvwxyz")
    assert passes(scn_checker.italianisms, "", "ABCDEFGHIJKLMNOPQRSTUVWXYZ")


def test_vocalism():
    """Test that we can detect vocalism issues."""
    scn_checker = SicilianChecker()
    assert passes(scn_checker.vocalism, "", "")
    assert fails(scn_checker.vocalism, "", "sale")
    assert fails(scn_checker.vocalism, "", "u vire")
    assert passes(scn_checker.vocalism, "", "me sali")
    assert passes(scn_checker.vocalism, "", "jo")
    assert passes(scn_checker.vocalism, "", "po jiri")
    assert passes(scn_checker.vocalism, "", "abcdefghijklmnopqrstuvwxyz")
    assert passes(scn_checker.vocalism, "", "ABCDEFGHIJKLMNOPQRSTUVWXYZ")


def test_suffixes():
    """Test that we can detect wrong suffixes."""
    scn_checker = SicilianChecker()
    assert passes(scn_checker.suffixes, "", "")
    assert fails(scn_checker.suffixes, "", "nazzioni")
    assert fails(scn_checker.suffixes, "", "cchiù azzioni")
    assert passes(scn_checker.suffixes, "razzioni", "razzioni")
    assert passes(scn_checker.suffixes, "", "nazziuni")
    assert passes(scn_checker.vocalism, "", "abcdefghijklmnopqrstuvwxyz")
    assert passes(scn_checker.vocalism, "", "ABCDEFGHIJKLMNOPQRSTUVWXYZ")
