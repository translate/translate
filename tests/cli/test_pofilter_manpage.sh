#!/bin/bash

source $(dirname $0)/test.inc.sh

python $PYTHON_ARGS $(which pofilter) --manpage
check_results
