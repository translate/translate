#!/bin/bash
#
# Copyright 2008 Zuza Software Foundation
#
# This file is part of Virtaal.
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


BUILD_DIR="/home/walter/mozbuild"
MOZCENTRAL_DIR="${BUILD_DIR}/mozilla-central" # Change "../mozilla-central" on line 39 too if you change this var
#HG_LANGS="af ar as be bg bn-IN ca cs da de el en-GB en-ZA es-AR es-ES et eu fa fi fr fy-NL ga-IE gl gu-IN he hi-IN hu hy-AM id is it ja ja-JP-mac ka kn ko ku langs lt lv mk ml mn mr nb-NO ne-NP nl nn-NO nr nso pa-IN pl ro ru rw si sk sl sq sr ss st sv-SE ta te th tn tr ts uk ve xh zh-CN zh-TW zu"
HG_LANGS="fr"
L10N_DIR="${BUILD_DIR}/l10n"
PO_DIR="${BUILD_DIR}/po"
POPACK_DIR="${BUILD_DIR}/popacks"
PORECOVER_DIR="${BUILD_DIR}/po-recover"
POT_INCLUDES="../README.mozilla-pot"
POTPACK_DIR="${BUILD_DIR}/potpacks"
POUPDATED_DIR="${BUILD_DIR}/po-updated"
LANGPACK_DIR="${BUILD_DIR}/xpi"
FF_VERSION="3.1b2"

# Make sure all directories exist
for dir in ${MOZCENTRAL_DIR} ${L10N_DIR} ${PO_DIR} ${POPACK_DIR} ${PORECOVER_DIR} ${POTPACK_DIR} ${POUPDATED_DIR} ${LANGPACK_DIR}
do
	[ ! -d ${dir} ] && mkdir -p ${dir}
done

L10N_DIR_REL=`echo ${L10N_DIR} | sed "s#${BUILD_DIR}/##"`
POUPDATED_DIR_REL=`echo ${POUPDATED_DIR} | sed "s#${BUILD_DIR}/##"`

(cd ${MOZCENTRAL_DIR}; hg pull -u; python client.py checkout --skip-inspector --skip-ldap --skip-chatzilla --skip-venkman)

cd ${L10N_DIR}

rm -rf en-US pot

# Update all Mercurial-managed languages
for lang in ${HG_LANGS}
do
	[ -d ${lang}/.hg ] && (cd ${lang}; hg pull -u)
done

# en-US and all languages should be up-to-date now
get_moz_enUS.py -s ../mozilla-central -d . -p browser -v
moz2po --progress=none -P --duplicates=msgctxt --exclude '.hg' en-US pot
find pot -name '*.html.pot' -o -name '*.xhtml.pot' -exec rm -f {} \;

# Create POT pack
PACKNAME="${POTPACK_DIR}/firefox-${FF_VERSION}-`date +%Y%m%d`"
tar cjf ${PACKNAME}.tar.bz2 pot en-US ${POT_INCLUDES}
zip -qr9 ${PACKNAME}.zip pot en-US ${POT_INCLUDES}

for lang in ${HG_LANGS}
do
	## Recover
	[ ! -d ${PORECOVER_DIR}/${lang} ] && mkdir -p ${PORECOVER_DIR}/${lang}
	#moz2po --progress=none --errorlevel=traceback --duplicates=msgctxt --exclude=".#*" --exclude='.hg' \
	#	-t ${L10N_DIR}/en-US ${L10N_DIR}/${lang} ${PORECOVER_DIR}/${lang}

	## Migrate
	[ ! -d ${PO_DIR}/${lang} ] && cp -R ${PORECOVER_DIR}/${lang} ${PO_DIR}

	# Try and update existing PO files
	updated=""
	[ -z ${updated} ] && [ -d ${PO_DIR}/${lang}/CVS ] && (cd ${PO_DIR}/${lang}; cvs up) && updated="1"
	[ -z ${updated} ] && [ -d ${PO_DIR}/${lang}/.hg ] && (cd ${PO_DIR}/${lang}; hg pull -u) && updated="1"
	[ -z ${updated} ] && [ -d ${PO_DIR}/${lang}/.svn ] && (cd ${PO_DIR}/${lang}; svn up) && updated="1"

	# Copy directory structure while preserving version control metadata
	rm -rf ${POUPDATED_DIR}/${lang}
	cp -R ${PO_DIR}/${lang} ${POUPDATED_DIR}
	find ${POUPDATED_DIR}/${lang} -name '*.po' -exec rm -f {} \;

	## Migrate to new POT files
	tempdir=`mktemp -d`
	cp -R ${PO_DIR}/${lang} ${tempdir}/${lang}
	pomigrate2 --use-compendium --quiet --pot2po ${tempdir}/${lang} ${POUPDATED_DIR}/${lang} ${L10N_DIR}/pot

	# Pre-moz2po hacks
	find ${POUPDATED_DIR} -name '*.html.po' -o -name '*.xhtml.po' -exec rm -f {} \;
	[ -d ${L10N_DIR}/${lang} ] && find ${L10N_DIR}/${lang} -name '*.dtd' -o -name '*.properties' -exec rm -f {} \;
	rm -rf ${tempdir}

	## Create Mozilla l10n layout from migrated PO files
	po2moz --progress=none --errorlevel=traceback --exclude=".svn" --exclude=".hg" \
		-t ${L10N_DIR}/en-US -i ${POUPDATED_DIR}/${lang} -o ${L10N_DIR}/${lang}
	
	## Create PO pack
	PACKNAME="${POPACK_DIR}/firefox-${FF_VERSION}-${lang}-`date +%Y%m%d`"
	(
		cd ${BUILD_DIR}
		tar cjf ${PACKNAME}.tar.bz2 --exclude '.svn' --exclude '.hg' ${L10N_DIR_REL}/${lang} ${POUPDATED_DIR_REL}/${lang}
		zip -qr9 ${PACKNAME}.zip ${L10N_DIR_REL}/${lang} ${POUPDATED_DIR_REL}/${lang} -x '*.svn*' -x "*.hg*"
	)

	# Pre-langpack build hacks
	# This file is empty and therefore not created by po2moz, but is still needed to build a langpack.
	touch ${L10N_DIR}/${lang}/extensions/reporter/chrome/reporterOverlay.properties 

	## Create XPI langpack
	buildxpi.py -L ${L10N_DIR} -s ${MOZCENTRAL_DIR} -o ${LANGPACK_DIR} ${lang}
done
