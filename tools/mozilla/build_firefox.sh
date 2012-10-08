#!/bin/bash -e
#
# Copyright 2009 João Miguel Neves <joao.neves@intraneia.com>
# Copyright 2008 Zuza Software Foundation
#
# This file is part of Translate.
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

abs_start_time=$(date +%s)
start_time=$abs_start_time
opt_vc="yes"
opt_build_xpi=""
opt_compare_locales="yes"
opt_copyfiles="yes"
opt_verbose=""
opt_time=""

progress=none
errorlevel=traceback
export USECPO=0
hgverbosity="--quiet" # --verbose to make it noisy
gitverbosity="--quiet" # --verbose to make it noisy
pomigrate2verbosity="--quiet"
get_moz_enUS_verbosity=""
easy_install_verbosity="--quiet"


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
			--no-compare-locales)
				opt_compare_locales=""
			;;
			--no-copyfiles)
				opt_copyfiles=""
			;;
			--verbose)
				opt_verbose="yes"
				hgverbosity="--verbose"
				gitverbosity=""
				progress=bar
				pomigrate2verbosity=""
				get_moz_enUS_verbosity="-v"
				easy_install_verbosity="--verbose"
			;;
			--time)
				opt_time="yes"
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
	HG_LANGS="ach af ak am cy en-ZA ff gd hi-IN hz ki lg ng nso ny sah son st-LS su sw tn ur ve wo xog zu"
	COUNT_LANGS=25
else
	HG_LANGS=$*
	COUNT_LANGS=$#
fi

function verbose() {
	if [ "$opt_verbose" -o "$opt_time" ]; then
		info_color=32 # Green
		time_color=34 # Blue
		end_time=$(date +%s)
		time_diff=$(($end_time - $start_time))
		echo -e "\033[${info_color}mINFO:\033[0m $1 [previous step \033[${time_color}m$time_diff sec\033[0m]"
		start_time=$end_time
	fi
}

# FIXME lets make this the execution directory
BUILD_DIR="$(pwd)"
MOZ_DIR="mozilla-aurora"
MOZCENTRAL_DIR="${BUILD_DIR}/${MOZ_DIR}"
L10N_DIR="${BUILD_DIR}/l10n"
PO_DIR="${BUILD_DIR}/po"
TOOLS_DIR="${BUILD_DIR}/tools"
POUPDATED_DIR="${BUILD_DIR}/po-updated"
# FIXME we should build this from the get_moz_enUS script
PRODUCT_DIRS="browser dom netwerk security services/sync toolkit mobile embedding" # Directories in language repositories to clear before running po2moz
LANGPACK_DIR="${BUILD_DIR}/xpi"

# Include current dir in path (for buildxpi and others)
CURDIR=$(dirname $0)
if [ "$CURDIR" == "" -o  "$CURDIR" == '.' ]; then
    CURDIR=$(pwd)
fi
PATH=${CURDIR}:${PATH}

# Make sure all directories exist
for dir in ${L10N_DIR} ${LANGPACK_DIR}
do
	[ ! -d ${dir} ] && mkdir -p ${dir}
done

# Compute relative paths of ${L10N_DIR} and ${POUPDATED_DIR}.
# (This assumes that both directories are sub-directories of ${BUILD_DIR}
L10N_DIR_REL=`echo ${L10N_DIR} | sed "s#${BUILD_DIR}/##"`
POUPDATED_DIR_REL=`echo ${POUPDATED_DIR} | sed "s#${BUILD_DIR}/##"`

if [ $opt_vc ]; then
	verbose "Translate Toolkit - update/pull using Git"
	if [ -d ${TOOLS_DIR}/translate/.git ]; then
		(cd ${TOOLS_DIR}/translate/
		git stash $gitverbosity
		git pull $gitverbosity --rebase
		git checkout $gitverbosity
		git stash pop $gitverbosity || true)
	else
		git clone $gitverbosity git@github.com:translate/translate.git ${TOOLS_DIR}/translate || git clone $gitverbosity git://github.com/translate/translate.git ${TOOLS_DIR}/translate
	fi
fi

if [ $opt_vc ]; then
	verbose "Compare-Locales - update if needed"
	sudo easy_install $easy_install_verbosity --upgrade compare-locales
fi

export PYTHONPATH="${TOOLS_DIR}/translate":"$PYTHONPATH"
export PATH="${TOOLS_DIR}/translate/tools":\
"${TOOLS_DIR}/translate/translate/convert":\
"${TOOLS_DIR}/translate/translate/tools":\
"${TOOLS_DIR}/translate/translate/filters":\
"${TOOLS_DIR}/translate/tools/mozilla":\
"$PATH"

