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

import StringIO
import urllib
import pycurl
import gobject
import logging

class RESTClient(object):
    """Nonblocking client that can handle multiple HTTP REST requests"""

    class Request(gobject.GObject):
        """Single HTTP REST request, blocking if used standalone"""
        def __init__(self, url, id, method='GET', data=None, headers=None):
            gobject.GObject.__init__(self)
            self.result = StringIO.StringIO()
            self.result_headers = StringIO.StringIO()

            # do we really need to keep these around?
            self.url = url.encode("utf-8")
            self.id = id.encode("utf-8")
            self.method = method
            self.data = data
            self.headers = headers
            self.status = None

            # the actual curl request object
            self.curl = pycurl.Curl()
            if (logging.root.level == logging.DEBUG):
                self.curl.setopt(pycurl.VERBOSE, 1)
                
            self.curl.setopt(pycurl.WRITEFUNCTION, self.result.write)
            self.curl.setopt(pycurl.HEADERFUNCTION, self.result_headers.write)
            self.curl.setopt(pycurl.URL, self.url + "/" + urllib.quote_plus(id))

            # let's set the HTTP request method
            if method == 'GET':
                self.curl.setopt(pycurl.HTTPGET, 1)
            elif method == 'POST':
                self.curl.setopt(pycurl.POST, 1)
            elif method == 'PUT':
                self.curl.setopt(pycurl.UPLOAD, 1)
            else:
                self.curl.setopt(pycurl.CUSTOMREQUEST, method)
            if data:
                self.curl.setopt(pycurl.POSTFIELDS, data)
            if headers:
                self.curl.setopt(pycurl.HTTPHEADER, headers)

            # self reference required cause CurlMulti will only return
            # Curl handles
            self.curl.request = self

        # define __hash__ and __eq__ so we can have meaningful sets
        def __hash__(self):
            return hash((self.url, self.id, self.method, self.data, self.headers))
        def __eq__(self, other):
            return (self.url, self.id, self.method, self.data, self.headers) == (other.url, other.id, other.method, other.data, other.headers)

        def perform(self):
            """run the request (blocks)"""
            self.curl.perform()

        def handle_result(self):
            """called after http request is done"""
            self.status = self.curl.getinfo(pycurl.HTTP_CODE)

            #TODO: handle 3xx, throw exception on other codes
            if self.status >= 200 and self.status < 300:
                # 2xx indicated success
                self.emit("REST-success", self.id, self.result.getvalue())
            elif self.status >= 400 and self.status < 500:
                # 4xx client error
                self.emit("REST-client-error", self.id, self.status)
            elif self.status >= 500 and self.status < 600:
                # 5xx server error
                self.emit("REST-server-error", self.id, self.status)


    def __init__(self):
        self.running = False
        self.requests = set()
        self.curl = pycurl.CurlMulti()


    def add(self,request):
        """add a request to the queue"""
        self.curl.add_handle(request.curl)
        self.requests.add(request)
        self.run()


    def run(self):
        """client should not be running when request queue is empty"""
        if self.running: return
        gobject.timeout_add(100, self.perform)
        self.running = True


    def close_request(self, handle):
        """finalize a successful request"""
        self.curl.remove_handle(handle)
        handle.request.handle_result()
        if handle.request in self.requests:
            self.requests.remove(handle.request)
        else:
            #FIXME: this shouldn't happen at all
            logging.error("attempted to remove non existing request")


    def perform(self):
        """main event loop function, non blocking execution of all queued requests"""
        ret, num_handles = self.curl.perform()
        if ret != pycurl.E_CALL_MULTI_PERFORM and num_handles == 0:
            self.running = False
        num, completed, failed = self.curl.info_read()
        [self.close_request(com) for com in completed]
        #TODO: handle failed requests
        if not self.running:
            #we are done with this batch what do we do?
            return False
        return True


#register the signal
gobject.signal_new("REST-success", RESTClient.Request,
                   gobject.SIGNAL_RUN_LAST,
                   gobject.TYPE_NONE,
                   (gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT))
gobject.signal_new("REST-client-error", RESTClient.Request,
                   gobject.SIGNAL_RUN_LAST,
                   gobject.TYPE_NONE,
                   (gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT))
gobject.signal_new("REST-server-error", RESTClient.Request,
                   gobject.SIGNAL_RUN_LAST,
                   gobject.TYPE_NONE,
                   (gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT))
