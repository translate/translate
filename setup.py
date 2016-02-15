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
from os.path import isfile, join

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

# This build console scripts list. More detail please see:
# http://python-packaging.readthedocs.org/en/latest/command-line-scripts.html#the-console-scripts-entry-point
translatescripts = [
    '{name}={entry}'.format(name=item[0], entry=item[1]) for item in [
        ('csv2po', 'translate.convert.csv2po:main'),
        ('csv2tbx', 'translate.convert.csv2tbx:main'),
        ('html2po', 'translate.convert.html2po:main'),
        ('ical2po', 'translate.convert.ical2po:main'),
        ('idml2po', 'translate.convert.idml2po:main'),
        ('ini2po', 'translate.convert.ini2po:main'),
        ('json2po', 'translate.convert.json2po:main'),
        ('moz2po', 'translate.convert.moz2po:main'),
        ('mozlang2po', 'translate.convert.mozlang2po:main'),
        ('odf2xliff', 'translate.convert.odf2xliff:main'),
        ('oo2po', 'translate.convert.oo2po:main'),
        ('oo2xliff', 'translate.convert.oo2xliff:main'),
        ('php2po', 'translate.convert.php2po:main'),
        ('po2csv', 'translate.convert.po2csv:main'),
        ('po2html', 'translate.convert.po2html:main'),
        ('po2ical', 'translate.convert.po2ical:main'),
        ('po2idml', 'translate.convert.po2idml:main'),
        ('po2ini', 'translate.convert.po2ini:main'),
        ('po2json', 'translate.convert.po2json:main'),
        ('po2moz', 'translate.convert.po2moz:main'),
        ('po2mozlang', 'translate.convert.po2mozlang:main'),
        ('po2oo', 'translate.convert.po2oo:main'),
        ('po2php', 'translate.convert.po2php:main'),
        ('po2prop', 'translate.convert.po2prop:main'),
        ('po2rc', 'translate.convert.po2rc:main'),
        ('po2resx', 'translate.convert.po2resx:main'),
        ('po2sub', 'translate.convert.po2sub:main'),
        ('po2symb', 'translate.convert.po2symb:main'),
        ('po2tiki', 'translate.convert.po2tiki:main'),
        ('po2tmx', 'translate.convert.po2tmx:main'),
        ('po2ts', 'translate.convert.po2ts:main'),
        ('po2txt', 'translate.convert.po2txt:main'),
        ('po2web2py', 'translate.convert.po2web2py:main'),
        ('po2wordfast', 'translate.convert.po2wordfast:main'),
        ('po2xliff', 'translate.convert.po2xliff:main'),
        ('pot2po', 'translate.convert.pot2po:main'),
        ('prop2po', 'translate.convert.prop2po:main'),
        ('rc2po', 'translate.convert.rc2po:main'),
        ('resx2po', 'translate.convert.resx2po:main'),
        ('sub2po', 'translate.convert.sub2po:main'),
        ('symb2po', 'translate.convert.symb2po:main'),
        ('tiki2po', 'translate.convert.tiki2po:main'),
        ('ts2po', 'translate.convert.ts2po:main'),
        ('txt2po', 'translate.convert.txt2po:main'),
        ('web2py2po', 'translate.convert.web2py2po:main'),
        ('xliff2odf', 'translate.convert.xliff2odf:main'),
        ('xliff2oo', 'translate.convert.xliff2oo:main'),
        ('xliff2po', 'translate.convert.xliff2po:main'),
        ('pofilter', 'translate.filters.pofilter:main'),
        ('tmserver', 'translate.services.tmserver:main'),
        ('build_tmdb', 'translate.tools.build_tmdb:main'),
        ('phppo2pypo', 'translate.tools.phppo2pypo:main'),
        ('poclean', 'translate.tools.poclean:main'),
        ('pocompile', 'translate.tools.pocompile:main'),
        ('poconflicts', 'translate.tools.poconflicts:main'),
        ('pocount', 'translate.tools.pocount:main'),
        ('podebug', 'translate.tools.podebug:main'),
        ('pogrep', 'translate.tools.pogrep:main'),
        ('pomerge', 'translate.tools.pomerge:main'),
        ('porestructure', 'translate.tools.porestructure:main'),
        ('posegment', 'translate.tools.posegment:main'),
        ('poswap', 'translate.tools.poswap:main'),
        ('poterminology', 'translate.tools.poterminology:main'),
        ('pretranslate', 'translate.tools.pretranslate:main'),
        ('pydiff', 'translate.tools.pydiff:main'),
        ('pypo2phppo', 'translate.tools.pypo2phppo:main'),
]]

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
            buildmanifest_in(manifest_in, translatebashscripts)
    except IOError as e:
        sys.stderr.write("warning: could not recreate MANIFEST.in, continuing anyway. (%s)\n" % e)

    for subpackage in subpackages:
        initfiles.append((join(sitepackages, "translate", subpackage),
                          [join("translate", subpackage, "__init__.py")]))
        packages.append("translate.%s" % subpackage)

    datafiles = getdatafiles()
    dosetup(name, version, packages + custompackages,
            datafiles + customdatafiles, translatescripts, translatebashscripts)


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
