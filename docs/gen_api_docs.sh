#!/bin/sh

# The translate toolkit must be in your PYTHONPATH when you
# build these documents.  Either install them or run:
#  . setpath
#
# The script will then find them, build docs and export them
# to sourceforge.
#
# You should also have a setup in .ssh/config that defines
# $sfaccount with your sourceforge shell login details for 
# the translate project.
#
# EPYDOC
# ======
# See: http://epydoc.sourceforge.net/manual-epytext.html
# and: http://epydoc.sourceforge.net/fields.html#fields

outputdir=apidocs/
sfaccount=sftranslate-shell

rm -rf $outputdir
epydoc --config=epydoc-config.ini
# Create a new shell account and update the API docs
ssh $sfaccount create
rsync -azv -e ssh --delete $outputdir $sfaccount:translate/htdocs/doc/api
