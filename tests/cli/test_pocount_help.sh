#!/bin/bash

source $(dirname $0)/test.inc.sh

python $PYTHON_ARGS $(which pocount) -h
start_checks
has_stdout
end_checks
