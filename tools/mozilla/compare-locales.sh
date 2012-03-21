for lang in $*
do
	compare-locales ../mozilla-aurora/browser/locales/l10n.ini . $lang
	compare-locales ../mozilla-aurora/mobile/locales/l10n.ini . $lang
done
