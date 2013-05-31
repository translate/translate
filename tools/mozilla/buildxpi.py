#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2008 Zuza Software Foundation
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

"""Create a XPI language pack from Mozilla sources and translated l10n files.
This script has only been tested with Firefox 3.1 beta sources.

(Basically the process described at
https://developer.mozilla.org/en/Creating_a_Language_Pack)

Example usage::

    buildxpi.py -L /path/to/l10n -s /path/to/mozilla-central -o /path/to/xpi_output af

- "/path/to/l10n" is the path to a the parent directory of the "af" directory
  containing the Afrikaans translated files.
- "/path/to/mozilla-central" is the path to the Firefox sources checked out
  from Mercurial. Note that --mozproduct is not specified, because the default
  is "browser". For Thunderbird (>=3.0) it should be "/path/to/comm-central"
  and "--mozproduct mail" should be specified, although this is not yet
  working.
- "/path/to/xpi_output" is the path to the output directory.
- "af" is the language (Afrikaans in this case) to build a language pack for.

NOTE: The .mozconfig in Firefox source directory gets backed up,
overwritten and replaced.
"""

import logging
import os
from glob       import glob
from shutil     import move, rmtree
from subprocess import Popen, PIPE, CalledProcessError
from tempfile   import mkdtemp

logger = logging.getLogger(__name__)


class RunProcessError(CalledProcessError):
    """Subclass of CalledProcessError exception with custom message strings
    """
    _default_message = "Command '%s' returned exit status %d"

    def __init__(self, message=None, **kwargs):
        """Use and strip string message='' from kwargs"""
        self._message = message or self._default_message
        super(RunProcessError, self).__init__(**kwargs)

    def __str__(self):
        """Format exception message string (avoiding TypeErrors)"""
        output = ''
        message = self._message
        if message.count('%') != 2:
            output += message + '\n'
            message = self._default_message
            
        output += message % (self.cmd, self.returncode)
        return output

def run(cmd, expected_status=0, fail_msg=None, stdout=-1, stderr=-1):
    """Run a command
    """
    # Default is to capture (and log) std{out,error} unless run as script
    if __name__ == '__main__' or logger.getEffectiveLevel() == logging.DEBUG:
        std = None
    else:
        std = PIPE

    if stdout == -1:
        stdout = std
    if stderr == -1:
        stderr = std

    cmdstring = isinstance(str, basestring) and cmd or ' '.join(cmd)
    logger.debug('>>> %s $ %s', os.getcwd(), cmdstring)
    p = Popen(cmd, stdout=stdout, stderr=stderr)
    (output, error) = p.communicate()
    cmd_status = p.wait()

    if stdout == PIPE:
        if cmd_status != expected_status:
            logger.info('%s', output)
    elif stderr == PIPE:
        logger.warning('%s', error)

    if cmd_status != expected_status:
        raise RunProcessError(returncode=cmd_status, cmd=cmdstring,
                              message=fail_msg)
    return cmd_status


def build_xpi(l10nbase, srcdir, outputdir, lang, product, delete_dest=False):
    MOZCONFIG = os.path.join(srcdir, '.mozconfig')
    # Backup existing .mozconfig if it exists
    backup_name = ''
    if os.path.exists(MOZCONFIG):
        backup_name = MOZCONFIG + '.tmp'
        os.rename(MOZCONFIG, backup_name)

    # Create a temporary directory for building
    builddir = mkdtemp('', 'buildxpi')

    # Per the original instructions, it should be possible to configure the
    # Mozilla build so that it doesn't require compiler toolchains or
    # development include/library files - however it is currently broken for
    # Aurora 22-23; # see https://bugzilla.mozilla.org/show_bug.cgi?id=862770
    # in case it has been fixed and you can put back:
    #ac_add_options --disable-compile-environment

    try:
        # Create new .mozconfig
        content = """
ac_add_options --disable-ogg
ac_add_options --disable-wave
ac_add_options --disable-webm
ac_add_options --disable-libjpeg-turbo
mk_add_options MOZ_OBJDIR=%(builddir)s
ac_add_options --with-l10n-base=%(l10nbase)s
ac_add_options --enable-application=%(product)s
""" % \
            {
                'builddir': builddir,
                'l10nbase': l10nbase,
                'product': product
            }

        mozconf = open(MOZCONFIG, 'w').write(content)

	# Try to make sure that "environment shell" is defined
        # (python/mach/mach/mixin/process.py)
        if not any (var in os.environ
                    for var in ('SHELL', 'MOZILLABUILD', 'COMSPEC')):
            os.environ['SHELL'] = '/bin/sh'

        # Start building process.
        # See https://developer.mozilla.org/en/Creating_a_Language_Pack for
        # more details.
        olddir = os.getcwd()
        os.chdir(srcdir)
        run(['make', '-f', 'client.mk', 'configure'],
            fail_msg="Build environment error - "
                     "check logs, fix errors, and try again")

        os.chdir(builddir)
        run(['make', '-C', 'config'],
            fail_msg="Unable to successfully configure build for XPI!")
        run(['make', '-C', os.path.join(product, 'locales'),
             'langpack-%s' % (lang)],
            fail_msg="Unable to successfully build XPI!")

        xpiglob = glob(
            os.path.join(
                builddir,
                product == 'mail' and 'mozilla' or '',
                'dist',
                '*',
                'xpi',
                '*.%s.langpack.xpi' % lang
            )
        )[0]
        filename = os.path.split(xpiglob)[1]
        destfile = os.path.join(outputdir, filename)
        if delete_dest:
            if os.path.isfile(destfile):
                os.unlink(destfile)
        move(xpiglob, outputdir)

    finally:
        os.chdir(olddir)
        # Clean-up
        rmtree(builddir)
        if backup_name:
            os.remove(MOZCONFIG)
            os.rename(backup_name, MOZCONFIG)

    return destfile


def create_option_parser():
    from optparse import OptionParser
    usage = 'Usage: buildxpi.py [<options>] <lang>'
    p = OptionParser(usage=usage)

    p.add_option(
        '-L', '--l10n-base',
        dest='l10nbase',
        default='l10n',
        help='The directory containing the <lang> subdirectory.'
    )
    p.add_option(
        '-o', '--output-dir',
        dest='outputdir',
        default='.',
        help='The directory to copy the built XPI to (default: current directory).'
    )
    p.add_option(
        '-p', '--mozproduct',
        dest='mozproduct',
        default='browser',
        help='The Mozilla product name (default: "browser").'
    )
    p.add_option(
        '-s', '--src',
        dest='srcdir',
        default='mozilla',
        help='The directory containing the Mozilla l10n sources.'
    )
    p.add_option(
        '-d', '--delete-dest',
        dest='delete_dest',
        action='store_true',
        default=False,
        help='Delete output XPI if it already exists.'
    )

    p.add_option(
        '-v', '--verbose',
        dest='verbose',
        action='store_true',
        default=False,
        help='Be more noisy'
    )

    return p

if __name__ == '__main__':
    options, args = create_option_parser().parse_args()

    if len(args) < 1:
        from argparse import ArgumentError
        raise ArgumentError(None, 'You need to specify at least a language!')

    if options.verbose:
        logging.basicConfig(level=logging.DEBUG)

    build_xpi(
        l10nbase=os.path.abspath(options.l10nbase),
        srcdir=os.path.abspath(options.srcdir),
        outputdir=os.path.abspath(options.outputdir),
        lang=args[0],
        product=options.mozproduct,
        delete_dest=options.delete_dest
    )
