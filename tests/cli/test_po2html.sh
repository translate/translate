#!/bin/bash

source $(dirname $0)/test.inc.sh

python $PYTHON_ARGS $(which po2html) --progress=none -t $template $one $out
check_results
