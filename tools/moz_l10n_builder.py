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
#
# moz-l10n-builder - takes a set of PO files, migrates them to a Mozilla build
# and creates XPIs and Windows .exe files.

"""Contains a Python-port of the moz-l10n-builder bash script."""

# NOTE: Because this script is adapted from a Bash script, some things in here
#       might be a little less Pythonic. See os.system() calls for more
#       details.

import glob
import os
import popen2
import shutil
import tempfile
import time

join = os.path.join

from translate.convert import moz2po
from translate.convert import po2moz
from translate.convert import po2prop
from translate.convert import po2txt
from translate.convert import txt2po

DEFAULT_TARGET_APP = 'browser'
langpack_release = '1'
targetapp = 'browser'
mozversion = '3'
l10ndir = 'l10n'
mozilladir = "mozilla"
podir = "po"
podir_recover = podir + '-recover'
podir_updated = podir + '-updated'
potpacks = "potpacks"
popacks = 'popacks'

USAGE='Usage: %prog [options] <langs...|ALL>'

class CommandError(StandardError):
    """Exception raised if a command does not return its expected value."""

    def __init__(self, cmd, status):
        self.cmd = cmd
        self.status = status

    def __str__(self):
        return '"%s" return unexptected status %d' % (self.cmd, self.status)

##### Utility Functions #####
def delfiles(pattern, path, files):
    """Delete files with names in C{files} matching glob-pattern C{glob} in the
        directory specified by C{path}.

        This function is meant to be used with C{os.path.walk}
        """
    path = os.path.abspath(path)
    match_files = glob.glob( join(path, pattern) )
    for f in files:
        if join(path, f) in match_files:
            os.unlink(join(path, f))

def run(cmd, expected_status=0, no_out=False, no_err=False):
    if no_out and no_err:
        cmd = cmd + ' 2>&1 > ' + os.devnull
    elif no_out:
        cmd = cmd + ' > ' + os.devnull
    elif no_err:
        cmd = cmd + ' 2> ' + os.devnull
    print '>>> %s $ %s' % (os.getcwd(), cmd)

    cmd_status = os.system(cmd)
    if cmd_status != expected_status:
        print '!!! "%s" returned unexpected status %d' % (cmd, cmd_status)
        #raise CommandError(cmd, cmd_status)

def get_langs(lang_args):
    """Returns the languages to handle based on the languages specified on the
        command-line.

        If "ALL" was specified, the languages are read from the Mozilla
        product's C{shipped-locales} file. If "ZA" was specified, all South
        African languages are selected.
        """

    langs = []

    if isinstance(lang_args, str):
        if lang_args == 'ALL':
            lang_args = ['ALL']
        elif lang_args == 'ZA':
            lang_args = ['ZA']
        else:
            lang_args = []

    if not lang_args:
        print USAGE
        exit(1)

    if lang_args[0] == 'ALL':
        # Get all available languages from the locales file
        locales_filename = join(mozilladir, targetapp, 'locales', 'shipped-locales')
        for line in open(locales_filename).readlines():
            langs.append(line.split()[0])

    elif lang_args[0] == 'ZA':
        # South African languages
        langs = ["af", "en_ZA", "nr", "nso", "ss", "st", "tn", "ts", "ve", "xh", "zu"]
    else:
        langs = lang_args

    return langs
#############################

