#!/bin/bash
# This script generates a python file that tests the detection of language code
# from the team information in the .mo files in /usr/share/locale.

cd /usr/share/locale/
cat <<EOF
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# A generated test script to test the detection of language code the team
# information found in the .mo files in /usr/share/locale.

from translate.lang.team import guess_language

EOF

for lang in $(ls)
do
	echo "print \"LANGUAGE: $lang\""
	for translation in $(find $lang -name "*.mo")
	do
		msgunfmt $translation | msgconv --to-code=utf-8 --no-wrap
	done | egrep "Language-Team:" | sort -u | sed "s/\"Language-Team:/print guess_language(u\"/;s/\\\\n\"$/\"\)/"
done
