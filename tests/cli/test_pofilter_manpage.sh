#!/bin/bash

source $(dirname $0)/test.inc.sh

python $PYTHON_ARGS $(which pofilter) --manpage | sed -E 's/"Translate Toolkit [0-9.]+"/"Translate Toolkit @VERSION@"/g'
check_results
