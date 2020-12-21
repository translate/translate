#!/bin/bash

source $(dirname $0)/test.inc.sh

python $PYTHON_ARGS $(which po2json) --removeuntranslated --progress=none -t $template $translations $out
check_results
