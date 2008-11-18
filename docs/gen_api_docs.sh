#!/bin/sh

# The translate toolkit must be in your PYTHONPATH when you
# build these documents.  Either install them or run:
#  . setpath
#
# The script will then find them, build docs and export them
# to sourceforge.
#
# You should also have a setup in .ssh/config that defines
# sftranslate as your sourceforge account for the translate
# project.

outputdir=apidocs/

rm -rf $outputdir
epydoc --config=epydoc-config.ini
rsync -az -e ssh --delete $outputdir sftranslate:htdocs/doc/api
