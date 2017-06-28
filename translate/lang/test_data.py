# -*- coding: utf-8 -*-

from translate.lang import data


def test_languagematch():
    """test language comparison"""
    # Simple comparison
    assert data.languagematch("af", "af")
    assert not data.languagematch("af", "en")

    # Handle variants
    assert data.languagematch("pt", "pt_PT")
    # FIXME don't think this one is correct
    #assert not data.languagematch("sr", "sr@Latn")

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
    _ = data.tr_lang('en_US')
    assert _(u"Bokmål, Norwegian; Norwegian Bokmål") == u"Norwegian Bokmål"
    assert _(u"Spanish; Castillian") == u"Spanish"
    assert _(u"Mapudungun; Mapuche") == u"Mapudungun"
    assert _(u"Interlingua (International Auxiliary Language Association)") == u"Interlingua"


def test_language_iso_fullname():
    """Test language ISO fullnames."""
    assert data.get_language_iso_fullname("af") == u'Afrikaans'
    assert data.get_language_iso_fullname("cak") == u'Kaqchikel'
    assert data.get_language_iso_fullname("en_ZA") == u'English (South Africa)'
    assert data.get_language_iso_fullname("pt") == u'Portuguese'
    assert data.get_language_iso_fullname("pt_PT") == u'Portuguese (Portugal)'
    assert data.get_language_iso_fullname("pt_BR") == u'Portuguese (Brazil)'
    assert data.get_language_iso_fullname("pt_br") == u'Portuguese (Brazil)'
    assert data.get_language_iso_fullname("pt-BR") == u'Portuguese (Brazil)'
    assert data.get_language_iso_fullname("pt-br") == u'Portuguese (Brazil)'
    assert data.get_language_iso_fullname("ca") == u'Catalan'
    assert data.get_language_iso_fullname("ca@valencia") == u''
    assert data.get_language_iso_fullname("") == u''
    assert data.get_language_iso_fullname("z") == u''
    assert data.get_language_iso_fullname("zzz") == u''
    assert data.get_language_iso_fullname("zzzz") == u''
    assert data.get_language_iso_fullname("zz_BB") == u''
    assert data.get_language_iso_fullname("zz-BB") == u''
    assert data.get_language_iso_fullname("zzz_BBB") == u''
    assert data.get_language_iso_fullname("zzz_BBB") == u''


def test_country_iso_name():
    """Test country ISO names."""
    assert data.get_country_iso_name("ZA") == u'South Africa'
    assert data.get_country_iso_name("PT") == u'Portugal'
    assert data.get_country_iso_name("BR") == u'Brazil'
    assert data.get_country_iso_name("br") == u'Brazil'
    assert data.get_country_iso_name("ESP") == u'Spain'
    assert data.get_country_iso_name("") == u''
    assert data.get_country_iso_name("z") == u''
    assert data.get_country_iso_name("zzz") == u''
    assert data.get_country_iso_name("zzzz") == u''

    # Use common name if available
    assert data.get_country_iso_name("TW") == u'Taiwan'
    assert data.get_country_iso_name("TW") != u'Taiwan, Province of China'


def test_language_iso_name():
    """Test language ISO names."""
    assert data.get_language_iso_name("af") == u'Afrikaans'
    assert data.get_language_iso_name("afr") == u'Afrikaans'
    assert data.get_language_iso_name("cak") == u'Kaqchikel'
    assert data.get_language_iso_name("en") == u'English'
    assert data.get_language_iso_name("pt") == u'Portuguese'
    assert data.get_language_iso_name("") == u''
    assert data.get_language_iso_name("z") == u''
    assert data.get_language_iso_name("zzz") == u''
    assert data.get_language_iso_name("zzzz") == u''

    # Use common name if available
    assert data.get_language_iso_name("bn") == u'Bangla'
    assert data.get_language_iso_name("bn") != u'Bengali'
