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
from lxml import etree
from StringIO import StringIO

__all__ = ['FileExistsInProjectError', 'FileNotInProjectError', 'Project']


class FileExistsInProjectError(Exception):
    pass

class FileNotInProjectError(Exception):
    pass


class Project(object):
    """Interface providing basic project functionality."""

    # INITIALIZERS #
    def __init__(self):
        self._files        = {}
        self._sourcefiles  = []
        self._targetfiles  = []
        self._transfiles   = []
        self.settings      = {}

        # The following dict groups together sets of mappings from a file
        # "type" string ("src", "tgt" or "trans") to various other values
        # or objects.
        self.TYPE_INFO = {
            # type => prefix for new files
            'f_prefix': {
                'src':   'sources/',
                'tgt':   'targets/',
                'trans': 'trans/'
            },
            # type => list containing filenames for that type
            'lists': {
                'src':   self._sourcefiles,
                'tgt':   self._targetfiles,
                'trans': self._transfiles,
            },
            # type => next type in process: src => trans => tgt
            'next_type': {
                'src':   'trans',
                'trans': 'tgt',
                'tgt':   None,
            },
            # type => name of the sub-section in the settings file/dict
            'settings': {
                'src':   'sources',
                'tgt':   'targets',
                'trans': 'transfiles',
            }
        }


    # ACCESSORS #
    def _get_sourcefiles(self):
        """Read-only access to C{self._sourcefiles}."""
        return tuple(self._sourcefiles)
    sourcefiles = property(_get_sourcefiles)

    def _get_targetfiles(self):
        """Read-only access to C{self._targetfiles}."""
        return tuple(self._targetfiles)
    targetfiles = property(_get_targetfiles)

    def _get_transfiles(self):
        """Read-only access to C{self._transfiles}."""
        return tuple(self._transfiles)
    transfiles = property(_get_transfiles)

    def append_file(self, afile, fname, ftype='trans'):
        if not ftype in self.TYPE_INFO['f_prefix']:
            raise ValueError('Invalid file type: %s' % (ftype))

        if isinstance(afile, basestring) and os.path.isfile(afile) and not fname:
            # Try and use afile as the file name
            fname, afile = afile, open(afile)

        # Check if we can get an real file name
        realfname = fname
        if realfname is None or not os.path.isfile(realfname):
            realfname = getattr(afile, 'name', None)
        if realfname is None or not os.path.isfile(realfname):
            realfname = getattr(afile, 'filename', None)
        if realfname is None or not os.path.isfile(realfname):
            realfname = None

        # Try to get the file name from the file object, if it was not given:
        if not fname:
            fname = getattr(afile, 'name', None)
        if not fname:
            fname = getattr(afile, 'filename', None)

        fname = self._fix_type_filename(ftype, fname)

        if not fname:
            raise ValueError('Could not deduce file name and none given')
        if fname in self._files:
            raise FileExistsInProjectError(fname)

        if os.path.isfile(realfname):
            self._files[fname] = realfname
        else:
            self._files[fname] = afile
        self.TYPE_INFO['lists'][ftype].append(fname)

        return afile, fname

    def append_sourcefile(self, afile, fname=None):
        return self.append_file(afile, fname, ftype='src')

    def append_targetfile(self, afile, fname=None):
        return self.append_file(afile, fname, ftype='tgt')

    def append_transfile(self, afile, fname=None):
        return self.append_file(afile, fname, ftype='trans')

    def remove_sourcefile(self, fname):
        self._remove_file(fname, ftype='src')

    def remove_targetfile(self, fname):
        self._remove_file(fname, ftype='tgt')

    def remove_transfile(self, fname):
        self._remove_file(fname, ftype='trans')

    def _remove_file(self, fname, ftype='trans'):
        if fname not in self._files:
            raise FileNotInProjectError(fname)
        self.TYPE_INFO['lists'][ftype].remove(fname)
        if self._files[fname] and hasattr(self._files[fname], 'close'):
            self._files[fname].close()
        del self._files[fname]


    # SPECIAL METHODS #
    def __in__(self, lhs):
        """@returns C{True} if C{lhs} is a file name or file object in the project."""
        return  lhs in self._sourcefiles or \
                lhs in self._targetfiles or \
                lhs in self._transfiles or \
                lhs in self._files or \
                lhs in self._files.values()


    # METHODS #
    def get_file(self, fname, mode='rb'):
        """Retrieve the file with the given name from the project.

            The file is looked up in the C{self._files} dictionary. The values
            in this dictionary may be C{None}, to indicate that the file is not
            cacheable and needs to be retrieved in a special way. This special
            way must be defined in this method of sub-classes. The value may
            also be a string, which indicates that it is a real file accessible
            via C{open()}.

            @type  mode: str
            @param mode: The mode in which to re-open the file (if it is closed)
            @see BundleProject.get_file"""
        if fname not in self._files:
            raise FileNotInProjectError(fname)

        rfile = self._files[fname]
        if isinstance(rfile, basestring):
            rfile = open(rfile, 'rb')
        # Check that the file is actually open
        if getattr(rfile, 'closed', False):
            rfname = fname
            if not os.path.isfile(rfname):
                rfname = getattr(rfile, 'name', None)
            if not rfile or not os.path.isfile(rfname):
                rfname = getattr(rfile, 'filename', None)
            if not rfile or not os.path.isfile(rfname):
                raise IOError('Could not locate file: %s (%s)' % (rfile, fname))
            rfile = open(rfname, mode)
            self._files[fname] = rfile

        return rfile

    def get_filename_type(self, fname):
        for ftype in self.TYPE_INFO['lists']:
            if fname in self.TYPE_INFO['lists'][ftype]:
                return ftype
        raise FileNotInProjectError(fname)

    def load(self, *args, **kwargs):
        pass

    def save(self, *args, **kwargs):
        pass

    def _fix_type_filename(self, ftype, fname):
        """Strip the path from the filename and prepend the correct prefix."""
        path, fname = os.path.split(fname)
        return self.TYPE_INFO['f_prefix'][ftype] + fname

    def _generate_settings(self):
        """@returns A XML string that represents the current settings."""
        xml = etree.Element('translationproject')

        # Add file names to settings XML
        if self._sourcefiles:
            sources_el = etree.Element('sources')
            for fname in self._sourcefiles:
                src_el = etree.Element('filename')
                src_el.text = fname
                sources_el.append(src_el)
            xml.append(sources_el)
        if self._transfiles:
            transfiles_el = etree.Element('transfiles')
            for fname in self._transfiles:
                trans_el = etree.Element('filename')
                trans_el.text = fname
                transfiles_el.append(trans_el)
            xml.append(transfiles_el)
        if self._targetfiles:
            target_el = etree.Element('targets')
            for fname in self._targetfiles:
                tgt_el = etree.Element('filename')
                tgt_el.text = fname
                target_el.append(tgt_el)
            xml.append(target_el)

        # Add options to settings
        if 'options' in self.settings:
            options_el = etree.Element('options')
            for option, value in self.settings['options'].items():
                opt_el = etree.Element('option')
                opt_el.attrib['name'] = option
                opt_el.text = value
                options_el.append(opt_el)
            xml.append(options_el)

        return etree.tostring(xml, pretty_print=True)

    def _load_settings(self, settingsxml):
        settings = {}
        xml = etree.fromstring(settingsxml)

        for section in ('sources', 'targets', 'transfiles'):
            groupnode = xml.find(section)
            if groupnode is None:
                continue

            settings[section] = []
            for fnode in groupnode.getchildren():
                settings[section].append(fnode.text)

        groupnode = xml.find('options')
        if groupnode is not None:
            settings['options'] = {}
            for opt in groupnode.getchildren():
                settings['options'][opt.attrib['name']] = opt.text

        self.settings = settings
