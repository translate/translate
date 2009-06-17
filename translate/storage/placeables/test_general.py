# -*- coding: utf-8 -*-

from translate.storage.placeables import general

def test_placeable_numbers():
    """Check the correct functioning of number placeables"""
    assert general.NumberPlaceable([u"25"]) in general.NumberPlaceable.parse(u"Here is a 25 number")
    assert general.NumberPlaceable([u"-25"]) in general.NumberPlaceable.parse(u"Here is a -25 number")
    assert general.NumberPlaceable([u"+25"]) in general.NumberPlaceable.parse(u"Here is a +25 number")

