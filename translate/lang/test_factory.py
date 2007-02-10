#!/usr/bin/env python
# -*- coding: utf-8 -*-

from translate.lang import factory

def test_getlanguage():
    """Tests that a basic call to getlanguage() works."""
    kmlanguage = factory.getlanguage('km')
    assert kmlanguage.code == 'km'
    assert kmlanguage.fullname == 'Khmer'
    
    language = factory.getlanguage('zz')
    assert language.code == ''
