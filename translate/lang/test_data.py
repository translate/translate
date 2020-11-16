from translate.lang import data


def test_languagematch():
    """test language comparison"""
    # Simple comparison
    assert data.languagematch("af", "af")
    assert not data.languagematch("af", "en")

    # Handle variants
    assert data.languagematch("pt", "pt_PT")
    # FIXME don't think this one is correct
    # assert not data.languagematch("sr", "sr@Latn")

    # No first language code, we just check that the other code is valid
    assert data.languagematch(None, "en")
    assert data.languagematch(None, "en_GB")
    assert data.languagematch(None, "en_GB@Latn")
    assert not data.languagematch(None, "not-a-lang-code")


def test_normalise_code():
    """test the normalisation of language codes"""
    assert data.normalize_code("af_ZA") == "af-za"
    assert data.normalize_code("xx@Latin") == "xx-latin"


def test_simplify_to_common():
    """test language code simplification"""
    assert data.simplify_to_common("af_ZA") == "af"
    assert data.simplify_to_common("pt_PT") == "pt"
    assert data.simplify_to_common("pt_BR") == "pt_BR"


def test_language_names():
    _ = data.tr_lang("en_US")
    assert _("Bokmål, Norwegian; Norwegian Bokmål") == "Norwegian Bokmål"
    assert _("Spanish; Castillian") == "Spanish"
    assert _("Mapudungun; Mapuche") == "Mapudungun"
    assert (
        _("Interlingua (International Auxiliary Language Association)") == "Interlingua"
    )


def test_language_iso_fullname():
    """Test language ISO fullnames."""
    assert data.get_language_iso_fullname("af") == "Afrikaans"
    assert data.get_language_iso_fullname("cak") == "Kaqchikel"
    assert data.get_language_iso_fullname("en_ZA") == "English (South Africa)"
    assert data.get_language_iso_fullname("pt") == "Portuguese"
    assert data.get_language_iso_fullname("pt_PT") == "Portuguese (Portugal)"
    assert data.get_language_iso_fullname("pt_BR") == "Portuguese (Brazil)"
    assert data.get_language_iso_fullname("pt_br") == "Portuguese (Brazil)"
    assert data.get_language_iso_fullname("pt-BR") == "Portuguese (Brazil)"
    assert data.get_language_iso_fullname("pt-br") == "Portuguese (Brazil)"
    assert data.get_language_iso_fullname("ca") == "Catalan"
    assert data.get_language_iso_fullname("ca@valencia") == ""
    assert data.get_language_iso_fullname("") == ""
    assert data.get_language_iso_fullname("z") == ""
    assert data.get_language_iso_fullname("zzz") == ""
    assert data.get_language_iso_fullname("zzzz") == ""
    assert data.get_language_iso_fullname("zz_BB") == ""
    assert data.get_language_iso_fullname("zz-BB") == ""
    assert data.get_language_iso_fullname("zzz_BBB") == ""
    assert data.get_language_iso_fullname("zzz_BBB") == ""


def test_country_iso_name():
    """Test country ISO names."""
    assert data.get_country_iso_name("ZA") == "South Africa"
    assert data.get_country_iso_name("PT") == "Portugal"
    assert data.get_country_iso_name("BR") == "Brazil"
    assert data.get_country_iso_name("br") == "Brazil"
    assert data.get_country_iso_name("ESP") == "Spain"
    assert data.get_country_iso_name("") == ""
    assert data.get_country_iso_name("z") == ""
    assert data.get_country_iso_name("zzz") == ""
    assert data.get_country_iso_name("zzzz") == ""

    # Use common name if available
    assert data.get_country_iso_name("TW") == "Taiwan"
    assert data.get_country_iso_name("TW") != "Taiwan, Province of China"


def test_language_iso_name():
    """Test language ISO names."""
    assert data.get_language_iso_name("af") == "Afrikaans"
    assert data.get_language_iso_name("afr") == "Afrikaans"
    assert data.get_language_iso_name("cak") == "Kaqchikel"
    assert data.get_language_iso_name("en") == "English"
    assert data.get_language_iso_name("pt") == "Portuguese"
    assert data.get_language_iso_name("") == ""
    assert data.get_language_iso_name("z") == ""
    assert data.get_language_iso_name("zzz") == ""
    assert data.get_language_iso_name("zzzz") == ""

    # Use common name if available
    assert data.get_language_iso_name("bn") == "Bangla"
    assert data.get_language_iso_name("bn") != "Bengali"
