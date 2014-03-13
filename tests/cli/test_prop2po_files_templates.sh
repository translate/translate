#!/bin/bash

source $(dirname $0)/test.inc.sh

prop2po --progress=none -t $one $two $out
check_results
