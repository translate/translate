#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2008 Zuza Software Foundation
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

"""Module to provide a translation memory database."""

from translate.search.lshtein import LevenshteinComparer

try:
    from pysqlite2 import dbapi2
except ImportError:
    from sqlite3 import dbapi2
import os.path


def transaction(f):
    """Modifies f to commit database changes if it executes without exceptions.
    Otherwise it rolls back the database.

    ALL publicly accessible methods in TMDB MUST be decorated with this
    decorator.
    """

    def decorated_f(self, *args, **kwargs):
        try:
            result = f(self, *args, **kwargs)
            self.con.commit()
            return result
        except:
            # If ANY exception is raised, we're left in an
            # uncertain state and we MUST roll back any changes to avoid getting
            # stuck in an inconsistent state.
            self.con.rollback()
            raise
    return decorated_f


# ALL PUBLICLY ACCESSIBLE METHODS MUST BE DECORATED WITH THE transaction DECORATOR.
class TMDB(object):
    """An object instantiated as a singleton for each database file that provides
    access to the database from a pool of TMDB objects."""
    _tm_dbs = {}
    defaultfile = None
    con = None
    """This db's connection"""
    cur = None
    """The current cursor"""

    def __new__(cls, db_file=None):
        def make_database(db_file):
            def connect(db):
                db.con = dbapi2.connect(db_file)
                db.cur = db.con.cursor()

            def clear_old_data(db):
                try:
                    #TODO: do some query to see if the DB is in the right
                    #schema. If not, remove it here and return True.
                    return False
                except dbapi2.OperationalError:
                    return False

            db = cls._tm_dbs[db_file] = object.__new__(cls)
            connect(db)
            if clear_old_data(db):
                connect(db)
            db.create()
            db.MIN_SIMILARITY = 70
            db.MAX_LENGTH = 1000
            db.comparer = LevenshteinComparer(db.MAX_LENGTH)
            return db

        if not db_file:
            if not cls.defaultfile:
                userdir = os.path.expanduser("~")
                dbdir = None
                if os.name == "nt":
                    dbdir = os.path.join(userdir, "Translate Toolkit")
                else:
                    dbdir = os.path.join(userdir, ".translate_toolkit")
                if not os.path.exists(dbdir):
                    os.mkdir(dbdir)
                cls.defaultfile = os.path.realpath(os.path.join(dbdir, "tm.db"))
            db_file = cls.defaultfile
        else:
            db_file = os.path.realpath(db_file)
        # First see if a db for this file already exists:
        if db_file in cls._tm_dbs:
            return cls._tm_dbs[db_file]
        # No existing db. Let's build a new one and keep a copy
        return make_database(db_file)

    def create(self):
        """Create all tables and indexes."""

        # Create Data table
        # TODO: msgctxt
        # TODO: review the missing NOT NULLS
        self.cur.execute("""CREATE TABLE IF NOT EXISTS data(
            data_id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id INTEGER NOT NULL,
            matched_source_id INTEGER NOT NULL,
            target_id INTEGER NOT NULL,
            source_lang_id INTEGER NOT NULL,
            target_lang_id INTEGER NOT NULL,
            match INTEGER NOT NULL,
            ref_count INTEGER);""")

        self.cur.execute("""CREATE INDEX IF NOT EXISTS data_source_idx
            ON data (source_id);""")
#        self.cur.execute("""CREATE INDEX IF NOT EXISTS data_matched_source_idx
#            ON data (matched_source_id);""")
        self.cur.execute("""CREATE INDEX IF NOT EXISTS data_target_idx
            ON data (target_id);""")
