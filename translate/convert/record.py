#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2004-2006 Zuza Software Foundation
#
# Derived from http://www.valuedlessons.com/2007/12/immutable-data-in-python-record-or.html
# This file is part of translate.
#
# translate is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# translate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with translate; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

def Record(*props):
    class cls(RecordBase):
        pass

    cls.setProps(props)

    return cls

class RecordBase(tuple):
    PROPS = ()

    def __new__(cls, *values):
        if cls.prepare != RecordBase.prepare:
            values = cls.prepare(*values)
        return cls.fromValues(values)

    @classmethod
    def fromValues(cls, values):
        return tuple.__new__(cls, values)

    def __repr__(self):
        return self.__class__.__name__ + tuple.__repr__(self)

    ## overridable
    @classmethod
    def prepare(cls, *args):
        return args

    ## setting up getters and setters
    @classmethod
    def setProps(cls, props):
        for index, prop in enumerate(props):
            cls.setProp(index, prop)
        cls.PROPS = props

    @classmethod
    def setProp(cls, index, prop):
        getter_name = prop
        setter_name = "set" + prop[0].upper() + prop[1:]

        setattr(cls, getter_name, cls.makeGetter(index, prop))
        setattr(cls, setter_name, cls.makeSetter(index, prop))

    @classmethod
    def makeGetter(cls, index, prop):
        return property(fget = lambda self : self[index])

    @classmethod
    def makeSetter(cls, index, prop):
        def setter(self, value):
            new_tuple = list(self)
            new_tuple[index] = value
            return self.fromValues(new_tuple)
        return setter

    def alter(self, **kwargs):
        new_tuple = list(self)
        for index, prop in enumerate(self.PROPS):
            if prop in kwargs:
                  new_tuple[index] = kwargs[prop]
        return self.fromValues(new_tuple)

    #def alter
