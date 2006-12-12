#!/usr/bin/env python

from translate.misc import dictutils


def test_add():
    d = dictutils.ordereddict()
    d[2] = 3
    assert len(d.order) == 1

def test_delete():
    d = dictutils.ordereddict()
    d[2] = 3
    del d[2]
    assert len(d.order) == 0
