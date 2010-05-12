#!/usr/bin/env python
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

    
