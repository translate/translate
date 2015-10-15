#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2006-2013 Zuza Software Foundation
#
# This file is part of Translate.
#
# Translate is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# Translate is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Translate; if not, see <http://www.gnu.org/licenses/>.

import os
import re
import sys
from distutils.sysconfig import get_python_lib
from os.path import basename, isfile, join

try:
    from sphinx.setup_command import BuildDoc
    cmdclass = {'build_sphinx': BuildDoc}
except ImportError:
    cmdclass = {}

from translate import __doc__, __version__


# Alias copied from six
if sys.version_info[0] == 2:
    string_types = basestring,
else:
    string_types = str,

PRETTY_NAME = 'Translate Toolkit'
translateversion = __version__.sver

packagesdir = get_python_lib()
sitepackages = packagesdir.replace(sys.prefix + os.sep, '')

infofiles = [(join(sitepackages, 'translate'),
             [filename for filename in ('COPYING', 'README.rst')])]
initfiles = [(join(sitepackages, 'translate'), [join('translate', '__init__.py')])]

subpackages = [
        "convert",
        "filters",
        "lang",
        "misc",
        join("misc", "wsgiserver"),
        "storage",
        join("storage", "placeables"),
        join("storage", "versioncontrol"),
        join("storage", "xml_extract"),
        "search",
        join("search", "indexing"),
        "services",
        "tools",
        ]
# TODO: elementtree doesn't work in sdist, fix this
packages = ["translate"]

translatescripts = [join(*('translate', ) + script) for script in [
                  ('convert', 'pot2po'),
                  ('convert', 'moz2po'), ('convert', 'po2moz'),
                  ('convert', 'oo2po'), ('convert', 'po2oo'),
                  ('convert', 'oo2xliff'), ('convert', 'xliff2oo'),
                  ('convert', 'prop2po'), ('convert', 'po2prop'),
                  ('convert', 'csv2po'), ('convert', 'po2csv'),
                  ('convert', 'txt2po'), ('convert', 'po2txt'),
                  ('convert', 'ts2po'), ('convert', 'po2ts'),
                  ('convert', 'html2po'), ('convert', 'po2html'),
                  ('convert', 'ical2po'), ('convert', 'po2ical'),
                  ('convert', 'ini2po'), ('convert', 'po2ini'),
                  ('convert', 'json2po'), ('convert', 'po2json'),
                  ('convert', 'tiki2po'), ('convert', 'po2tiki'),
                  ('convert', 'php2po'), ('convert', 'po2php'),
                  ('convert', 'rc2po'), ('convert', 'po2rc'),
                  ('convert', 'resx2po'), ('convert', 'po2resx'),
                  ('convert', 'xliff2po'), ('convert', 'po2xliff'),
                  ('convert', 'sub2po'), ('convert', 'po2sub'),
                  ('convert', 'symb2po'), ('convert', 'po2symb'),
                  ('convert', 'po2tmx'),
                  ('convert', 'po2wordfast'),
                  ('convert', 'csv2tbx'),
                  ('convert', 'odf2xliff'), ('convert', 'xliff2odf'),
                  ('convert', 'web2py2po'), ('convert', 'po2web2py'),
                  ('filters', 'pofilter'),
                  ('tools', 'pocompile'),
                  ('tools', 'poconflicts'),
                  ('tools', 'pocount'),
                  ('tools', 'podebug'),
                  ('tools', 'pogrep'),
                  ('tools', 'pomerge'),
                  ('tools', 'porestructure'),
                  ('tools', 'posegment'),
                  ('tools', 'poswap'),
                  ('tools', 'poclean'),
                  ('tools', 'poterminology'),
                  ('tools', 'pretranslate'),
                  ('services', 'tmserver'),
                  ('tools', 'build_tmdb')]
]

translatebashscripts = [join(*('tools', ) + script) for script in [
                  ('junitmsgfmt', ),
                  ('mozilla', 'build_firefox.sh'),
                  ('mozilla', 'buildxpi.py'),
                  ('mozilla', 'get_moz_enUS.py'),
                  ('pocommentclean', ),
                  ('pocompendium', ),
                  ('pomigrate2', ),
                  ('popuretext', ),
                  ('poreencode', ),
                  ('posplit', ),
    ]
]

classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: GNU General Public License (GPL)",
    "Operating System :: OS Independent",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: Unix",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Software Development :: Localization",
]


