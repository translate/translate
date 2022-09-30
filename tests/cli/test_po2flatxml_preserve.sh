#!/bin/bash

source $(dirname $0)/test.inc.sh

python $PYTHON_ARGS $(which po2flatxml) --progress=none -i $one -t $two -o $out
check_results
