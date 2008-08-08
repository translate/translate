#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2008 Zuza Software Foundation
#
# This file is part of Spelt
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
import shutil
import tempfile

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
podir_updated = podir + '-updated'
potpacks = "potpacks"

USAGE='Usage: %prog [options] <langs...|ALL>'

def run(cmd):
    print '$$$ ' + cmd
    if cmd.startswith('cvs') or cmd.startswith('make'):
        return -1
    return os.system(cmd)

def get_langs(lang_args):
    """Returns the languages to handle based on the languages specified on the
        command-line.

        If "ALL" was specified, the languages are read from the Mozilla
        product's C{shipped-locales} file. If "ZA" was specified, all South
        African languages are selected.
        """

    langs = []

    if not lang_args:
        print USAGE
        exit(1)

    if lang_args[0] == 'ALL':
        # Get all available languages from the locales file
        locales_filename = os.path.join(mozilladir, targetapp, 'locales', 'shipped-locales')
        for line in open(locales_filename).readlines():
            langs.append(line.split()[0])

    elif lang_args[0] == 'ZA':
        # South African languages
        langs =["af", "en_ZA", "nr", "nso", "ss", "st", "tn", "ts", "ve", "xh", "zu"]
    else:
        langs = lang_args

    return langs

def checkout(cvstag, langs):
    """Check-out needed files from Mozilla's CVS."""

    olddir = os.getcwd()
    if cvstag != '-A':
        cvstag = "-r %s" % (cvstag)

    if not os.path.exists(mozilladir):
        run(
            'cvs -d:pserver:anonymous@cvs-mirror.mozilla.org:/cvsroot co %(tag)s %(mozdir)s/client.mk' % \
            {'tag': cvstag, 'mozdir': mozilladir}
        )
        run(
            'cvs -d:pserver:anonymous@cvs-mirror.mozilla.org:/cvsroot co %(mozdir)s/tools/l10n' % \
            {'mozdir': mozilladir}
        )

    os.chdir(mozilladir)
    pass # run('cvs up %(tag)s client.mk' % {'tag': cvstag})
    run('make -f client.mk l10n-checkout MOZ_CO_PROJECT=%s' % (targetapp))
    if not os.path.exists(l10ndir):
        run('cvs -d:pserver:anonymous@cvs-mirror.mozilla.org:/l10n co -d %s -l l10n' % (l10ndir))

    os.chdir(l10ndir)
    for lang in langs:
        if os.path.exists(lang):
            run('cvs up %s' % (lang))
        else:
            run('cvs -d:pserver:anonymous@cvs.mozilla.org:/l10n co %s' % lang)

    # Make latest POT file
    shutil.rmtree('en-US')
    shutil.rmtree('pot')

    os.chdir(os.path.join(olddir, mozilladir))
    run('cvs up tools/l10n')
    run('python tools/l10n/l10n.py --dest="../%s" --app=%s en-US' % (l10ndir, targetapp))
    os.chdir(olddir)

    os.chdir(l10ndir)
    moz2po.main(["-P", "--duplicates=msgctxt", "en-US", "pot"])

    if mozversion != '3':
        for f in [  'en-US/browser/README.txt pot/browser/README.txt.pot',
                    'en-US/browser/os2/README.txt pot/browser/os2/README.txt.pot',
                    'en-US/mail/README.txt pot/mail/README.txt.pot',
                    'en-US/mail/os2/README.txt pot/mail/os2/README.txt.pot' ]:
            txt2po.main(['-P', f])

    os.chdir(olddir)

def pack_pot():
    import time
    global timestamp
    timestamp = time.strftime('%Y%m%d')

    try:
        os.makedirs(potpacks)
    except OSError:
        pass

    run('tar cjf %(potpacks)s/%(targetapp)s-%(mozversion)s-%(timestamp)s.tar.bz2 %(l10ndir)s/en-US %(l10ndir)s/pot' % globals())
    run('zip -qr9 %(potpacks)s/%(targetapp)s-%(mozversion)s-%(timestamp)s.zip %(l10ndir)s/en-US %(l10ndir)s/pot' % globals())

