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

import sys
import urllib
import re
from optparse import OptionParser
import simplejson as json
from wsgiref.simple_server import make_server
from selector import Selector, pliant, opliant
from translate.search import match
from translate.storage import factory

class TMServer:
    """a RESTful JSON TM server"""
    tmmatcher = None
    rest = None

    def __init__(self, tmfiles, max_candidates=3, min_similarity=75, max_length=1000, prefix=""):
        
        #initialize matcher
        if isinstance(tmfiles, list):
            tmstore = [factory.getobject(tmfile) for tmfile in tmfiles]
        else:
            tmstore = factory.getobject(tmfiles)        
        self.tmmatcher = match.matcher(tmstore, max_candidates=max_candidates, min_similarity=min_similarity, max_length=max_length)
        
        #initialize url dispatcher
        self.rest = Selector(prefix=prefix)
        self.rest.add("/unit/{uid:any}", GET=self.get_unit)
        #self.rest.add("/unit/{uid}", POST=self.post_unit)
        #self.rest.add("/unit/{uid}", PUT=self.put_unit)
        #self.rest.add("/unit/{uid}", DELETE=self.delete_unit)

        #self.rest.add("/store/{sid}", GET=self.get_store)
        #self.rest.add("/store/{sid}", POST=self.post_store)
        #self.rest.add("/store/{sid}", PUT=self.put_store)
        #self.rest.add("/store/{sid}", DELETE=self.delete_store)


    @opliant
    def get_unit(self, environ, start_response, uid):
        start_response("200 OK", [('Content-type', 'text/plain')])
        uid = unicode(urllib.unquote_plus(uid),"utf-8")
        
        candidates = [_unit2dict(candidate) for candidate in self.tmmatcher.matches(uid)]
        response =  json.dumps((uid,candidates), indent=4)
        return [response]


def _unit2dict(unit):
    """converts a pounit to a simple dict structure for use over the web"""
    return {"source": unit.source, "target": unit.target, 
            "quality": _parse_quality(unit.othercomments), "context": unit.getcontext()}


def _parse_quality(comments):
    """extracts match quality from po comments"""
    for comment in comments:
        quality = re.search('([0-9]+)%', comment)
        if quality:
            return quality.group(1)
            


def main(argv=None):
    parser = OptionParser()
    parser.add_option("-t", "--tm", dest="tmfiles", action="append",
                      help="translaion memory file")
    parser.add_option("-b", "--bind", dest="bind",
                      help="adress to bind server to")
    parser.add_option("-p", "--port", dest="port", type="int",
                      help="port to listen on")


    (options, args) = parser.parse_args()

    application = TMServer(options.tmfiles, prefix="/tmserver")
    httpd = make_server(options.bind, options.port, application.rest)
    httpd.serve_forever()


if __name__ == '__main__':
    main()

