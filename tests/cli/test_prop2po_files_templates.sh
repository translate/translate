#!/bin/bash

source $(dirname $0)/test.inc.sh

python $PYTHON_ARGS $(which prop2po) --progress=none -t $one $two $out
check_results
