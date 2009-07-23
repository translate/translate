# -*- coding: utf-8 -*-

from translate.storage.placeables import general

def test_placeable_numbers():
    """Check the correct functioning of number placeables"""
    assert general.NumberPlaceable([u"25"]) in general.NumberPlaceable.parse(u"Here is a 25 number")
    assert general.NumberPlaceable([u"-25"]) in general.NumberPlaceable.parse(u"Here is a -25 number")
    assert general.NumberPlaceable([u"+25"]) in general.NumberPlaceable.parse(u"Here is a +25 number")
    assert general.NumberPlaceable([u"25.00"]) in general.NumberPlaceable.parse(u"Here is a 25.00 number")
    assert general.NumberPlaceable([u"2,500.00"]) in general.NumberPlaceable.parse(u"Here is a 2,500.00 number")
    assert general.NumberPlaceable([u"1\u00a0000,99"]) in general.NumberPlaceable.parse(u"Here is a 1\u00a0000,99 number")

def test_placeable_newline():
    assert general.NewlinePlaceable.parse(u"A newline\n")[1] == general.NewlinePlaceable([u"\n"])
    assert general.NewlinePlaceable.parse(u"First\nSecond")[1] == general.NewlinePlaceable([u"\n"])

def test_placeable_alt_attr():
    assert general.AltAttrPlaceable.parse(u'Click on the <img src="image.jpg" alt="Image">')[1] == general.AltAttrPlaceable([u'alt="Image"'])

def test_placeable_qt_formatting():
    assert general.QtFormattingPlaceable.parse(u'One %1 %99 %L1 are all valid')[1] == general.QtFormattingPlaceable([u'%1'])
    assert general.QtFormattingPlaceable.parse(u'One %1 %99 %L1 are all valid')[3] == general.QtFormattingPlaceable([u'%99'])
    assert general.QtFormattingPlaceable.parse(u'One %1 %99 %L1 are all valid')[5] == general.QtFormattingPlaceable([u'%L1'])

def test_placeable_camelcase():
    assert general.CamelCasePlaceable.parse(u'CamelCase')[0] == general.CamelCasePlaceable([u'CamelCase'])
    assert general.CamelCasePlaceable.parse(u'iPod')[0] == general.CamelCasePlaceable([u'iPod'])
    assert general.CamelCasePlaceable.parse(u'DokuWiki')[0] == general.CamelCasePlaceable([u'DokuWiki'])
    assert general.CamelCasePlaceable.parse(u'KBabel')[0] == general.CamelCasePlaceable([u'KBabel'])
    assert general.CamelCasePlaceable.parse(u'_Bug') is None
    assert general.CamelCasePlaceable.parse(u'NOTCAMEL') is None

def test_placeable_space():
    assert general.SpacesPlaceable.parse(u' Space at start')[0] == general.SpacesPlaceable([u' '])
    assert general.SpacesPlaceable.parse(u'Space at end ')[1] == general.SpacesPlaceable([u' '])
    assert general.SpacesPlaceable.parse(u'Double  space')[1] == general.SpacesPlaceable([u'  '])

def test_placeable_punctuation():
    assert general.PunctuationPlaceable.parse(u'These, are not. Special: punctuation; marks! Or are "they"?') is None
    assert general.PunctuationPlaceable.parse(u'Downloading…')[1] == general.PunctuationPlaceable([u'…'])

def test_placeable_xml_entity():
    assert general.XMLEntityPlaceable.parse(u'&brandShortName;')[0] == general.XMLEntityPlaceable([u'&brandShortName;'])
    assert general.XMLEntityPlaceable.parse(u'&#1234;')[0] == general.XMLEntityPlaceable([u'&#1234;'])
    assert general.XMLEntityPlaceable.parse(u'&xDEAD;')[0] == general.XMLEntityPlaceable([u'&xDEAD;'])

def test_placeable_option():
    assert general.OptionPlaceable.parse(u'Type --help for this help')[1] == general.OptionPlaceable([u'--help'])
    assert general.OptionPlaceable.parse(u'Short -S ones also')[1] == general.OptionPlaceable([u'-S'])

# TODO: PythonFormattingPlaceable, JavaMessageFormatPlaceable, FormattingPlaceable (printf), UrlPlaceable, FilePlaceable, EmailPlaceable, CapsPlaceable, XMLTagPlaceable
