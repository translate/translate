#!/bin/bash

source $(dirname $0)/test.inc.sh

rc2po --progress=none -i $one -o $out
check_results
