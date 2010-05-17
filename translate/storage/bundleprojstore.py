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

from translate.misc.zipfileext import ZipFileExt
from translate.storage.projstore import *

__all__ = ['BundleProjectStore', 'InvalidBundleError']


class InvalidBundleError(Exception):
    pass


class BundleProjectStore(ProjectStore):
    """Represents a translate project bundle (zip archive)."""

    # INITIALIZERS #
    def __init__(self, fname):
        super(BundleProjectStore, self).__init__()
        self._tempfiles = {}
        if os.path.isfile(fname):
            self.load(fname)
        else:
            self.zip = ZipFileExt(fname, 'a')
            self.save()

    def __del__(self):
        self.cleanup()
        super(BundleProjectStore, self).__del__()


    # CLASS METHODS #
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


    # METHODS #
    def append_file(self, afile, fname, ftype='trans'):
        afile, fname = super(BundleProjectStore, self).append_file(afile, fname, ftype)

        if hasattr(afile, 'seek'):
            afile.seek(0)
        self.zip.writestr(fname, afile.read())
        self._files[fname] = None # Clear the cached file object to force the
                                  # file to be read from the zip file.
        return self.get_file(fname), fname

    def remove_file(self, fname, ftype=None):
        super(BundleProjectStore, self).remove_file(fname, ftype)
        if fname in self.zip.namelist():
            self.zip.delete(fname)

    def cleanup(self):
        """Clean up our mess - update project files from temporary files."""
        deleted = []
        for tempfname in self.tempfiles:
            tmp = open(tempfname)
            self.update_file(self.tempfiles[tempfname], tmp)
            if not tmp.closed:
                tmp.close()
            os.unlink(tempfname)
            deleted.append(tempfname)
        for delfname in deleted:
            del self.tempfiles[delfname]

    def get_file(self, fname):
        retfile = None
        if fname in self._files or fname in self.zip.namelist():
            # Check if the file has not already been extracted to a temp file
            tempfname = [tfn for tfn in self._tempfiles if self._tempfiles[tfn] == fname]
            if tempfname and os.path.isfile(tempfname[0]):
                tempfname = tempfname[0]
            else:
                tempfname = ''
            if not tempfname:
                # Extract the file to a temporary file
                zfile = self.zip.open(fname)
                tempfname = os.path.split(fname)[-1]
                tempfd, tempfname = tempfile.mkstemp(suffix=tempfname)
                os.close(tempfd)
                open(tempfname, 'w').write(zfile.read())
            retfile = open(tempfname)
            self._tempfiles[tempfname] = fname

        if not retfile:
            raise FileNotInProjectError(fname)
        return retfile

    def get_proj_filename(self, realfname):
        """Try and find a project file name for the given real file name."""
        try:
            fname = super(BundleProjectStore, self).get_proj_filename(realfname)
        except ValueError, ve:
            fname = None
        if fname:
            return fname
        if realfname in self._tempfiles:
            return self._tempfiles[realfname]
        raise ValueError('Real file not in project store: %s' % (realfname))

    def load(self, zipname):
        self.zip = ZipFileExt(zipname, mode='a')
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
        from StringIO import StringIO

        io = StringIO()
        newzip = ZipFileExt(io, mode='a')
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
        self.zip = ZipFileExt(zfname, mode='a')

    def _load_settings(self):
        if 'project.xtp' not in self.zip.namelist():
            raise InvalidBundleError('Not a translate project bundle')
        super(BundleProjectStore, self)._load_settings(self.zip.open('project.xtp').read())

    def _create_temp_zipfile(self):
        """Create a new zip file with a temporary file name (with mode 'w')."""
        newzipfd, newzipfname = tempfile.mkstemp(prefix='translate_bundle', suffix='.zip')
        os.close(newzipfd)
        return ZipFile(newzipfname, 'w')

    def _replace_project_zip(self, zfile):
        """Replace the currently used zip file (C{self.zip}) with the given zip
            file. Basically, C{os.rename(zfile.filename, self.zip.filename)}."""
        if not zfile.fp.closed:
            zfile.close()
        if not self.zip.fp.closed:
            self.zip.close()
        os.rename(zfile.filename, self.zip.filename)
        self.zip = ZipFile(self.zip.filename, mode='a')

    def _update_from_tempfiles(self):
        """Update project files from temporary files."""
        for tempfname in self._tempfiles:
            tmp = open(tempfname)
            self.update_file(self._tempfiles[tempfname], tmp)
            if not tmp.closed:
                tmp.close()

    def _zip_delete(self, fnames):
        """Delete the files with the given names from the zip file (C{self.zip})."""
        # Sanity checking
        if not isinstance(fnames, (list, tuple)):
            raise ValueError("fnames must be list or tuple: %s" % (fnames))
        if not self.zip:
            raise ValueError("No zip file to work on")
        zippedfiles = self.zip.namelist()
        for fn in fnames:
            if fn not in zippedfiles:
                raise KeyError("File not in zip archive: %s" % (fn))

        newzip = self._create_temp_zipfile()
        newzip.writestr('project.xtp', self._generate_settings())

        for fname in zippedfiles:
            # Copy all files from self.zip that are not project.xtp (already
            # in the new zip file) or in fnames (they are to be removed, after
            # all.
            if fname in fnames or fname == 'project.xtp':
                continue
            newzip.writestr(fname, self.zip.read(fname))

        self._replace_project_zip(newzip)
