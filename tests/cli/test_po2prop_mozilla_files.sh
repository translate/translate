#!/bin/bash

source $(dirname $0)/test.inc.sh

po2prop --personality=mozilla --progress=none -t $template $translations $out
check_results
