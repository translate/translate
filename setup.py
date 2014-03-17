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
import site
import sys
from distutils.sysconfig import get_python_lib
from os.path import dirname, isfile, join

try:
    from sphinx.setup_command import BuildDoc
    cmdclass = {'build_sphinx': BuildDoc}
except ImportError:
    cmdclass = {}

from translate import __doc__, __version__


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


# py2exe-specific stuff
try:
    import py2exe
except ImportError:
    py2exe = None
else:
    BuildCommand = py2exe.build_exe.py2exe
    Distribution = py2exe.Distribution

    class InnoScript(object):
        """class that builds an InnoSetup script"""
        def __init__(self, name, lib_dir, dist_dir, exe_files=[], other_files=[],
                    install_scripts=[], version="1.0"):
            self.lib_dir = lib_dir
            self.dist_dir = dist_dir
            if not self.dist_dir.endswith(os.sep):
                self.dist_dir += os.sep
            self.name = name
            self.version = version
            self.exe_files = [self.chop(p) for p in exe_files]
            self.other_files = [self.chop(p) for p in other_files]
            self.install_scripts = install_scripts

        def getcompilecommand(self):
            try:
                import _winreg
                compile_key = _winreg.OpenKey(_winreg.HKEY_CLASSES_ROOT,
                                            "innosetupscriptfile\\shell\\compile\\command")
                compilecommand = _winreg.QueryValue(compile_key, "")
                compile_key.Close()
            except:
                compilecommand = 'compil32.exe "%1"'
            return compilecommand

        def chop(self, pathname):
            """returns the path relative to self.dist_dir"""
            assert pathname.startswith(self.dist_dir)
            return pathname[len(self.dist_dir):]

        def create(self, pathname=None):
            """creates the InnoSetup script"""
            if pathname is None:
                _name = self.name + os.extsep + "iss"
                self.pathname = join(self.dist_dir, _name).replace(" ", "_")
            else:
                self.pathname = pathname

            # See http://www.jrsoftware.org/isfaq.php for more InnoSetup config options.
            ofi = self.file = open(self.pathname, "w")
            ofi.write("; WARNING: This script has been created by py2exe. Changes to this script\n")
            ofi.write("; will be overwritten the next time py2exe is run!\n")
            ofi.write("[Setup]\n")
            ofi.write("AppName=%s\n" % self.name)
            ofi.write("AppVerName=%s %s\n" % (self.name, self.version))
            ofi.write("DefaultDirName={pf}\\%s\n" % self.name)
            ofi.write("DefaultGroupName=%s\n" % self.name)
            ofi.write("OutputBaseFilename=%s-%s-setup\n" % (self.name, self.version))
            ofi.write("ChangesEnvironment=yes\n")
            ofi.write("\n")
            ofi.write("[Files]\n")
            for path in self.exe_files + self.other_files:
                ofi.write('Source: "%s"; DestDir: "{app}\\%s"; Flags: ignoreversion\n' % (path, dirname(path)))
            ofi.write("\n")
            ofi.write("[Icons]\n")
            ofi.write('Name: "{group}\\Documentation"; Filename: "{app}\\docs\\index.html";\n')
            ofi.write('Name: "{group}\\Translate Toolkit Command Prompt"; Filename: "cmd.exe"\n')
            ofi.write('Name: "{group}\\Uninstall %s"; Filename: "{uninstallexe}"\n' % self.name)
            ofi.write("\n")
            ofi.write("[Registry]\n")
            # TODO: Move the code to update the Path environment variable to a
            # Python script which will be invoked by the [Run] section (below)
            ofi.write('Root: HKCU; Subkey: "Environment"; ValueType: expandsz; '
                    'ValueName: "Path"; ValueData: "{reg:HKCU\\Environment,Path|};{app};"\n')
            ofi.write("\n")
            if self.install_scripts:
                ofi.write("[Run]\n")
                for path in self.install_scripts:
                    ofi.write('Filename: "{app}\\%s"; WorkingDir: "{app}"; Parameters: "-install"\n' % path)
                ofi.write("\n")
                ofi.write("[UninstallRun]\n")
                for path in self.install_scripts:
                    ofi.write('Filename: "{app}\\%s"; WorkingDir: "{app}"; Parameters: "-remove"\n' % path)
            ofi.write("\n")
            ofi.close()

        def compile(self):
            """compiles the script using InnoSetup"""
            shellcompilecommand = self.getcompilecommand()
            compilecommand = shellcompilecommand.replace('"%1"', self.pathname)
            result = os.system(compilecommand)
            if result:
                print("Error compiling iss file")
                print("Opening iss file, use InnoSetup GUI to compile manually")
                os.startfile(self.pathname)


    class build_exe_map(BuildCommand):
        """distutils py2exe-based class that builds the exe file(s) but allows
        mapping data files"""

        def reinitialize_command(self, command, reinit_subcommands=0):
            if command == "install_data":
                install_data = BuildCommand.reinitialize_command(self, command,
                                                            reinit_subcommands)
                install_data.data_files = self.remap_data_files(install_data.data_files)
                return install_data
            return BuildCommand.reinitialize_command(self, command, reinit_subcommands)

        def remap_data_files(self, data_files):
            """maps the given data files to different locations using external
            map_data_file function"""
            new_data_files = []
            for f in data_files:
                if type(f) in (str, unicode):
                    f = map_data_file(f)
                else:
                    datadir, files = f
                    datadir = map_data_file(datadir)
                    if datadir is None:
                        f = None
                    else:
                        f = datadir, files
                if f is not None:
                    new_data_files.append(f)
            return new_data_files


    class BuildInstaller(build_exe_map):
        """distutils class that first builds the exe file(s), then creates a
        Windows installer using InnoSetup"""
        description = "create an executable installer for MS Windows using InnoSetup and py2exe"
        user_options = getattr(BuildCommand, 'user_options', []) + \
            [('install-script=', None,
            "basename of installation script to be run after installation or before deinstallation")]

        def initialize_options(self):
            BuildCommand.initialize_options(self)
            self.install_script = None

        def run(self):
            # First, let py2exe do it's work.
            BuildCommand.run(self)
            lib_dir = self.lib_dir
            dist_dir = self.dist_dir
            # create the Installer, using the files py2exe has created.
            exe_files = self.windows_exe_files + self.console_exe_files
            install_scripts = self.install_script
            if isinstance(install_scripts, (str, unicode)):
                install_scripts = [install_scripts]
            script = InnoScript(PRETTY_NAME, lib_dir, dist_dir, exe_files,
                                self.lib_files,
                                version=self.distribution.metadata.version,
                                install_scripts=install_scripts)
            print("*** creating the inno setup script***")
            script.create()
            print("*** compiling the inno setup script***")
            script.compile()
            # Note: By default the final setup.exe will be in an Output
            # subdirectory.


    class TranslateDistribution(Distribution):
        """a modified distribution class for translate"""
        def __init__(self, attrs):
            baseattrs = {}
            py2exeoptions = {}
            py2exeoptions["packages"] = ["translate", "encodings"]
            py2exeoptions["compressed"] = True
            py2exeoptions["excludes"] = [
                "PyLucene", "Tkconstants", "Tkinter", "tcl",
                "enchant",  # Need to do more to support spell checking on Windows
                # strange things unnecessarily included with some versions of pyenchant:
                "win32ui", "_win32sysloader", "win32pipe", "py2exe", "win32com",
                "pywin", "isapi", "_tkinter", "win32api",
            ]
            version = attrs.get("version", translateversion)
            py2exeoptions["dist_dir"] = "translate-toolkit-%s" % version
            py2exeoptions["includes"] = ["lxml", "lxml._elementpath"]
            options = {"py2exe": py2exeoptions}
            baseattrs['options'] = options
            if py2exe:
                baseattrs['console'] = translatescripts
                baseattrs['zipfile'] = "translate.zip"
                baseattrs['cmdclass'] = cmdclass.update({
                    "py2exe": build_exe_map,
                    "innosetup": BuildInstaller,
                })
                options["innosetup"] = py2exeoptions.copy()
                options["innosetup"]["install_script"] = []
            baseattrs.update(attrs)
            Distribution.__init__(self, baseattrs)


    def map_data_file(data_file):
        """remaps a data_file (could be a directory) to a different location
        This version gets rid of Lib\\site-packages, etc"""
        data_parts = data_file.split(os.sep)
        if data_parts[:2] == ["Lib", "site-packages"]:
            data_parts = data_parts[2:]
            if data_parts:
                data_file = join(*data_parts)
            else:
                data_file = ""
        if data_parts[:1] == ["translate"]:
            data_parts = data_parts[1:]
            if data_parts:
                data_file = join(*data_parts)
            else:
                data_file = ""
        return data_file


