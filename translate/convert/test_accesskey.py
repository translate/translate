from translate.convert import accesskey

from py import test

def test_getlabel():
    """test that we can extract the label component of an accesskey+label string"""
    assert accesskey.getlabel("&File") == "File"
    assert accesskey.getlabel("&File") != "F"

def test_getaccesskey():
    """test that we can extract the accesskey component of an accesskey+label string"""
    assert accesskey.getaccesskey("&File") == "F"
    assert accesskey.getaccesskey("&File") != "File"

def test_ignore_entities():
    """test that we don't get confused with entities and a & access key marker"""
    assert accesskey.getaccesskey("Set &browserName; as &Default") != "b"
    assert accesskey.getaccesskey("Set &browserName; as &Default") == "D"
 
def test_alternate_accesskey_marker():
    """check that we can identify the accesskey if the marker is different"""
    assert accesskey.getlabel("~File", "~") == "File"
    assert accesskey.getlabel("&File", "~") == "&File"
    assert accesskey.getaccesskey("~File", "~") == "F"
    assert accesskey.getaccesskey("&File", "~") == ""
