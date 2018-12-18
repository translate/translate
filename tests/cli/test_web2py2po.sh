#!/bin/bash

source $(dirname $0)/test.inc.sh

web2py2po --progress=none $one $out
check_results
