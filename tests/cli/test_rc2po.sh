#!/bin/bash

source $(dirname $0)/test.inc.sh

python $PYTHON_ARGS $(which rc2po) --progress=none -i $one -o $out
check_results
