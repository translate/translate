#!/bin/bash

source $(dirname $0)/test.inc.sh

# out == en-af.po
python $PYTHON_ARGS $(which poswap) --progress=none --reverse -t $fr_af $fr $out
check_results