def pre_po2moz_hacks(lang, buildlang, debug):
    """Hacks that should be run before running C{po2moz}."""

    # Protect the real original PO dir
    temp_po = tempfile.mkdtemp()
    for f in glob.glob(os.path.join(podir, lang, '*')):
        shutil.copy2(f, temp_po)

    if lang in ['zu', 'xh']:
        dirname = os.path.join(temp_po, 'editor', 'ui')
        shutil.rmtree(dirname)
        os.makedirs(dirname)
        shutil.move(os.path.join(temp_po, 'editor', 'chrome'), dirname)

    # Fix for languages that have no Windows codepage
    if lang == 've':
        src  = os.path.join(podir, 'en_ZA', 'browser', 'installer', '*.properties')
        dest = os.path.join(temp_po, 'browser', 'installer')
        shutil.copytree(src, dest)

    old = temp_po
    new = os.path.join(podir_updated, lang)
    templates = os.path.join(l10ndir, 'pot')
    run('pomigrate2 --use-compendium --quiet --pot2po %s %s %s' % (old, new, templates))

    # FIXME: The line below should be replaced with a os.path.walk/os.unlink combo
    run('rm -f `find %s/%s -name "*.xhtml.po" -o -name "*.html.po"`' % (podir_updated, lang))

    if debug:
        olddir = os.getcwd()
        os.chdir(os.path.join("%s" % (podir_updated), lang))
        run('podebug --errorlevel=traceback --ignore=mozilla . .')
        os.chdir(olddir)

    # Create l10n related files
    if os.path.isdir( os.path.join(l10ndir, buildlang) ):
        dir = os.path.join(l10ndir, buildlang)
        # FIXME: The line below should be replaced with a os.path.walk/os.unlink combo
        run('rm -rf `find %s -name "*.properties" -o -name "*.dtd"`' % (dir))

    shutil.rmtree(temp_po)

def post_po2moz_hacks(lang, buildlang):
    """Hacks that should be run after running C{po2moz}."""

    # Hack to fix creating Thunderber installer
    inst_inc_po = os.path.join(podir_updated, lang, 'mail', 'installer', 'installer.inc.po')
    if os.path.isfile(inst_inc_po):
        tempdir = tempfile.mkdtemp()
        tmp_po = os.path.join(tempdir, 'installer.%s.properties.po' % (lang))
        shutil.copy2(inst_po, tmp_po)

        inst_inc = os.path.join(l10ndir, 'en-US', 'mail', 'installer', 'installer.inc')
        tmp_properties = os.path.join(tempdir, 'installer.properties')
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
            os.path.join(l10ndir, buildlang, 'mail', 'installer', 'installer.inc')
        )

        shutil.rmtree(tempdir)

def process_langs(langs, update_transl, debug):
    for lang in langs:
        print 'Language: %s' % (lang)

        buildlang=lang.replace('_', '-')

        if update_transl:
            olddir = os.getcwd()
            os.chdir(podir)
            run('svn up %s' % (lang))
            os.chdir(olddir)

            os.chdir(l10ndir)
            run('cvs up %s' % (lang))
            os.chdir(olddir)

        # Migrate language from current PO to latest POT
        if os.path.isdir(podir):
            shutil.rmtree( os.path.join(podir_updated, '.svn') )
            shutil.copytree( os.path.join(podir, '.svn'), podir_updated )
            shutil.rmtree( os.path.join(podir_updated, lang) )
            shutil.copytree( os.path.join(podir, lang), podir_updated )
            # FIXME: The line below should be replaced with a os.path.walk/os.unlink combo
            run('rm -f `find %s/%s -name "*.po"`' % (podir_updated, lang))

        pre_po2moz_hacks(lang, buildlang, debug)

        use_fuzzy = debug and '--fuzzy' or ''

        ###################################################
        po2moz.main(
            [
                '--errorlevel=traceback',
                '--exclude=".svn"',
                use_fuzzy,
                '-t', os.path.join(l10ndir, 'en-US'),
                os.path.join(podir_updated, lang),
                os.path.join(l10ndir, buildlang)
            ]
        )
        ###################################################

        post_po2moz_hacks(lang, buildlang)

        # Copy and update non-translatable files
        # TODO: copyfiletype and copyfile lines (299-312)

        # Clean up where we made real tabs \t
        if mozversion != '3':
            run('sed -i "/^USAGE_MSG/s/\\\t/\t/g" %s/%s/toolkit/installer/unix/install.it' % (l10ndir, buildlang))
            run('sed -i "/^#define MSG_USAGE/s/\\\t/\t/g" %s/%s/browser/installer/installer.inc' % (l10ndir, buildlang))

        # Fix bookmark file to point to the locale
        # FIXME - need some way to preserve this file if its been translated already
        run('sed -i "s/en-US/%s/g" %s/%s/browser/profile/bookmarks.html' % (buildlang, l10ndir, buildlang))

