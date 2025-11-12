#!/bin/bash

source $(dirname $0)/test.inc.sh

# out == es-qu.po with intermediate mode
python $PYTHON_ARGS $(which poswap) --progress=none --intermediate -t $en $es $out
check_results
