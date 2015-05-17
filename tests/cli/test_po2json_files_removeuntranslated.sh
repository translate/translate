#!/bin/bash

source $(dirname $0)/test.inc.sh

po2json --removeuntranslated --progress=none -t $template $translations $out
check_results