def parse_requirements(file_name):
    """Parses a pip requirements file and returns a list of packages.

    Use the result of this function in the ``install_requires`` field.
    Copied from cburgmer/pdfserver.
    """
    requirements = []
    with open(file_name, 'r') as fh:
        for line in fh:
            # Ignore comments, blank lines and included requirements files
            if re.match(r'(\s*#)|(\s*$)|(-r .*$)', line):
                continue

            if re.match(r'\s*-e\s+', line):
                requirements.append(re.sub(r'\s*-e\s+.*#egg=(.*)$', r'\1', line))
            elif not re.match(r'\s*-f\s+', line):
                requirements.append(line.rstrip('\n'))

    return requirements


def getdatafiles():
    datafiles = initfiles + infofiles

    def listfiles(srcdir):
        return (
            join(sitepackages, 'translate', srcdir),
            [join(srcdir, f)
             for f in os.listdir(srcdir) if isfile(join(srcdir, f))])

    docfiles = []
    for subdir in ['docs', 'share']:
        docwalk = os.walk(subdir)
        for docs in docwalk:
            files = listfiles(docs[0])
            if files[1]:
                docfiles.append(files)
        datafiles += docfiles
    return datafiles


def build_console_scripts(scripts):
    """This build console scripts list. More detail please see:
    http://python-packaging.readthedocs.org/en/latest/command-line-scripts.html#the-console-scripts-entry-point
    """
    return [
        '{scriptname}={modulename}:main'.format(
            scriptname=basename(scriptfile),
            modulename=scriptfile.replace(os.sep, '.'))
        for scriptfile in scripts
    ]


def buildmanifest_in(f, scripts):
    """This writes the required files to a MANIFEST.in file"""
    f.write("# MANIFEST.in: the below autogenerated by setup.py from translate %s\n" % translateversion)
    f.write("# things needed by translate setup.py to rebuild\n")
    f.write("# informational fs\n")
    for infof in ("README.rst", "COPYING", "*.txt"):
        f.write("global-include %s\n" % infof)
    f.write("# C programs\n")
    f.write("global-include *.c\n")
    f.write("# scripts which don't get included by default in sdist\n")
    for scriptname in scripts:
        f.write("include %s\n" % scriptname)
    f.write("# include our documentation\n")
    f.write("graft docs\n")
    f.write("prune docs/doctrees\n")
    f.write("graft tests\n")
    f.write("global-exclude .coverage*\n")
    f.write("global-exclude *~\n")
    f.write("global-exclude *.pyc\n")
    f.write("graft share\n")
    f.write("# MANIFEST.in: end of autogenerated block")


def standardsetup(name, version, custompackages=[], customdatafiles=[]):
    # TODO: make these end with .py ending on Windows...
    try:
        with open("MANIFEST.in", "w") as manifest_in:
            buildmanifest_in(manifest_in, translatescripts + translatebashscripts)
    except IOError as e:
        sys.stderr.write("warning: could not recreate MANIFEST.in, continuing anyway. (%s)\n" % e)

    for subpackage in subpackages:
        initfiles.append((join(sitepackages, "translate", subpackage),
                          [join("translate", subpackage, "__init__.py")]))
        packages.append("translate.%s" % subpackage)

    datafiles = getdatafiles()
    console_scripts = build_console_scripts(translatescripts)
    dosetup(name, version, packages + custompackages,
            datafiles + customdatafiles, console_scripts, translatebashscripts)


def dosetup(name, version, packages, datafiles, console_scripts, scripts, ext_modules=[]):
    from setuptools import setup
    description, long_description = __doc__.split("\n", 1)

    setup(name=name,
          version=version,
          license="GNU General Public License (GPL)",
          description=description,
          long_description=long_description,
          author="Translate",
          author_email="translate-devel@lists.sourceforge.net",
          url="http://toolkit.translatehouse.org/",
          download_url="http://sourceforge.net/projects/translate/files/Translate Toolkit/" + version,
          platforms=["any"],
          classifiers=classifiers,
          packages=packages,
          data_files=datafiles,
          entry_points = {
              'console_scripts': console_scripts,
          },
          scripts=scripts,
          ext_modules=ext_modules,
          cmdclass=cmdclass,
          install_requires=parse_requirements('requirements/required.txt'),
    )


if __name__ == "__main__":
    standardsetup("translate-toolkit", translateversion)
