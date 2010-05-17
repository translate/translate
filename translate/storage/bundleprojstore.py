#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2010 Zuza Software Foundation
#
# This file is part of the Translate Toolkit.
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

import os
import tempfile
from zipfile import ZipFile

from translate.storage.projstore import *

__all__ = ['BundleProjectStore', 'InvalidBundleError']


class InvalidBundleError(Exception):
    pass


class BundleProjectStore(ProjectStore):
    """Represents a translate project bundle (zip archive)."""

    # INITIALIZERS #
    def __init__(self, fname):
        super(BundleProjectStore, self).__init__()
        if os.path.isfile(fname):
            self.load(fname)
        else:
            self.zip = ZipFile(fname, 'w')

    @classmethod
    def from_project(cls, proj, fname=None):
        if fname is None:
            fname = 'bundle.zip'

        bundle = BundleProjectStore(fname)
        for fn in proj.sourcefiles:
            bundle.append_sourcefile(proj.get_file(fn))
        for fn in proj.transfiles:
            bundle.append_transfile(proj.get_file(fn))
        for fn in proj.targetfiles:
            bundle.append_targetfile(proj.get_file(fn))
        bundle.settings = proj.settings.copy()
        bundle.save()
        return bundle


    # ACCESSORS #
    def append_file(self, afile, fname, ftype='trans'):
        afile, fname = super(BundleProjectStore, self).append_file(afile, fname, ftype)

        if hasattr(afile, 'seek'):
            afile.seek(0)
        self.zip.writestr(fname, afile.read())
        self._files[fname] = None # Clear the cached file object to force the
                                  # file to be read from the zip file.
        return self.get_file(fname), fname


    # METHODS #
    def get_file(self, fname):
        retfile = None
        try:
            retfile = super(BundleProjectStore, self).get_file(fname)
        except FileNotInProjectError:
            pass

        if fname in self.zip.namelist():
            # Extract the file to a temporary file
            zfile = self.zip.open(fname)
            tempfname = os.path.split(fname)[-1]
            tempfd, tempfname = tempfile.mkstemp(suffix=tempfname)
            os.close(tempfd)
            outputfile = open(tempfname, 'w').write(zfile.read())
            retfile = open(tempfname)

        if not retfile:
            raise FileNotInProjectError(fname)
        return retfile

    def load(self, zipname):
        self.zip = ZipFile(zipname, mode='a')
        self._load_settings()

        append_section = {
            'sources':    self._sourcefiles.append,
            'targets':    self._targetfiles.append,
            'transfiles': self._transfiles.append,
        }
        for section in ('sources', 'targets', 'transfiles'):
            if section in self.settings:
                for fname in self.settings[section]:
                    append_section[section](fname)
                    self._files[fname] = None

    def save(self):
        import tempfile
        from StringIO import StringIO

        io = StringIO()
        newzip = ZipFile(io, mode='w')
        newzip.writestr('project.xtp', self._generate_settings())
        for fname in self._sourcefiles + self._transfiles + self._targetfiles:
            newzip.writestr(fname, self.get_file(fname).read())
        newzip.close()
        self.zip.close()

        # Save the contents of the zip file (io) to a temp file
        newzipfd, newzipfname = tempfile.mkstemp(prefix='translate_bundle')
        io.seek(0)
        os.write(newzipfd, io.read())
        os.close(newzipfd)

        # XXX: The following overwrites the original zip file. Is this correct behaviour?
        zfname = self.zip.filename
        os.rename(newzipfname, zfname)
        self.zip = ZipFile(zfname, mode='a')

    def _load_settings(self):
        if 'project.xtp' not in self.zip.namelist():
            raise InvalidBundleError('Not a translate project bundle')
        super(BundleProjectStore, self)._load_settings(self.zip.open('project.xtp').read())
