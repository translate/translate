from translate.lang import data


def test_normalise_code() -> None:
    """Test the normalisation of language codes."""
    assert data.normalize_code("af_ZA") == "af-za"
    assert data.normalize_code("xx@Latin") == "xx-latin"


def test_simplify_to_common() -> None:
    """Test language code simplification."""
    assert data.simplify_to_common("af_ZA") == "af"
    assert data.simplify_to_common("pt_PT") == "pt"
    assert data.simplify_to_common("pt_BR") == "pt_BR"


def test_is_rtl() -> None:
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


def test_is_rtl_script_specific_codes() -> None:
    """RTL variants of languages whose base language is not RTL."""
    # Punjabi is Gurmukhi (LTR) in India and Shahmukhi (Perso-Arabic) in Pakistan
    assert data.is_rtl("pa") is False
    assert data.is_rtl("pa_PK") is True
    assert data.is_rtl("pa-PK") is True
    # Malay is Latin by default and Jawi (Perso-Arabic) when tagged as such
    assert data.is_rtl("ms") is False
    assert data.is_rtl("ms_Arab") is True
    assert data.is_rtl("ms-Arab") is True


def test_rtl_langs_are_all_reachable() -> None:
    """Every code listed in RTL_LANGS has to be detected by is_rtl()."""
    assert [code for code in sorted(data.RTL_LANGS) if not data.is_rtl(code)] == []


def test_is_rtl_perso_arabic_and_hebrew_script_languages() -> None:
    """Languages CLDR resolves to an RTL script."""
    for code in ("azb", "glk", "haz", "lki", "hno", "swb", "prs"):
        assert data.is_rtl(code) is True, code
    for code in ("jpr", "jrb", "lad"):
        assert data.is_rtl(code) is True, code
    # Tuareg varieties: CLDR resolves these to the Latin script
    for code in ("tmh", "ttq", "thv"):
        assert data.is_rtl(code) is False, code
