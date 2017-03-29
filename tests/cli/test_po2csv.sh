#!/bin/bash

source $(dirname $0)/test.inc.sh

po2csv --progress=none $one $out
check_results
