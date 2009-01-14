#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2008 Zuza Software Foundation
#
# This file is part of Virtaal.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""Build the TM database."""

from translate.storage import factory
from translate.storage import tmdb
import sys
import os


def do_thing(filename, db):
    try:
        store = factory.getobject(filename)
    except ValueError, e:
        print >> sys.stderr, str(e)
        return
    # do something useful with the store and db
    try:
        db.add_store(store, "en-US", "ar", commit=False)
    except Exception, e:
        print e
    print "new file:", filename


class Builder:
    def __init__(self, filenames):
        self.db = tmdb.TMDB("test.db")
        for filename in filenames:
            if not os.path.exists(filename):
                print >> sys.stderr, "cannot process %s: does not exist" % filename
                continue
            elif os.path.isdir(filename):
                self.handledir(filename)
            else:
                self.handlefile(filename)
        self.db.connection.commit()

    def handlefile(self, filename):
#        try:
        if True:
            do_thing(filename, self.db)
#        except: # This happens if we have a broken file.
#            print >> sys.stderr, sys.exc_info()[1]

    def handlefiles(self, dirname, filenames):
        for filename in filenames:
            pathname = os.path.join(dirname, filename)
            if os.path.isdir(pathname):
                self.handledir(pathname)
            else:
                self.handlefile(pathname)

    def handledir(self, dirname):
        path, name = os.path.split(dirname)
        if name in ["CVS", ".svn", "_darcs", ".git", ".hg", ".bzr"]:
            return
        entries = os.listdir(dirname)
        self.handlefiles(dirname, entries)

def main():
    try:
        import psyco
        psyco.full()
    except Exception:
        pass
    Builder(sys.argv[1:])

if __name__ == '__main__':
    main()
