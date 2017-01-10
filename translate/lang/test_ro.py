# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from translate.lang.ro import RomanianChecker


def test_cedillas():
    """Test that we can detect cedillas."""
    ro_checker = RomanianChecker()
    assert ro_checker.cedillas("", "") is False
    assert ro_checker.cedillas("", "blaŢbla") is True
    assert ro_checker.cedillas("", "blaŞbla") is True
    assert ro_checker.cedillas("", "blaţbla") is True
    assert ro_checker.cedillas("", "blaşbla") is True
    assert ro_checker.cedillas("", "blaŢblaŞblaţblaşbla']") is True
    assert ro_checker.cedillas("", "blașțăâîȘȚĂÂÎbla") is False
    assert ro_checker.cedillas("", "abcdefghijklmnopqrstuvwxyz") is False
    assert ro_checker.cedillas("", "ABCDEFGHIJKLMNOPQRSTUVWXYZ") is False


def test_niciun():
    """Test that we can detect niciun/nicio."""
    ro_checker = RomanianChecker()
    assert ro_checker.niciun_nicio("", "") is False
    assert ro_checker.niciun_nicio("", "bla nici un bla") is True
    assert ro_checker.niciun_nicio("", "bla nici o bla") is True
    assert ro_checker.niciun_nicio("", "bla niciun bla") is False
    assert ro_checker.niciun_nicio("", "bla nicio bla") is False
    assert ro_checker.niciun_nicio("", "abcdefghijklmnopqrstuvwxyz") is False
    assert ro_checker.niciun_nicio("", "ABCDEFGHIJKLMNOPQRSTUVWXYZ") is False
