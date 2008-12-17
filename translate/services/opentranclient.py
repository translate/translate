#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2008 Zuza Software Foundation
#
# This file is part of Translate.
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

from translate.services import restclient
import os
import xmlrpclib
import pycurl

class OpenTranClient(restclient.RESTClient):
    """CRUD operations for TM units and stores"""
    
    def __init__(self, url, target_lang, source_lang="en"):
        restclient.RESTClient.__init__(self)
        self.url = url
        self.target_lang = target_lang
        self.source_lang = source_lang
        
    def translate_unit(self, unit_source, callback=None):
        if isinstance(unit_source, unicode):
            unit_source = unit_source.encode("utf-8")

        request_body = xmlrpclib.dumps(
            (unit_source, self.source_lang, self.target_lang), "suggest2")
        request = restclient.RESTClient.Request(
                self.url, unit_source, "POST", request_body)
        request.curl.setopt(pycurl.VERBOSE, 1)
        request.curl.setopt(pycurl.URL, self.url)
        self.add(request)
        if callback:
            request.connect("REST-success", 
                            lambda widget, id, response: callback(widget, id, self.format_suggestions(response)))

    def format_suggestions(self, suggestions):
        """clean up open tran suggestion and use the same format as tmserver"""
        (suggestions,), fish = xmlrpclib.loads(suggestions)
        results = []
        for suggestion in suggestions:
            result = {}
            result['target'] = suggestion['text']
            result['source'] = suggestion['projects'][0]['orig_phrase']
            result['quality'] = "50"
            results.append(result)
        return results
