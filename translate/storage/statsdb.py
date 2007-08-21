#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2007 Zuza Software Foundation
# 
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

"""Module to provide a cache of statistics in a database.

@organization: Zuza Software Foundation
@copyright: 2007 Zuza Software Foundation
@license: U{GPL <http://www.fsf.org/licensing/licenses/gpl.html>}
"""

from translate import __version__ as toolkitversion
from translate.storage import factory
from translate.misc.multistring import multistring
from translate.lang.common import Common

try:
    from sqlite3 import dbapi2
except ImportError:
    from pysqlite2 import dbapi2
import os.path
import re

kdepluralre = re.compile("^_n: ")
brtagre = re.compile("<br\s*?/?>")
xmltagre = re.compile("<[^>]+>")
numberre = re.compile("\\D\\.\\D")

def wordcount(string):
    # TODO: po class should understand KDE style plurals
    string = kdepluralre.sub("", string)
    string = brtagre.sub("\n", string)
    string = xmltagre.sub("", string)
    string = numberre.sub(" ", string)
    #TODO: This should still use the correct language to count in the target 
    #language
    return len(Common.words(string))

def wordsinunit(unit):
    """Counts the words in the unit's source and target, taking plurals into 
    account. The target words are only counted if the unit is translated."""
    (sourcewords, targetwords) = (0, 0)
    if isinstance(unit.source, multistring):
        sourcestrings = unit.source.strings
    else:
        sourcestrings = [unit.source or ""]
    for s in sourcestrings:
        sourcewords += wordcount(s)
    if not unit.istranslated():
        return sourcewords, targetwords
    if isinstance(unit.target, multistring):
        targetstrings = unit.target.strings
    else:
        targetstrings = [unit.target or ""]
    for s in targetstrings:
        targetwords += wordcount(s)
    return sourcewords, targetwords

def statefordb(unit):
    """Returns the numeric database state for the unit."""
    if unit.istranslated():
        return 1
    if unit.isfuzzy() and unit.target:
        return 2
    return 0

def statefromdb(state):
    """Converts a database state number to the text version."""
    if state == 1:
        return "translated"
    if state == 2:
        return "fuzzy"
    return "untranslated"

def emptystats():
    """Returns a dictionary with all statistics initalised to 0."""
    stats = {}
    for state in ["total", "translated", "fuzzy", "untranslated", "review"]:
        stats[state] = 0
        stats[state + "sourcewords"] = 0
        stats[state + "targetwords"] = 0
    return stats