def parse_requirements(file_name):
    """Parses a pip requirements file and returns a list of packages.

    Use the result of this function in the ``install_requires`` field.
    Copied from cburgmer/pdfserver.
    """
    requirements = []
    for line in open(file_name, 'r').read().split('\n'):
        # Ignore comments, blank lines and included requirements files
        if re.match(r'(\s*#)|(\s*$)|(-r .*$)', line):
            continue

        if re.match(r'\s*-e\s+', line):
            requirements.append(re.sub(r'\s*-e\s+.*#egg=(.*)$', r'\1', line))
        elif re.match(r'\s*-f\s+', line):
            pass
        else:
            requirements.append(line)

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
            docfiles.append(listfiles(docs[0]))
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
    f.write("graft share\n")
    f.write("# MANIFEST.in: end of autogenerated block")


def standardsetup(name, version, custompackages=[], customdatafiles=[]):
    # TODO: make these end with .py ending on Windows...
    try:
        manifest_in = open("MANIFEST.in", "w")
        buildmanifest_in(manifest_in, translatescripts + translatebashscripts)
        manifest_in.close()
    except IOError as e:
        sys.stderr.write("warning: could not recreate MANIFEST.in, continuing anyway. (%s)\n" % e)

    for subpackage in subpackages:
        initfiles.append((join(sitepackages, "translate", subpackage),
                          [join("translate", subpackage, "__init__.py")]))
        packages.append("translate.%s" % subpackage)

    datafiles = getdatafiles()
    dosetup(name, version, packages + custompackages, datafiles + customdatafiles,
            translatescripts + translatebashscripts)


def dosetup(name, version, packages, datafiles, scripts, ext_modules=[]):
    from setuptools import setup
    description, long_description = __doc__.split("\n", 1)
    kwargs = {}
    if py2exe:
        kwargs["distclass"] = TranslateDistribution

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
          scripts=scripts,
          ext_modules=ext_modules,
          cmdclass=cmdclass,
          install_requires=parse_requirements('requirements/required.txt'),
          **kwargs
    )

if __name__ == "__main__":
    standardsetup("translate-toolkit", translateversion)