def checkout(cvstag, langs):
    """Check-out needed files from Mozilla's CVS."""

    olddir = os.getcwd()
    if cvstag != '-A':
        cvstag = "-r %s" % (cvstag)

    if not os.path.exists(mozilladir):
        run(
            'cvs -d:pserver:anonymous@cvs-mirror.mozilla.org:/cvsroot co %(tag)s %(mozdir)s/client.mk' % \
            {'tag': cvstag, 'mozdir': mozilladir},
            no_out=True, no_err=True
        )
        run(
            'cvs -d:pserver:anonymous@cvs-mirror.mozilla.org:/cvsroot co %(mozdir)s/tools/l10n' % \
            {'mozdir': mozilladir},
            no_out=True, no_err=True
        )

    os.chdir(mozilladir)
    run('cvs up %(tag)s client.mk' % {'tag': cvstag}, no_out=True, no_err=True)
    run('make -f client.mk l10n-checkout MOZ_CO_PROJECT=%s' % (targetapp), no_out=True, no_err=True)
    os.chdir(olddir)

    if not os.path.exists(l10ndir):
        run('cvs -d:pserver:anonymous@cvs-mirror.mozilla.org:/l10n co -d %s -l l10n' % (l10ndir))

    os.chdir(l10ndir)
    for lang in langs:
        if os.path.isdir(lang):
            run('cvs up %s' % (lang))
        else:
            run('cvs -d:pserver:anonymous@cvs-mirror.mozilla.org:/l10n co -d %s l10n/%s' % (lang, lang))
    os.chdir(olddir)

    # Make latest POT file
    for rmdir in ('en-US', 'pot'):
        try:
            shutil.rmtree( join(l10ndir, rmdir) )
        except OSError, oe:
            # "No such file or directory" errors are fine. The rest we raise again.
            if oe.errno != 2:
                raise oe

    os.chdir(mozilladir)
    run('cvs up tools/l10n')
    run('python tools/l10n/l10n.py --dest="%s" --app=%s en-US' % (join(os.pardir, l10ndir), targetapp))
    os.chdir(olddir)

    os.chdir(l10ndir)
    moz2po.main(["-P", "--duplicates=msgctxt", "en-US", "pot"])

    # Delete the help-related POT-files, seeing as Firefox help is now on-line.
    try:
        shutil.rmtree(join('pot', 'browser', 'chrome', 'help'))
    except OSError, oe:
        # "No such file or directory" errors are fine. The rest we raise again.
        if oe.errno != 2:
            raise oe

    if mozversion < '3':
        for f in [  'en-US/browser/README.txt pot/browser/README.txt.pot',
                    'en-US/browser/os2/README.txt pot/browser/os2/README.txt.pot',
                    'en-US/mail/README.txt pot/mail/README.txt.pot',
                    'en-US/mail/os2/README.txt pot/mail/os2/README.txt.pot' ]:
            txt2po.main(['-P', f])
    os.chdir(olddir)

def recover_langs(langs):
    for lang in langs:
        if not os.path.isdir(join(podir_recover, lang)):
            os.makedirs(join(podir_recover, lang))

        moz2po.main(
            [
                '--errorlevel=traceback', '--duplicates=msgctxt',
                '--exclude=.#*',
                '-t', join(mozilladir, l10ndir, 'en-US'),
                join(l10ndir, lang),
                join(podir_recover, lang)
            ]
        )

def pack_pot():
    global timestamp
    timestamp = time.strftime('%Y%m%d')

    try:
        os.makedirs(potpacks)
    except OSError:
        pass

    run('tar cjf %(potpacks)s/%(targetapp)s-%(mozversion)s-%(timestamp)s.tar.bz2 %(l10ndir)s/en-US %(l10ndir)s/pot' % globals())
    run('zip -qr9 %(potpacks)s/%(targetapp)s-%(mozversion)s-%(timestamp)s.zip %(l10ndir)s/en-US %(l10ndir)s/pot' % globals())

def pack_po(langs):
    global timestamp
    timestamp = time.strftime('%Y%m%d')

    try:
        os.makedirs(popacks)
    except OSError:
        pass

    global lang
    for lang in langs:
        run('tar cjf %(popacks)s/%(targetapp)s-%(mozversion)s-%(lang)s-%(timestamp)s.tar.bz2 %(l10ndir)s/%(lang)s' % globals())
        run('zip -qr9 %(popacks)s/%(targetapp)s-%(mozversion)s-%(lang)s-%(timestamp)s.zip %(l10ndir)s/%(lang)s' % globals())

