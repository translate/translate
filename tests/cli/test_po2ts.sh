#!/bin/bash

source $(dirname $0)/test.inc.sh

po2ts --progress=none $one $out
check_results
