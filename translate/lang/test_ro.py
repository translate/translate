# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from translate.lang.ro import RomanianChecker


def test_cedillas():
    """Tests that we can detect cedillas."""
    language = RomanianChecker()

    assert language.cedillas("", "") is False
    assert language.cedillas("", "blaŢbla") is True
    assert language.cedillas("", "blaŞbla") is True
    assert language.cedillas("", "blaţbla") is True
    assert language.cedillas("", "blaşbla") is True
    assert language.cedillas("", "blaŢblaŞblaţblaşbla']") is True
    assert language.cedillas("", "blașțăâîȘȚĂÂÎbla") is False
    assert language.cedillas("", "abcdefghijklmnopqrstuvwxyz") is False
    assert language.cedillas("", "ABCDEFGHIJKLMNOPQRSTUVWXYZ") is False

    assert language.niciun_nicio("", "bla nici un bla") is True
    assert language.niciun_nicio("", "bla nici o bla") is True
    assert language.niciun_nicio("", "bla niciun bla") is False
    assert language.niciun_nicio("", "bla nicio bla") is False
    assert language.niciun_nicio("", "abcdefghijklmnopqrstuvwxyz") is False
    assert language.niciun_nicio("", "ABCDEFGHIJKLMNOPQRSTUVWXYZ") is False
