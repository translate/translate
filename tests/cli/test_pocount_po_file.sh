#!/bin/bash

source $(dirname $0)/test.inc.sh

python $PYTHON_ARGS $(which pocount) $one --no-color
check_results
