# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from translate.lang.ro import RomanianChecker


def test_cedillas():
    """Tests that we can detect cedillas."""
    language = RomanianChecker()
    assert language.cedillas("", "blaŢbla") is True
    assert language.cedillas("", "blaŞbla") is True
    assert language.cedillas("", "blaţbla") is True
    assert language.cedillas("", "blaşbla") is True
    assert language.cedillas("", "blaŢblaŞblaţblaşbla']") is True
    assert language.cedillas("", "blașțăâîȘȚĂÂÎbla") is False
    assert language.cedillas("", "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ") is False
