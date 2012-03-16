#!/bin/bash -e
#
# Copyright 2009 João Miguel Neves <joao.neves@intraneia.com>
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

##########################################################################
# NOTE: Documentation regarding (the use of) this script can be found at #
# http://translate.sourceforge.net/wiki/toolkit/mozilla_l10n_scripts     #
##########################################################################

opt_vc="yes"
opt_build_xpi=""

for option in $*
do
	if [ "${option##-*}" != "$option" ]; then
		case $option in
			--xpi)
				opt_build_xpi="yes"
			;;
			--no-vc)
				opt_vc=""
			;;
			*) 
			echo "Unkown option: $option"
			exit
			;;
		esac
		shift
	else
		break
	fi
done

if [ $# -eq 0 ]; then
	HG_LANGS="ach af ak am en-ZA ff gd hz ki lg ng nso ny sah son st-LS su sw tn ur ve wo xog zu"
else
	HG_LANGS=$*
fi

# FIXME lets make this the execution directory
BUILD_DIR="$(pwd)"
MOZCENTRAL_DIR="${BUILD_DIR}/mozilla-aurora" # Change "../mozilla-central" on line 39 too if you change this var
L10N_DIR="${BUILD_DIR}/l10n"
PO_DIR="${BUILD_DIR}/po"
TOOLS_DIR="${BUILD_DIR}/tools"
POPACK_DIR="${BUILD_DIR}/popacks"
PORECOVER_DIR="${BUILD_DIR}/po-recover"
POT_INCLUDES="../README.mozilla-pot"
POTPACK_DIR="${BUILD_DIR}/potpacks"
POUPDATED_DIR="${BUILD_DIR}/po-updated"
# FIXME we should build this from the get_moz_enUS script
PRODUCT_DIRS="browser dom netwerk security services/sync toolkit mobile embedding" # Directories in language repositories to clear before running po2moz
LANGPACK_DIR="${BUILD_DIR}/xpi"
FF_VERSION="4.0b7pre"

# Include current dir in path (for buildxpi and others)
CURDIR=`dirname $0`
if [ x"$CURDIR" == x ] || [ x"$CURDIR" == x. ]; then
    CURDIR=`pwd`
fi
PATH=${CURDIR}:${PATH}

# Make sure all directories exist
for dir in ${MOZCENTRAL_DIR} ${L10N_DIR} ${PO_DIR} ${POPACK_DIR} ${PORECOVER_DIR} ${POTPACK_DIR} ${POUPDATED_DIR} ${LANGPACK_DIR}
do
	[ ! -d ${dir} ] && mkdir -p ${dir}
done

# Compute relative paths of ${L10N_DIR} and ${POUPDATED_DIR}.
# (This assumes that both directories are sub-directories of ${BUILD_DIR}
L10N_DIR_REL=`echo ${L10N_DIR} | sed "s#${BUILD_DIR}/##"`
POUPDATED_DIR_REL=`echo ${POUPDATED_DIR} | sed "s#${BUILD_DIR}/##"`

[ $opt_vc ] && if [ -d ${TOOLS_DIR} ]; then
	svn up ${TOOLS_DIR}
else
	svn co https://translate.svn.sourceforge.net/svnroot/translate/src/trunk ${TOOLS_DIR}
fi
(cd ${TOOLS_DIR}; ./setuppath)

. ${TOOLS_DIR}/setpath

if [ $opt_vc ]; then
	if [ -d "${MOZCENTRAL_DIR}/.hg" ]; then
	    cd ${MOZCENTRAL_DIR}
		hg pull -u
		hg update -C
	else
		hg clone http://hg.mozilla.org/releases/mozilla-aurora/ ${MOZVENTRAL_DIR}
	fi
    find ${MOZCENTRAL_DIR} -name '*.orig' | xargs  --no-run-if-empty rm
fi

cd ${L10N_DIR}

# Update all Mercurial-managed languages
for lang in ${HG_LANGS}
do
	if [ $opt_vc ]; then
	    if [ -d ${lang} ]; then
	        if [ -d ${lang}/.hg ]; then
		        (cd ${lang}
		    	hg revert --all -r default
		    	hg pull -u
		    	hg update -C)
			else
		        rm -rf ${lang}/* 
			fi
		else
		    hg clone http://hg.mozilla.org/releases/l10n/mozilla-aurora/${lang} ${lang} || mkdir ${lang}
	    fi
	    find ${lang} -name '*.orig' | xargs  --no-run-if-empty rm
	fi
done

[ -d pot ] && rm -rf pot

# en-US and all languages should be up-to-date now
[ -d en-US_browser ] && rm -rf en-US_browser
[ -L en-US ] && rm en-US
get_moz_enUS.py -s ../mozilla-aurora -d . -p browser -v
get_moz_enUS.py -s ../mozilla-aurora -d . -p mobile -v
mv en-US{,_browser}
ln -sf en-US_browser ./en-US
# CREATE POT FILES FROM en-US
moz2po --errorlevel=traceback --progress=none -P --duplicates=msgctxt --exclude '.hg' en-US pot
find pot \( -name '*.html.pot' -o -name '*.xhtml.pot' \) -exec rm -f {} \;

# Create POT pack
# Comment out the lines starting with "tar" and/or "zip" to keep from building archives in the specific format(s).
PACKNAME="${POTPACK_DIR}/firefox-${FF_VERSION}-`date +%Y%m%d`"
#tar chjf ${PACKNAME}.tar.bz2 pot en-US ${POT_INCLUDES}
#zip -qr9 ${PACKNAME}.zip pot en-US ${POT_INCLUDES}

# The following functions are used in the loop following it
function copyfile {
	filename=$1
	language=$2
	directory=$(dirname $filename)
	if [ -f ${L10N_DIR}/en-US/$filename ]; then
		mkdir -p ${L10N_DIR}/$language/$directory
		cp -p ${L10N_DIR}/en-US/$filename ${L10N_DIR}/$language/$directory
	fi
}

function copyfiletype {
	filetype=$1
	language=$2
	files=$(cd ${L10N_DIR}/en-US; find . -name "$filetype")
	for file in $files
	do
		copyfile $file $language
	done
}

function copydir {
	dir=$1
	language=$2
	if [ -d ${L10N_DIR}/en-US/$dir ]; then
		files=$(cd ${L10N_DIR}/en-US/$dir && find . -type f)
		for file in $files
		do
			copyfile $dir/$file $language
		done
	fi
}

for lang in ${HG_LANGS}
do
	### RECOVER - Recover PO files from existing l10n directory.
	### Comment out the following "moz2po"-line if recovery should not be done.
	#[ ! -d ${PORECOVER_DIR}/${lang} ] && mkdir -p ${PORECOVER_DIR}/${lang}
	#moz2po --progress=none --errorlevel=traceback --duplicates=msgctxt --exclude=".#*" --exclude='.hg' \
	#	-t ${L10N_DIR}/en-US ${L10N_DIR}/${lang} ${PORECOVER_DIR}/${lang}

	#[ ! -d ${PO_DIR}/${lang} ] && cp -R ${PORECOVER_DIR}/${lang} ${PO_DIR}

	# Try and update existing PO files
        polang=$(echo $lang|sed "s/-/_/g")
	updated=""
	[ -z ${updated} ] && [ -d ${PO_DIR}/${polang}/CVS ] && (cd ${PO_DIR}/${polang}; cvs up) && updated="1"
	[ -z ${updated} ] && [ -d ${PO_DIR}/${polang}/.hg ] && (cd ${PO_DIR}/${polang}; hg pull -u) && updated="1"
	[ -z ${updated} ] && [ -d ${PO_DIR}/${polang}/.svn ] && (cd ${PO_DIR}/${polang}; svn up) && updated="1"

	# Copy directory structure while preserving version control metadata
	if [ -d ${PO_DIR}/${polang} ]; then
		rm -rf ${POUPDATED_DIR}/${polang}
		cp -R ${PO_DIR}/${polang} ${POUPDATED_DIR}
		(cd ${POUPDATED_DIR/${polang}; find $PRODUCT_DIRS -name '*.po' -exec rm -f {} \;)
	fi

	## MIGRATE - Migrate PO files to new POT files.
	# Comment out the following "pomigrate2"-line if migration should not be done.
	tempdir=`mktemp -d tmp.XXXXXXXXXX`
	[ -d ${PO_DIR}/${polang} ] && cp -R ${PO_DIR}/${polang} ${tempdir}/${polang}
	pomigrate2 --use-compendium --pot2po --quiet ${tempdir}/${polang} ${POUPDATED_DIR}/${polang} ${L10N_DIR}/pot
	rm -rf ${tempdir}

	## Cleanup migrated PO files
	# msgcat to make them look the same
	(cd ${POUPDATED_DIR}/${polang}
	for po in $(find ${PRODUCT_DIRS} -name "*.po")
	do
		msgcat $po > $po.2
		mv $po.2 $po
	done
	)

	# Revert files with only header changes
	[ -d ${POUPDATED_DIR}/${polang}/.svn ] && svn revert $(svn diff --diff-cmd diff -x "--unified=3 --ignore-matching-lines=POT-Creation --ignore-matching-lines=X-Generator -s" ${POUPDATED_DIR}/${polang} |
	egrep "are identical$" |
	sed "s/^Files //;s/\(\.po\).*/\1/")

	## Migrate to new PO files: move old to obsolete/ and add new files
	if [ ! -d ${POUPDATED_DIR}/${polang}/.svn ]; then
		# No VC so assume it's a new language
		svn add ${POUPDATED_DIR}/${polang}
	else
		(cd ${POUPDATED_DIR}/${polang}
		for newfile in $(svn status $PRODUCT_DIRS | egrep "^\?" | sed "s/\?\w*//")
		do
			[ -d $newfile ] && svn add $newfile
			[ -f $newfile -a "$(echo $newfile | cut -d"." -f2)" == "po" ] && svn add $newfile
		done

		if [ -d obsolete/.svn ]; then
			svn revert -R obsolete
		else
			mkdir -p obsolete
			svn add obsolete
		fi

		for oldfile in $(svn status $PRODUCT_DIRS | egrep "^!"| sed "s/!\w*//")
		do
			if [ -d $newfile ]; then
				svn revert -R $oldfile
				svn move --parents $oldfile obsolete/$oldfile
			fi
			if [ -f $newfile -a "$(echo $newfile | cut -d"." -f2)" == "po" ]; then
				svn revert $oldfile
				svn move --parents $oldfile obsolete/$oldfile
			fi
		done
		)
	fi

	# Pre-po2moz hacks
	lang_product_dirs=
	for dir in ${PRODUCT_DIRS}; do lang_product_dirs="${lang_product_dirs} ${L10N_DIR}/$lang/$dir"; done
	for product_dir in ${lang_product_dirs}
	do
		[ -d ${product_dir} ] && find ${product_dir} \( -name '*.dtd' -o -name '*.properties' \) -exec rm -f {} \;
	done
	find ${POUPDATED_DIR} \( -name '*.html.po' -o -name '*.xhtml.po' \) -exec rm -f {} \;

	# PO2MOZ - Create Mozilla l10n layout from migrated PO files.
	# Comment out the "po2moz"-line below to prevent l10n files to be updated to the current PO files.
	po2moz --progress=none --errorlevel=traceback --exclude=".svn" --exclude=".hg" --exclude="obsolete" --exclude="editor" --exclude="mail" --exclude="thunderbird" \
		-t ${L10N_DIR}/en-US -i ${POUPDATED_DIR}/${polang} -o ${L10N_DIR}/${lang}

	# Copy files not handled by moz2po/po2moz
	copydir browser/os2 ${lang}
	copyfiletype "*.xhtml" ${lang} # Our XHTML and HTML is broken
	copyfiletype "*.html" ${lang}
	copyfiletype "*.rdf" ${lang}   # Don't support .rdf files
	copyfile browser/firefox-l10n.js ${lang}
	copyfile browser/microsummary-generators/list.txt ${lang}
	copyfile browser/profile/chrome/userChrome-example.css ${lang}
	copyfile browser/profile/chrome/userContent-example.css ${lang}
        # Ignore lists.txt since we need specil approval for that
	#copyfile browser/searchplugins/list.txt ${lang}
	#copyfile toolkit/chrome/global/intl.css ${lang}
        # Revert some files that need careful human review or authorisation
	[ -d ${L10N_DIR}/${lang}/.hg ] && (cd ${L10N_DIR}/${lang}; hg revert browser/chrome/browser-region/region.properties browser/searchplugins/list.txt)
	# These seem to have been removed for Fx4
	#[ ! -f ${L10N_DIR}/${lang}/browser/profile/bookmarks.html ] && copyfile browser/profile/bookmarks.html ${lang}
	#sed -i "s/en-US/${lang}/g" ${L10N_DIR}/${lang}/browser/profile/bookmarks.html || /bin/true

	## CREATE PO PACK - Create archives of PO files.
	# Comment out the lines starting with "tar" and/or "zip" to keep from building archives in the specific format(s).
	PACKNAME="${POPACK_DIR}/firefox-${FF_VERSION}-${polang}-`date +%Y%m%d`"
	(
		cd ${BUILD_DIR}
		#tar cjf ${PACKNAME}.tar.bz2 --exclude '.svn' --exclude '.hg' ${L10N_DIR_REL}/${lang} ${POUPDATED_DIR_REL}/${polang}
		#zip -qr9 ${PACKNAME}.zip ${L10N_DIR_REL}/${lang} ${POUPDATED_DIR_REL}/${polang} -x '*.svn*' -x "*.hg*"
	)

	## CREATE XPI LANGPACK
	[ $opt_build_xpi ] && buildxpi.py -d -L ${L10N_DIR} -s ${MOZCENTRAL_DIR} -o ${LANGPACK_DIR} ${lang}

done
