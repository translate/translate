#!/bin/bash

source $(dirname $0)/test.inc.sh

po2flatxml --progress=none -i $one -t $two -o $out
check_results
