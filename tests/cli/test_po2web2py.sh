#!/bin/bash

source $(dirname $0)/test.inc.sh

po2web2py --progress=none $one $out
check_results