#        self.cur.execute("""CREATE INDEX IF NOT EXISTS data_source_lang_idx
#            ON data (source_lang_id);""")
#        self.cur.execute("""CREATE INDEX IF NOT EXISTS data_target_lang_idx
#            ON data (target_lang_id);""")

        self.cur.execute("""CREATE TABLE IF NOT EXISTS load(
            load_id INTEGER PRIMARY KEY AUTOINCREMENT,
            source VARCHAR NOT NULL,
            target VARCHAR,
            context VARCHAR,
            source_lang VARCHAR NOT NULL,
            target_lang VARCHAR NOT NULL);""")

        self.cur.execute("""CREATE TABLE IF NOT EXISTS texts(
            text_id INTEGER PRIMARY KEY AUTOINCREMENT,
            string VARCHAR NOT NULL,
            context VARCHAR,
            lang VARCHAR NOT NULL,
            len INTEGER NOT NULL);""")

        self.cur.execute("""CREATE INDEX IF NOT EXISTS text_string_idx
            ON texts (string);""")
        self.cur.execute("""CREATE INDEX IF NOT EXISTS text_len_idx
            ON texts (len);""")

        # TODO load from a table of ISO codes
        self.cur.execute("""CREATE TABLE IF NOT EXISTS lang(
            iso VARCHAR PRIMARY KEY,
            name VARCHAR);""")

    create = transaction(create)

    def load_data(self, source, target, context, source_lang, target_lang):
        self.cur.execute("""INSERT INTO load
                (source, target, context, source_lang, target_lang)
                VALUES (?,?,?,?,?);""", (source, target, context, source_lang, target_lang))
    load_data = transaction(load_data)

    def bulk_load_data(self, inserts):
        self.cur.executemany("""INSERT INTO load
                (source, target, context, source_lang, target_lang)
                VALUES (?,?,?,?,?);""", inserts)
    bulk_load_data = transaction(bulk_load_data)

    def populate_from_load(self):
        """populate the data table with newly loaded data"""

        def insert_languages():
            """Insert potentially new languages into the language table"""
            self.cur.execute("""INSERT OR IGNORE INTO lang(iso)
                    SELECT DISTINCT source_lang FROM load;""")
            self.cur.execute("""INSERT OR IGNORE INTO lang(iso)
                    SELECT DISTINCT target_lang FROM load;""")

        def insert_texts():
            """Insert all distinct strings from the load table into the texts table."""
            self.cur.execute("""INSERT INTO texts(string, len, lang)
                    SELECT DISTINCT source, length(source), source_lang FROM load;""")
            self.cur.execute("""INSERT INTO texts(string, len, lang)
                    SELECT DISTINCT target, length(target), target_lang FROM load;""")

        def insert_data(source_id, matched_id, target, source_lang, target_lang, match):
            """Insert a row into the data table."""
            cur = self.con.cursor()
            cur.execute("""INSERT INTO
                 data(source_id, matched_source_id, target_id, source_lang_id,
                 target_lang_id, match, ref_count)
                 SELECT ?, ?, text_id, ?, ?, ?, 1 FROM texts
                 WHERE string=? AND lang=? LIMIT 1;""",
                 (source_id, matched_id, source_lang, target_lang, match, target, target_lang))

        def process_new_load_row(row):
            """Handles one row from the load table."""
            # TODO handle plurals
            # TODO segmentation
            # TODO we should be storing the backwards match
            row_id, source, target, context, source_lang, target_lang = row
            cur = self.con.cursor()
            source_text_id = cur.execute("""SELECT text_id FROM texts
                    WHERE string=? LIMIT 1;""", (source,)).fetchone()[0]
            source_data = cur.execute("""SELECT * FROM data
                    WHERE source_id=? LIMIT 1;""", (source_text_id,)).fetchone()
            # TODO - we aren't storing anything that doesn't have a match to 
            #something else of > self.MIN_SIMILARITY

            if source_data is not None:
#                print "Don't need to do calculation - source already exists"
                target_text_id = cur.execute("""SELECT text_id FROM texts
                        WHERE string=? LIMIT 1;""", (target,)).fetchone()[0]
                refcount = cur.execute("""SELECT ref_count FROM data
                        WHERE source_id=? AND target_id=? LIMIT 1;""",
                        (source_text_id, target_text_id)).fetchone()
                if refcount is not None:
#                    print "Increase reference count - target is the same"
                    cur.execute("""UPDATE data SET ref_count=?
                            WHERE source_id=? AND target_id=?;""",
                            (refcount[0] + 1, source_text_id, target_text_id))
                else:
#                    print "Copy existing records - target is different"
                    #TODO: be more specific about language here to find the target
                    marker_id = source_data[3]
                    cur.execute("""INSERT INTO data
                    (source_id, matched_source_id, target_id,
                    source_lang_id, target_lang_id, match, ref_count)
                    SELECT source_id, matched_source_id, ?,
                    source_lang_id, target_lang_id, match, 1
                    FROM data WHERE source_id=? AND target_id=?;""",
                    (target_text_id, source_text_id, marker_id))

            else:
#                print "Calculate distance measurements - new record"
                min_similarity = self.MIN_SIMILARITY
                source_l = len(source)
                min_length = max(source_l * (min_similarity/100.0), 2)
                max_length = min(source_l / (min_similarity/100.0), self.MAX_LENGTH)
                candidates = cur.execute("""SELECT text_id, string FROM texts
                        WHERE (len BETWEEN ? AND ?) AND lang=? ORDER BY len ASC;""",
                        (min_length, max_length, source_lang))
                inserts = []
                new_cur = self.con.cursor()
                for candidate in candidates:
                    match = self.comparer.similarity(source, candidate[1])
                    if match >= min_similarity:
                        target_id = new_cur.execute("""SELECT text_id FROM texts
                                WHERE string=? AND lang=? LIMIT 1;""",
                                (target, target_lang)).fetchone()[0]
                        inserts.append((source_text_id, candidate[0], target_id, source_lang, target_lang, match))
                cur.executemany("""INSERT INTO data(
                    source_id, matched_source_id, target_id,
                    source_lang_id, target_lang_id, match, ref_count)
                    VALUES (?,?,?,?,?,?,1);""", inserts)

        def delete_load(load_id):
            cur = self.con.cursor()
            cur.execute("""DELETE FROM load WHERE
                load_id=?;""", (load_id,))

        insert_texts()
        insert_languages()
        cur = self.con.cursor()
        for row in self.cur.execute("""SELECT * FROM load ORDER BY length(source) ASC;"""):
            process_new_load_row(row)
            delete_load(row[0])
    populate_from_load = transaction(populate_from_load)
