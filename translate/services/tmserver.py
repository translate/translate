#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2008 Zuza Software Foundation
#
# This file is part of translate.
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

"""A translation memory server using REST and JSON."""

import urllib
from optparse import OptionParser
import simplejson as json
from wsgiref.simple_server import make_server

from translate.misc import selector
from translate.search import match
from translate.storage import factory
from translate.storage import base
from translate.storage import tmdb

class TMServer:
    """a RESTful JSON TM server"""
    def __init__(self, tmdbfile, tmfiles, max_candidates=3, min_similarity=75, max_length=1000, prefix="", source_lang=None, target_lang=None):

        self.tmdb = tmdb.TMDB(tmdbfile, max_candidates, min_similarity, max_length)

        #load files into db
        if isinstance(tmfiles, list):
            [self.tmdb.add_store(factory.getobject(tmfile), source_lang, target_lang) for tmfile in tmfiles]
        elif tmfiles:
            self.tmdb.add_store(factory.getobject(tmfiles), source_lang, target_lang)

        #initialize url dispatcher
        self.rest = selector.Selector(prefix=prefix)
        self.rest.add("/{slang}/{tlang}/unit/{uid:any}",
                      GET=self.get_suggestions,
                      POST=self.update_unit,
                      PUT=self.add_unit,
                      DELETE=self.forget_unit
                      )

        self.rest.add("/store/{sid:any}", GET=self.get_store_stats)
        self.rest.add("/store/{sid:any}", POST=self.add_store)
        self.rest.add("/store/{sid:any}", PUT=self.upload_store)
        self.rest.add("/store/{sid:any}", DELETE=self.forget_store)

    @selector.opliant
    def get_suggestions(self, environ, start_response, uid, slang, tlang):
        start_response("200 OK", [('Content-type', 'text/plain')])
        uid = unicode(urllib.unquote_plus(uid),"utf-8")
        candidates = self.tmdb.translate_unit(uid, slang, tlang)
        response =  json.dumps(candidates, indent=4)
        return [response]

    @selector.opliant
    def add_unit(self, environ, start_response, uid, slang, tlang):
        start_response("200 OK", [('Content-type', 'text/plain')])
        uid = unicode(urllib.unquote_plus(uid),"utf-8")
        data = json.loads(environ['wsgi.input'].read(int(environ['CONTENT_LENGTH'])))
        unit = base.TranslationUnit(data['source'])
        unit.target = data['target']
        self.tmdb.add_unit(unit, slang, tlang)
        return [""]

    @selector.opliant
    def update_unit(self, environ, start_response, uid, slang, tlang):
        start_response("200 OK", [('Content-type', 'text/plain')])
        uid = unicode(urllib.unquote_plus(uid),"utf-8")
        data = json.loads(environ['wsgi.input'].read(int(environ['CONTENT_LENGTH'])))
        unit = base.TranslationUnit(data['source'])
        unit.target = data['target']
        self.tmdb.add_unit(unit, slang, tlang)
        return [""]

    @selector.opliant
    def forget_unit(self, environ, start_response, uid):
        #FIXME: implement me
        start_response("200 OK", [('Content-type', 'text/plain')])
        uid = unicode(urllib.unquote_plus(uid),"utf-8")

        return [response]

    @selector.opliant
    def get_store_stats(self, environ, start_response, sid):
        #FIXME: implement me
        start_response("200 OK", [('Content-type', 'text/plain')])
        sid = unicode(urllib.unquote_plus(sid),"utf-8")

        return [response]

    @selector.opliant
    def upload_store(self, environ, start_response, sid):
        #FIXME: implement me
        start_response("200 OK", [('Content-type', 'text/plain')])
        sid = unicode(urllib.unquote_plus(sid),"utf-8")
        data = json.loads(environ['wsgi.input'].read(int(environ['CONTENT_LENGTH'])))
        return [response]

    @selector.opliant
    def add_store(self, environ, start_response, sid):
        #FIXME: implement me
        start_response("200 OK", [('Content-type', 'text/plain')])
        sid = unicode(urllib.unquote_plus(sid),"utf-8")
        data = json.loads(environ['wsgi.input'].read(int(environ['CONTENT_LENGTH'])))
        return [response]

    @selector.opliant
    def forget_store(self, environ, start_response, sid):
        #FIXME: implement me
        start_response("200 OK", [('Content-type', 'text/plain')])
        sid = unicode(urllib.unquote_plus(sid),"utf-8")

        return [response]


def main():
    parser = OptionParser()
    parser.add_option("-d", "--tmdb", dest="tmdbfile", default=":memory:",
                      help="translation memory database file")
    parser.add_option("-f", "--import-translation-file", dest="tmfiles", action="append",
                      help="translation file to import into the database")
    parser.add_option("-t", "--import-target-lang", dest="target_lang",
                      help="target language of translation files")
    parser.add_option("-s", "--import-source-lang", dest="source_lang",
                      help="source language of translation files")
    parser.add_option("-b", "--bind", dest="bind",
                      help="adress to bind server to")
    parser.add_option("-p", "--port", dest="port", type="int",
                      help="port to listen on")

    (options, args) = parser.parse_args()

    application = TMServer(options.tmdbfile, options.tmfiles, prefix="/tmserver", source_lang=options.source_lang, target_lang=options.target_lang)
    httpd = make_server(options.bind, options.port, application.rest)
    httpd.serve_forever()


if __name__ == '__main__':
    main()

