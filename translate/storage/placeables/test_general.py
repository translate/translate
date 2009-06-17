# -*- coding: utf-8 -*-

from translate.storage.placeables import general

def test_placeable_numbers():
    """Check the correct functioning of number placeables"""
    assert general.NumberPlaceable([u"25"]) in general.NumberPlaceable.parse(u"Here is a 25 number")
    assert general.NumberPlaceable([u"-25"]) in general.NumberPlaceable.parse(u"Here is a -25 number")
    assert general.NumberPlaceable([u"+25"]) in general.NumberPlaceable.parse(u"Here is a +25 number")

def test_placeable_newline():
    assert general.NewlinePlaceable.parse(u"A newline\n")[1] == general.NewlinePlaceable([u"\n"])
    assert general.NewlinePlaceable.parse(u"First\nSecond")[1] == general.NewlinePlaceable([u"\n"])