if [ $opt_vc ]; then
	verbose "${MOZ_DIR} - update/pull using Mercurial"
	if [ -d "${MOZCENTRAL_DIR}/.hg" ]; then
		cd ${MOZCENTRAL_DIR}
		hg pull $hgverbosity -u
		hg update $hgverbosity -C
	else
		hg clone $hgverbosity http://hg.mozilla.org/releases/${MOZ_DIR}/ ${MOZCENTRAL_DIR}
	fi
fi

if [ $opt_vc ]; then
	verbose "Translations - prepare the parent directory po/"
	if [ -d ${PO_DIR} ]; then
		(cd ${PO_DIR}
		git stash $gitverbosity
		git pull $gitverbosity --rebase
		git checkout $gitverbosity
		git stash pop $gitverbosity || true)
	else
		git clone $gitverbosity git@github.com:translate/mozilla-l10n.git ${PO_DIR} || git clone $gitverbosity git://github.com/translate/mozilla-l10n.git ${PO_DIR}
	fi
	if [ -d ${POUPDATED_DIR} -a ! -d ${POUPDATED_DIR}/.git ]; then
		git clone $gitverbosity ${PO_DIR} ${POUPDATED_DIR}
	fi
fi

verbose "Localisations - update Mercurial-managed languages in l10n/"
cd ${L10N_DIR}
for lang in ${HG_LANGS}
do
	if [ $opt_vc ]; then
		verbose "Update l10n/$lang"
		if [ -d ${lang} ]; then
			if [ -d ${lang}/.hg ]; then
			        (cd ${lang}
				hg revert $hgverbosity --no-backup --all -r default
				hg pull $hgverbosity -u
				hg update $hgverbosity -C)
			else
			        rm -rf ${lang}/* 
			fi
		else
		    hg clone $hgverbosity http://hg.mozilla.org/releases/l10n/${MOZ_DIR}/${lang} ${lang} || mkdir ${lang}
		fi
	fi
done

[ -d pot ] && rm -rf pot

verbose "Extract the en-US source files from the repo into localisation structure in l10n/en-US"
rm -rf en-US
get_moz_enUS.py $get_moz_enUS_verbosity -s ../${MOZ_DIR} -d . -p browser
get_moz_enUS.py $get_moz_enUS_verbosity -s ../${MOZ_DIR} -d . -p mobile

verbose "moz2po - Create POT files from l10n/en-US"
moz2po --errorlevel=$errorlevel --progress=$progress -P --duplicates=msgctxt --exclude '.hg' en-US pot

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

function copyfileifmissing {
	filename=$1
	language=$2
	if [ ! -f ${L10N_DIR}/$language/$filename ]; then
		copyfile $1 $2
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

verbose "Translations - build l10n/ files"
for lang in ${HG_LANGS}
do
	[ $COUNT_LANGS -gt 1 ] && echo "Language: $lang"
        polang=$(echo $lang|sed "s/-/_/g")
	verbose "Update existing po/$lang in case any changes are in version control"
	(cd ${PO_DIR};
		git stash $gitverbosity
		git pull $gitverbosity --rebase
		git checkout $gitverbosity
		git stash pop $gitverbosity || true)

	if [ -d ${PO_DIR}/${polang} ]; then
		verbose "Copy directory structure while preserving version control metadata"
		rm -rf ${POUPDATED_DIR}/${polang}
		cp -R ${PO_DIR}/${polang} ${POUPDATED_DIR}
		(cd ${POUPDATED_DIR/${polang}; find $PRODUCT_DIRS -name '*.po' -exec rm -f {} \;)
	fi

	verbose "Migrate - update PO files to new POT files"
	tempdir=`mktemp -d tmp.XXXXXXXXXX`
	[ -d ${PO_DIR}/${polang} ] && cp -R ${PO_DIR}/${polang} ${tempdir}/${polang}
	pomigrate2 --use-compendium --pot2po $pomigrate2verbosity ${tempdir}/${polang} ${POUPDATED_DIR}/${polang} ${L10N_DIR}/pot
	rm -rf ${tempdir}

	(cd ${POUPDATED_DIR}
	if [ $USECPO -eq 0 ]; then
		verbose "Migration cleanup - fix migrated PO files using msgcat"
		(cd ${polang}
		for po in $(find ${PRODUCT_DIRS} -name "*.po")
		do
			msgcat -o $po.2 $po 2> >(egrep -v "warning: internationali[zs]ed messages should not contain the .* escape sequence" >&2) && mv $po.2 $po # parallel?
		done
		)
	fi

	verbose "Migration cleanup - Revert files with only header changes"
	[ "$(git status --porcelain ${polang})" != "?? ${polang}/" ] && git checkout $gitverbosity -- $(git difftool -y -x 'diff --unified=3 --ignore-matching-lines=POT-Creation --ignore-matching-lines=X-Generator -s' ${polang} |
	egrep "are identical$" |
	sed "s/^Files.*.\.po and //;s/\(\.po\).*/\1/") || echo "No header only changes, so no reverts needed"

	verbose "Migrate to new PO files: move old to obsolete/ and add new files"
	if [ "$(git status --porcelain ${polang})" == "?? ${polang}/" ]; then
		# Not VC managed, assume it's a new language
		git add ${polang}/\*.po
	else
		(cd ${polang}
		for newfile in $(git status --porcelain $PRODUCT_DIRS | egrep "^\?\?" | sed "s/^??\w*//")
		do
			[ -f $newfile -a "$(echo $newfile | cut -d"." -f3)" = "po" ] && git add $newfile
		done

		for oldfile in $(git status --porcelain $PRODUCT_DIRS | egrep "^ D" | sed "s/^ D\w*//")
		do
			if [ -f $newfile -a "$(echo $newfile | cut -d"." -f3)" = "po" ]; then
				git checkout $gitverbosity -- $oldfile
				mkdir -p obsolete/$(dirname $oldfile)
				git mv $oldfile obsolete/$oldfile
			fi
		done
		)
	fi
	)

	verbose "Pre-po2moz hacks"
	lang_product_dirs=
	for dir in ${PRODUCT_DIRS}; do lang_product_dirs="${lang_product_dirs} ${L10N_DIR}/$lang/$dir"; done
	for product_dir in ${lang_product_dirs}
	do
		[ -d ${product_dir} ] && find ${product_dir} \( -name '*.dtd' -o -name '*.properties' \) -exec rm -f {} \;
	done

	verbose "po2moz - Create Mozilla l10n layout from migrated PO files."
	po2moz --progress=$progress --errorlevel=$errorlevel --exclude=".git" --exclude=".hg" --exclude="obsolete" --exclude="editor" --exclude="mail" --exclude="thunderbird" --exclude="chat" --exclude="*~" \
		-t ${L10N_DIR}/en-US -i ${POUPDATED_DIR}/${polang} -o ${L10N_DIR}/${lang}

	if [ $opt_copyfiles ]; then
		verbose "Copy files not handled by moz2po/po2moz"
		copyfileismissing toolkit/chrome/mozapps/help/welcome.xhtml ${lang}
		copyfileifmissing toolkit/chrome/mozapps/help/help-toc.rdf ${lang}
		copyfile browser/firefox-l10n.js ${lang}
		copyfile browser/profile/chrome/userChrome-example.css ${lang}
		copyfile browser/profile/chrome/userContent-example.css ${lang}
		copyfileifmissing toolkit/chrome/global/intl.css ${lang}
		# This one needs special approval but we need it to pass and compile
		copyfileifmissing browser/searchplugins/list.txt ${lang}
		# Revert some files that need careful human review or authorisation
		if [ -d ${L10N_DIR}/${lang}/.hg ]; then
			(cd ${L10N_DIR}/${lang}
			hg revert $hgverbosity --no-backup browser/chrome/browser-region/region.properties browser/searchplugins/list.txt
			)
		fi
	fi

	## CREATE XPI LANGPACK
	if [ $opt_build_xpi ]; then
		verbose "Language Pack - create an XPI"
		buildxpi.py -d -L ${L10N_DIR} -s ${MOZCENTRAL_DIR} -o ${LANGPACK_DIR} ${lang}
	fi

	# COMPARE LOCALES
	if [ $opt_compare_locales ]; then
		verbose "Compare-Locales - to find errors"
		compare-locales ${MOZCENTRAL_DIR}/browser/locales/l10n.ini ${L10N_DIR} $lang
		compare-locales ${MOZCENTRAL_DIR}/mobile/locales/l10n.ini ${L10N_DIR} $lang
	fi

done

# Cleanup rubbish we seem to leave behind
rm -rf ${L10N_DIR}/tmp*
abs_end_time=$(date +%s)
total_time=$(($abs_end_time - $abs_start_time))
verbose "Total time $(date --date="@$total_time" +%M:%S)"