def create_diff(langs):
    """Create CVS-diffs for all languages."""

    for lang in langs:
        buildlang = lang.replace('_', '-')
        olddir = os.getcwd()

        os.chdir(l10ndir)
        outfile = os.path.join('..', 'diff', lang+'-l10n.diff')
        run('cvs diff --newfile %s > %s' % (buildlang, outfile))
        os.chdir(olddir)

        os.chdir(os.path.join(podir_updated, lang))
        outfile = os.path.join('..', '..', 'diff', lang+'-po.diff')
        run('svn diff --diff-cmd diff -x "-u --ignore-matching-lines=^\"POT\|^\"X-Gene" > %s' % (outfile))
        os.chdir(olddir)

def create_langpacks(langs):
    """Builds a XPI and installers for languages."""
    for lang in langs:
        olddir = os.getcwd()

        buildlang = lang.replace('_', '-')

        os.chdir(mozilladir)
        run('./configure --disable-compile-environment --disable-xft --enable-application=%s' % (targetapp))
        langpack_name = 'langpack-' + buildlang
        moz_brand_dir = os.path.join('other-licenses', 'branding', 'firefox')
        langpack_file = os.path.join('$(_ABS_DIST)', 'install', 'Firefox-Languagepack-$(MOZ_APP_VERSION)-%s.$(AB_CD).xpi' % langpack_release)
        run('make %s MOZ_BRANDING_DIRECTORY=%s LANGPACK_FILE=%s' % (langpack_name, moz_brand_dir, langpack_file))
        # The commented out (and very long) line below was found commented out in the source script as well.
        #( cd $mozilladir/$targetapp/locales; make repackage-win32-installer-af MOZ_BRANDING_DIRECTORY=other-licenses/branding/firefox WIN32_INSTALLER_IN=../../../Firefox-Setup-2.0.exe WIN32_INSTALLER_OUT='$(_ABS_DIST)'"/install/sea/Firefox-Setup-"'$(MOZ_APP_VERSION).$(AB_CD)'".exe" )

        os.chdir(olddir)

def recover(langs):
    olddir = os.getcwd()

    os.chdir(mozilladir)
    for lang in langs:
        moz2po.main(
            [
                '--errorlevel=traceback', '--duplicates=msgctxt',
                '--exclude=.#*',
                '-t', os.path.join(l10ndir, 'en-US'),
                os.path.join(l10ndir, lang),
                os.path.join(podir, lang)
            ]
        )
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
    parser.add_option(
        '--recover',
        dest='recover',
        action='store_true',
        default=False,
        help="build PO files from Mozilla's l10n files"
    )

    return parser

def main():
    options, args = create_option_parser().parse_args()
    targetapp = options.mozproduct
    langs = get_langs(args)

    if options.mozcheckout:
        checkout(options.moztag, langs)

    if options.recover:
        recover(langs)

    if options.potpack:
        pack_pot()

    process_langs(langs, options.update_translations, options.debug)

    if options.diff:
        create_diff(langs)

    if options.langpack:
        create_langpacks(langs)



if __name__ == '__main__':
    main()
