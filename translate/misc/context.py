#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2002-2006 Zuza Software Foundation
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
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#

import sys


def with_(mgr, body):
    """A function to mimic the with statement introduced in Python 2.5

    The code below was taken from http://www.python.org/dev/peps/pep-0343/
    """
    exit = mgr.__exit__  # Not calling it yet
    value = mgr.__enter__()
    exc = True
    try:
        try:
            if isinstance(value, (tuple, list)):
                return body(*value)
            else:
                return body(value)
        except:
            # The exceptional case is handled here
            exc = False
            if not exit(*sys.exc_info()):
                raise
            # The exception is swallowed if exit() returns true
    finally:
        # The normal and non-local-goto cases are handled here
        if exc:
            exit(None, None, None)
