#!/bin/bash

source $(dirname $0)/test.inc.sh

prop2po --progress=none $one $out
check_results
