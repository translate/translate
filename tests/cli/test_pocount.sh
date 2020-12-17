#!/bin/bash

source $(dirname $0)/test.inc.sh

python $PYTHON_ARGS $(which pocount)
start_checks
startswithi_stderr "Usage"
end_checks
