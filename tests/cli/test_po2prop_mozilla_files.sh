#!/bin/bash

source $(dirname $0)/test.inc.sh

python $PYTHON_ARGS $(which po2prop) --personality=mozilla --progress=none -t $template $translations $out
check_results
