#!/bin/bash

source $(dirname $0)/test.inc.sh

po2html --progress=none -t $template $one $out
check_results
