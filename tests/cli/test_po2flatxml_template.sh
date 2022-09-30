#!/bin/bash

source $(dirname $0)/test.inc.sh

python $PYTHON_ARGS $(which po2flatxml) --progress=none -i $one -t $two -o $out --root "dictionary" --value "translation" --key "resource" --namespace "urn:translate-toolkit:flatxml-test-suite" --indent 4
check_results