def pre_po2moz_hacks(lang, buildlang, debug):
    """Hacks that should be run before running C{po2moz}."""

    # Protect the real original PO dir
    temp_po = tempfile.mkdtemp()
    shutil.copytree( join(podir, lang), join(temp_po, lang) )

    if lang in ['zu', 'xh']:
        dirname = join(temp_po, lang, 'editor', 'ui')
        shutil.rmtree(dirname)
        os.makedirs(dirname)
        shutil.move(join(temp_po, lang, 'editor', 'chrome'), dirname)

    # Fix for languages that have no Windows codepage
    if lang == 've':
        src  = join(podir, 'en_ZA', 'browser', 'installer', '*.properties')
        dest = join(temp_po, lang, 'browser', 'installer')
        shutil.copytree(src, dest)

    old = join(temp_po, lang)
    new = join(podir_updated, lang)
    templates = join(l10ndir, 'pot')
    run('pomigrate2 --use-compendium --quiet --pot2po %s %s %s' % (old, new, templates))

    os.path.walk(join(podir_updated, lang), delfiles, '*.html.po')
    os.path.walk(join(podir_updated, lang), delfiles, '*.xhtml.po')

    if debug:
        olddir = os.getcwd()
        os.chdir(join("%s" % (podir_updated), lang))
        run('podebug --errorlevel=traceback --ignore=mozilla . .')
        os.chdir(olddir)

    # Create l10n related files
    if os.path.isdir( join(l10ndir, buildlang) ):
        os.path.walk(join(l10ndir, buildlang), delfiles, '*.dtd')
        os.path.walk(join(l10ndir, buildlang), delfiles, '*.properties')

    shutil.rmtree(temp_po)

def post_po2moz_hacks(lang, buildlang):
    """Hacks that should be run after running C{po2moz}."""

    # Hack to fix creating Thunderber installer
    inst_inc_po = join(podir_updated, lang, 'mail', 'installer', 'installer.inc.po')
    if os.path.isfile(inst_inc_po):
        tempdir = tempfile.mkdtemp()
        tmp_po = join(tempdir, 'installer.%s.properties.po' % (lang))
        shutil.copy2(inst_po, tmp_po)

        inst_inc = join(l10ndir, 'en-US', 'mail', 'installer', 'installer.inc')
        tmp_properties = join(tempdir, 'installer.properties')
        shutil.copy2(inst_inc, tmp_properties)

        po2prop.main(
            [
                '--progress=none', '--errorlevel=traceback',
                '-t', tmp_properties, # -t /tmp/installer.properties
                tmp_po,               # /tmp/installer.$lang.properties.po
                tmp_po[:-3]           # /tmp/installer.$lang.properties
            ]
        )

        # mv /tmp/installer.$lang.properties $l10ndir/$buildlang/mail/installer/installer.inc
        shutil.move(
            tmp_po[:-3],
            join(l10ndir, buildlang, 'mail', 'installer', 'installer.inc')
        )

        shutil.rmtree(tempdir)

    def copyfile(filename, language):
        dir = os.path.dirname(filename)

        if os.path.isfile(join(l10ndir, 'en-US', filename)):
            try:
                os.makedirs(join(l10ndir, language, dir))
            except OSError:
                pass # Don't worry if the directory already exists
            shutil.copy2(
                join(l10ndir, 'en-US', filename),
                join(l10ndir, language, dir)
            )

    def copyfiletype(filetype, language):
        def checkfiles(filetype, dir, files):
            for f in files:
                if f.endswith(filetype):
                    copyfile(join(dir, f), language)

        os.path.walk(join(l10ndir, 'en-US'), checkfiles, filetype)

    # Copy and update non-translatable files
    for ft in ('.xhtml', '.html', '.rdf'):
        copyfiletype(ft, buildlang)

    for f in (
            join('browser', 'extra-jar.mn'),
            join('browser', 'firefox-l10n.js'),
            join('browser', 'microsummary-generators', 'list.txt'),
            join('browser', 'profile', 'chrome', 'userChrome-example.css'),
            join('browser', 'profile', 'chrome', 'userContent-example.css'),
            join('browser', 'searchplugins', 'list.txt'),
            join('extensions', 'reporter', 'chrome', 'reporterOverlay.properties'),
            join('mail', 'all-l10n.js'),
            join('toolkit', 'chrome', 'global', 'intl.css')
        ):
        copyfile(f, buildlang)


