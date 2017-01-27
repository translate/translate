#!/bin/bash

source $(dirname $0)/test.inc.sh

# We expect no output as translations are not complete
po2txt --progress=none --threshold=100 $one $out
check_results
