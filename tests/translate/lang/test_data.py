from translate.lang import data


def test_normalise_code():
    """Test the normalisation of language codes."""
    assert data.normalize_code("af_ZA") == "af-za"
    assert data.normalize_code("xx@Latin") == "xx-latin"


def test_simplify_to_common():
    """Test language code simplification."""
    assert data.simplify_to_common("af_ZA") == "af"
    assert data.simplify_to_common("pt_PT") == "pt"
    assert data.simplify_to_common("pt_BR") == "pt_BR"


def test_is_rtl():
    """Test RTL language detection."""
    # RTL languages
    assert data.is_rtl("ar") is True
    assert data.is_rtl("he") is True
    assert data.is_rtl("fa") is True
    assert data.is_rtl("ur") is True
    assert data.is_rtl("yi") is True
    assert data.is_rtl("ug") is True
    assert data.is_rtl("ps") is True
    assert data.is_rtl("dv") is True

    # RTL language variants with region codes
    assert data.is_rtl("ar_EG") is True
    assert data.is_rtl("ar-EG") is True
    assert data.is_rtl("ar_SA") is True
    assert data.is_rtl("fa_AF") is True
    assert data.is_rtl("ur_IN") is True

    # LTR languages
    assert data.is_rtl("en") is False
    assert data.is_rtl("fr") is False
    assert data.is_rtl("es") is False
    assert data.is_rtl("de") is False
    assert data.is_rtl("ja") is False
    assert data.is_rtl("zh") is False
    assert data.is_rtl("ru") is False

    # Edge cases
    assert data.is_rtl("") is False
    assert data.is_rtl(None) is False
