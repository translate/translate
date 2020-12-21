#!/bin/bash

source $(dirname $0)/test.inc.sh

python $PYTHON_ARGS $(which pocount) missing.po
check_results