class StatsCache:

    def __init__(self, statsfile=None):
        if not statsfile:
            userdir = os.path.expanduser("~")
            cachedir = os.path.join(userdir, ".wordforge")
            if not os.path.exists(cachedir):
                os.mkdir(cachedir)
            statsfile = os.path.join(cachedir, "stats.db")
        self.con = dbapi2.connect(statsfile)
        self.cur = self.con.cursor()
        self.create()

    def create(self):
        """Create all tables and indexes."""
        self.cur.execute("""CREATE TABLE IF NOT EXISTS files(
            fileid INTEGER PRIMARY KEY AUTOINCREMENT,
            path VARCHAR NOT NULL UNIQUE,
            mtime INTEGER NOT NULL,
            toolkitbuild INTEGER NOT NULL);""")

        self.cur.execute("""CREATE UNIQUE INDEX IF NOT EXISTS filepathindex
            ON files (path);""")

        self.cur.execute("""CREATE TABLE IF NOT EXISTS units(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            unitid VARCHAR NOT NULL,
            fileid INTEGER NOT NULL,
            unitindex INTEGER NOT NULL,
            source VARCHAR NOT NULL,
            target VARCHAR,
            state INTEGER,
            sourcewords INTEGER,
            targetwords INTEGER);""")
        
        self.cur.execute("""CREATE INDEX IF NOT EXISTS fileidindex
            ON units(fileid);""")

        self.cur.execute("""CREATE TABLE IF NOT EXISTS checkerconfigs(
            configid INTEGER PRIMARY KEY AUTOINCREMENT,
            config VARCHAR);""")

        self.cur.execute("""CREATE INDEX IF NOT EXISTS configindex
            ON checkerconfigs(config);""")

        self.cur.execute("""CREATE TABLE IF NOT EXISTS uniterrors(
            errorid INTEGER PRIMARY KEY AUTOINCREMENT,
            unitindex INTEGER NOT NULL,
            fileid INTEGER NOT NULL,
            configid INTEGER NOT NULL,
            name VARCHAR NOT NULL,
            message VARCHAR);""")

        self.cur.execute("""CREATE INDEX IF NOT EXISTS uniterrorindex
            ON uniterrors(fileid, configid);""")
        
        self.con.commit()

    def _getstoredfileid(self, filename):
        """Attempt to find the fileid of the given file, if it hasn't been
        updated since the last record update.

        None is returned if either the file's record is not found, or if it is
        not up to date.

        @rtype: String or None
        """
        absolutepath = os.path.abspath(filename)
        mtime = os.path.getmtime(absolutepath)
        self.cur.execute("SELECT fileid, mtime FROM files WHERE path=?;", (absolutepath,))
        filerow = self.cur.fetchone()
        if not filerow or filerow[1] != mtime:
            return None
        else:
            return filerow[0]

    def _getstoredcheckerconfig(self, checker):
        """See if this checker configuration has been used before."""
        config = str(checker.config.__dict__)
        self.cur.execute("""SELECT configid, config FROM checkerconfigs WHERE 
            config=?;""", (config,))
        configrow = self.cur.fetchone()
        if not configrow or configrow[1] != config:
            return None
        else:
            return configrow[0]

    def cachestore(self, store):
        """Calculates and caches the statistics of the given store 
        unconditionally."""
        absolutepath = os.path.abspath(store.filename)
        mtime = os.path.getmtime(absolutepath)
        self.cur.execute("""DELETE FROM files WHERE
            path=?;""", (absolutepath,))
        self.cur.execute("""INSERT INTO files 
            (fileid, path, mtime, toolkitbuild) values (NULL, ?, ?, ?);""", 
            (absolutepath, mtime, toolkitversion.build))
        fileid = self.cur.lastrowid
        unitvalues = []
        for index, unit in enumerate(store.units):
            if unit.istranslatable():
                sourcewords, targetwords = wordsinunit(unit)
                
                # what about plurals in .source and .target?
                unitvalues.append((unit.getid(), fileid, index, \
                                unit.source, unit.target, \
                                sourcewords, targetwords, \
                                statefordb(unit)))

        self.cur.execute("""DELETE FROM units WHERE
            fileid=?""", (fileid,))
        # executemany is non-standard
        self.cur.executemany("""INSERT INTO units
            (unitid, fileid, unitindex, source, target, sourcewords, targetwords, state) 
            values (?, ?, ?, ?, ?, ?, ?, ?);""",
            unitvalues)
        self.con.commit()
        return fileid

    def filetotals(self, filename):
        """Retrieves the statistics for the given file if possible, otherwise 
        delegates to cachestore()."""
        fileid = self._getstoredfileid(filename)
        if not fileid:
            try:
                store = factory.getobject(filename)
                fileid = self.cachestore(store)
            except ValueError, e:
                print str(e)
                return {}

        self.cur.execute("""SELECT 
            state,
            count(unitid) as total,
            sum(sourcewords) as sourcewords,
            sum(targetwords) as targetwords
            FROM units WHERE fileid=?
            GROUP BY state;""", (fileid,))
        values = self.cur.fetchall()

        totals = emptystats()
        for stateset in values:
            state = statefromdb(stateset[0])            # state
            totals[state] = stateset[1] or 0            # total
            totals[state + "sourcewords"] = stateset[2] # sourcewords
            totals[state + "targetwords"] = stateset[3] # targetwords
        totals["total"] = totals["untranslated"] + totals["translated"] + totals["fuzzy"]
        totals["totalsourcewords"] = totals["untranslatedsourcewords"] + \
                totals["translatedsourcewords"] + \
                totals["fuzzysourcewords"]
        return totals

    def cachestorechecks(self, fileid, store, checker, configid):
        """Calculates and caches the error statistics of the given store 
        unconditionally."""
        # We always want to store one dummy error to know that we have actually
        # run the checks on this file with the current checker configuration
        unitvalues = [(-1, fileid, configid, "noerror", "")]
        for index, unit in enumerate(store.units):
            if unit.istranslatable():
                failures = checker.run_filters(unit)
                for failure in failures:
                    unitvalues.append((index, fileid, configid, failure[0], failure[1]))

        self.cur.execute("""DELETE FROM uniterrors WHERE
            fileid=?""", (fileid,))
        # executemany is non-standard
        self.cur.executemany("""INSERT INTO uniterrors
            (unitindex, fileid, configid, name, message) 
            values (?, ?, ?, ?, ?);""",
            unitvalues)
        self.con.commit()
        return fileid

    def filechecks(self, filename, checker, store=None):
        """Retrieves the error statistics for the given file if possible, 
        otherwise delegates to cachestorechecks()."""
        fileid = self._getstoredfileid(filename)
        configid = self._getstoredcheckerconfig(checker)
        try:
            if not fileid:
                store = store or factory.getobject(filename)
                fileid = self.cachestore(store)
            if not configid:
                self.cur.execute("""INSERT INTO checkerconfigs
                    (configid, config) values (NULL, ?);""", 
                    (str(checker.config.__dict__),))
                configid = self.cur.lastrowid
        except ValueError, e:
            print str(e)
            return {}

        def geterrors():
            self.cur.execute("""SELECT 
                name,
                unitindex
                FROM uniterrors WHERE fileid=? and configid=?
                ORDER BY unitindex;""", (fileid, configid))
            return self.cur.fetchall()

        values = geterrors()
        if not values:
            # This could happen if we haven't done the checks before, or we the
            # file changed, or we are using a different configuration
            store = store or factory.getobject(filename)
            self.cachestorechecks(fileid, store, checker, configid)
            values = geterrors()

        errors = {}
        for value in values:
            if value[1] == -1:
                continue
            checkkey = 'check-' + value[0]      #value[0] is the error name
            if not checkkey in errors:
                errors[checkkey] = []
            errors[checkkey].append(value[1])   #value[1] is the unitindex

        return errors

    def filestats(self, filename, checker, store=None):
        """complete stats"""
        stats = {"total": [], "translated": [], "fuzzy": [], "untranslated": []}

        stats.update(self.filechecks(filename, checker, store))
        fileid = self._getstoredfileid(filename)

        self.cur.execute("""SELECT 
            state,
            unitindex
            FROM units WHERE fileid=?
            ORDER BY unitindex;""", (fileid,))

        values = self.cur.fetchall()
        for value in values:
            stats[statefromdb(value[0])].append(value[1])
            stats["total"].append(value[1])

        return stats
