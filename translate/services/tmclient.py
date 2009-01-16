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
import simplejson as json

class TMClient(restclient.RESTClient):
    """CRUD operations for TM units and stores"""

    def __init__(self, base_url):
        restclient.RESTClient.__init__(self)
        self.base_url = base_url

    def translate_unit(self, unit_source, source_lang, target_lang, callback=None):
        request = restclient.RESTClient.Request(
                self.base_url + "/%s/%s/unit" % (source_lang, target_lang),
                unit_source, "GET")
        self.add(request)
        if callback:
            request.connect("REST-success",
                            lambda widget, id, response: callback(widget, id, json.loads(response)))

    def add_unit(self, unit, source_lang, target_lang, callback=None):
        request = restclient.RESTClient.Request(
                self.base_url + "/%s/%s/unit" % (source_lang, target_lang),
                unit['source'], "PUT", json.dumps(unit))
        self.add(request)
        if callback:
            request.connect("REST-success",
                            lambda widget, id, response: callback(widget, id, json.loads(response)))

    def update_unit(self, unit, source_lang, target_lang, callback=None):
        request = restclient.RESTClient.Request(
                self.base_url + "/%s/%s/unit" % (source_lang, target_lang),
                unit['source'], "POST", json.dumps(unit))
        self.add(request)
        if callback:
            request.connect("REST-success",
                            lambda widget, id, response: callback(widget, id, json.loads(response)))

    def forget_unit(self, unit_source, source_lang, target_lang, callback=None):
        request = restclient.RESTClient.Request(
                self.base_url + "/%s/%s/unit" % (source_lang, target_lang),
                unit_source, "DELETE")
        self.add(request)
        if callback:
            request.connect("REST-success",
                            lambda widget, id, response: callback(widget, id, json.loads(response)))

    def get_store_stats(self, store, callback=None):
        request = restclient.RESTClient.Request(
                self.base_url + "/store",
                store.filename, "GET")
        self.add(request)
        if callback:
            request.connect("REST-success",
                            lambda widget, id, response: callback(widget, id, json.loads(response)))

    def upload_store(self, store, callback=None):
        data = str(store)
        request = restclient.RESTClient.Request(
                self.base_url + "/store",
                store.filename, "PUT", data)
        self.add(request)
        if callback:
            request.connect("REST-success",
                            lambda widget, id, response: callback(widget, id, json.loads(response)))

    def add_store(self, store_path, callback=None):
        tmp, store_filename = os.path.split(store_path)
        request = restclient.RESTClient.Request(
                self.base_url + "/store",
                store_filename, "POST", store_path)
        self.add(request)
        if callback:
            request.connect("REST-success",
                            lambda widget, id, response: callback(widget, id, json.loads(response)))

    def forget_store(self, store, callback=None):
        request = restclient.RESTClient.Request(
                self.base_url + "/store",
                store.filename, "DELETE")
        self.add(request)
        if callback:
            request.connect("REST-success",
                            lambda widget, id, response: callback(widget, id, json.loads(response)))
