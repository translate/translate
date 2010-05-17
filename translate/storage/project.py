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
import shutil

from translate.convert import factory as convert_factory

from projstore import ProjectStore

__all__ = ['Project']


class Project(object):
    """Manages a project store as well as the processes involved in a project
        workflow."""

    # INITIALIZERS #
    def __init__(self, projstore=None):
        if projstore is None:
            projstore = ProjectStore()
        self.store = projstore


    # METHODS #
    def add_source(self, srcfile, src_fname=None):
        return self.store.append_sourcefile(srcfile, src_fname)

    def add_source_convert(self, srcfile, src_fname=None, convert_options=None, extension=None):
        """Convenience method that calls L{add_source} and L{convert_forward}
            and returns the results from both."""
        srcfile, srcfname = self.add_source(srcfile, src_fname)
        transfile, transfname = self.convert_forward(srcfname, convert_options=convert_options)
        return srcfile, srcfname, transfile, transfname

    def convert_forward(self, input_fname, template=None, output_fname=None, append_output_ext=True, convert_options=None):
        """Convert the given input file to the next type in the process:
            Source document (eg. ODT) -> Translation file (eg. XLIFF) ->
            Translated document (eg. ODT).

            @type  input_fname: basestring
            @param input_fname: The project name of the file to convert
            @type  convert_options: dict (optional)
            @param convert_options: Passed as-is to C{translate.convert.
            @returns 2-tuple: the converted file object and it's project name."""
        if convert_options is None:
            convert_options = {}

        inputfile = self.get_file(input_fname)
        input_type = self.store.get_filename_type(input_fname)

        if input_type == 'tgt':
            raise ValueError('Cannot convert a target document further: %s' % (input_fname))

        templ_fname = None
        if isinstance(template, basestring):
            template, templ_fname = self.get_file(template)

        if template and not templ_fname:
            templ_fname = template.name

        # Check if we can determine a template from the conversion map
        if template is None:
            convert_map = self.store.convert_map
            if input_fname in convert_map:
                templ_fname = convert_map[input_fname][1]
                template = self.get_file(templ_fname)
            elif input_type == 'trans':
                # inputfile is a translatable file, so it needed to be converted
                # from some input document. Let's try and use that document as a
                # template for this conversion.
                for in_name, (out_name, tmpl_name) in self.store.convert_map.items():
                    if input_fname == out_name:
                        template, templ_fname = self.get_file(in_name), in_name
                        break

        # Populate the options dict with the options we can detect
        options = dict(in_fname=input_fname)

        converted_file, converted_ext = convert_factory.convert(
            inputfile,
            template=template,
            options=options,
            convert_options=convert_options
        )

        # Determine the file name and path where the output should be moved.
        if not output_fname:
            _dir, fname = os.path.split(input_fname)
            dir = ''
            if hasattr(inputfile, 'name'):
                dir, _fn = os.path.split(inputfile.name)
            else:
                dir = os.getcwd()
            output_fname = os.path.join(dir, fname)
        if append_output_ext:
            output_fname += os.extsep + converted_ext

        os.rename(converted_file.name, output_fname)

        output_type = self.store.TYPE_INFO['next_type'][input_type]
        outputfile, output_fname = self.store.append_file(output_fname, None, ftype=output_type)
        self.store.convert_map[input_fname] = (output_fname, templ_fname)

        return outputfile, output_fname

    def export_file(self, fname, destfname):
        """Export the file with the specified filename to the given destination.
            This method will raise L{FileNotInProjectError} via the call to
            L{ProjectStore.get_file()} if C{fname} is not found in the project."""
        open(destfname, 'w').write(self.store.get_file(fname).read())

    def get_file(self, fname):
        """Proxy for C{ProjectStore.get_file()}."""
        return self.store.get_file(fname)

    def get_proj_filename(self, realfname):
        """Proxy to C{self.store.get_proj_filename()}."""
        return self.store.get_proj_filename(realfname)

    def get_real_filename(self, projfname):
        """Try and find a real file name for the given project file name."""
        projfile = self.get_file(projfname)
        rfname = getattr(projfile, 'name', getattr(projfile, 'filename', None))
        if rfname is None:
            raise ValueError('Project file has no real file: %s' % (projfname))
        return rfname

    def update_file(self, proj_fname, infile):
        """Proxy to C{self.store.update_file()}."""
        self.store.update_file(proj_fname, infile)