def migrate_langs(langs, recover, update_transl, debug):
    for lang in langs:
        print 'Language: %s' % (lang)

        buildlang=lang.replace('_', '-')

        if recover and not os.path.isdir(join(podir, lang)):
            # If we recovered the .po files for lang, but there is no other po
            # directory, we use the recovered .po files
            try:
                os.mkdir(podir)
            except OSError, oe:
                # "File exists" errors are fine. The rest we raise again.
                if oe.errno != 17:
                    raise oe
            shutil.copytree(join(podir_recover, lang), join(podir, lang))

        if update_transl:
            olddir = os.getcwd()
            os.chdir(podir)
            run('svn up %s' % (lang))
            os.chdir(olddir)

            os.chdir(l10ndir)
            run('cvs up %s' % (lang))
            os.chdir(olddir)

        # Migrate language from current PO to latest POT
        if os.path.isdir(join(podir, '.svn')):
            shutil.rmtree(join(podir_updated, '.svn'))
            shutil.copytree(join(podir, '.svn'), podir_updated)
        if os.path.isdir(join(podir_updated, lang)):
            shutil.rmtree(join(podir_updated, lang))
        shutil.copytree( join(podir, lang), join(podir_updated, lang) )
        os.path.walk(join(podir_updated, lang), delfiles, '*.po')

        pre_po2moz_hacks(lang, buildlang, debug)

        ###################################################
        args = [
            '--errorlevel=traceback',
            '--exclude=".svn"',
            '-t', join(l10ndir, 'en-US'),
            '-i', join(podir_updated, lang),
            '-o', join(l10ndir, buildlang)
        ]

        if debug:
            args.append('--fuzzy')

        po2moz.main(args)
        ###################################################

        post_po2moz_hacks(lang, buildlang)

        # Copy and update non-translatable files
        # TODO: copyfiletype and copyfile lines (299-312)

        # Clean up where we made real tabs \t
        if mozversion < '3':
            run('sed -i "/^USAGE_MSG/s/\\\t/\t/g" %s/%s/toolkit/installer/unix/install.it' % (l10ndir, buildlang))
            run('sed -i "/^#define MSG_USAGE/s/\\\t/\t/g" %s/%s/browser/installer/installer.inc' % (l10ndir, buildlang))

        # Fix bookmark file to point to the locale
        # FIXME - need some way to preserve this file if its been translated already
        run('sed -i "s/en-US/%s/g" %s/%s/browser/profile/bookmarks.html' % (buildlang, l10ndir, buildlang))

def create_diff(langs):
    """Create CVS-diffs for all languages."""

    if not os.path.isdir('diff'):
        os.mkdir('diff')

    for lang in langs:
        buildlang = lang.replace('_', '-')
        olddir = os.getcwd()

        os.chdir(l10ndir)
        outfile = join(os.pardir, 'diff', lang+'-l10n.diff')
        run('cvs diff --newfile %s > %s' % (buildlang, outfile))
        os.chdir(olddir)

        os.chdir(join(podir_updated, lang))
        outfile = join(os.pardir, os.pardir, 'diff', lang+'-po.diff')
        run('svn diff --diff-cmd diff -x "-u --ignore-matching-lines=^\"POT\|^\"X-Gene" > %s' % (outfile))
        os.chdir(olddir)

def create_langpacks(langs):
    """Builds a XPI and installers for languages."""
    for lang in langs:
        buildlang = lang.replace('_', '-')

        olddir = os.getcwd()

        os.chdir(mozilladir)
        run('./configure --disable-compile-environment --disable-xft --enable-application=%s' % (targetapp))
        os.chdir(olddir)

        os.chdir(join(mozilladir, targetapp, 'locales'))
        langpack_name = 'langpack-' + buildlang
        moz_brand_dir = join('other-licenses', 'branding', 'firefox')
        langpack_file = join("'$(_ABS_DIST)'", 'install', "Firefox-Languagepack-'$(MOZ_APP_VERSION)'-%s.'$(AB_CD)'.xpi" % langpack_release)
        run('make %s MOZ_BRANDING_DIRECTORY=%s LANGPACK_FILE=%s' % (langpack_name, moz_brand_dir, langpack_file))
        # The commented out (and very long) line below was found commented out in the source script as well.
        #( cd $mozilladir/$targetapp/locales; make repackage-win32-installer-af MOZ_BRANDING_DIRECTORY=other-licenses/branding/firefox WIN32_INSTALLER_IN=../../../Firefox-Setup-2.0.exe WIN32_INSTALLER_OUT='$(_ABS_DIST)'"/install/sea/Firefox-Setup-"'$(MOZ_APP_VERSION).$(AB_CD)'".exe" )
        os.chdir(olddir)


def create_option_parser():
    """Creates and returns cmd-line option parser."""

    from optparse import OptionParser

    parser = OptionParser(usage=USAGE)

    parser.add_option(
        '--mozilla-product',
        dest='mozproduct',
        default=DEFAULT_TARGET_APP,
        help='Which product to build'
    )
    parser.add_option(
        '--mozilla-checkout',
        dest='mozcheckout',
        action='store_true',
        default=False,
        help="Update of the Mozilla l10n files and POT files"
    )
    parser.add_option(
        '--recover',
        dest='recover',
        action='store_true',
        default=False,
        help="build PO files from Mozilla's l10n files"
    )
    parser.add_option(
        '--mozilla-tag',
        dest='moztag',
        default='-A',
        help='The tag to check out of CVS (implies --mozilla-checkout)'
    )
    parser.add_option(
        '--update-translations',
        dest='update_translations',
        action='store_true',
        default=False,
        help="Update translations"
    )
    parser.add_option(
        '--diff',
        dest='diff',
        action='store_true',
        default=False,
        help='Create diffs for migrated translations and localized Mozilla files'
    )
    parser.add_option(
        '--potpack',
        dest='potpack',
        action='store_true',
        default=False,
        help="Create packages of the en-US and POT directories with today's timestamp"
    )
    parser.add_option(
        '--popack',
        dest='popack',
        action='store_true',
        default=False,
        help="Create packages of all specified languages' PO-files with today's timestamp"
    )
    parser.add_option(
        '--langpack',
        dest='langpack',
        action='store_true',
        default=False,
        help="Build a langpack"
    )
    parser.add_option(
        '--debug',
        dest='debug',
        action='store_true',
        default=False,
        help="Add podebug debug markers"
    )

    return parser

def main(
        langs=['ALL'], mozproduct='browser', mozcheckout=False, moztag='-A',
        recover=False, potpack=False, popack=False, update_trans=False,
        debug=False, diff=False, langpack=False
        ):
    targetapp = mozproduct
    langs = get_langs(langs)

    if mozcheckout:
        checkout(moztag, langs)

    if recover:
        recover_langs(langs)

    if potpack:
        pack_pot()

    migrate_langs(langs, recover, update_trans, debug)

    if popack:
        pack_po(langs)

    if diff:
        create_diff(langs)

    if langpack:
        create_langpacks(langs)


def main_cmd_line():
    options, args = create_option_parser().parse_args()

    main(
        langs=args,
        mozproduct=targetapp,
        mozcheckout=options.mozcheckout,
        moztag=options.moztag,
        recover=options.recover,
        potpack=options.potpack,
        popack=options.popack,
        update_trans=options.update_translations,
        debug=options.debug,
        diff=options.diff,
        langpack=options.langpack
    )

if __name__ == '__main__':
    main_cmd_line()
