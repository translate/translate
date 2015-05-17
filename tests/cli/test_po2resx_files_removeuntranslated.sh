#!/bin/bash

source $(dirname $0)/test.inc.sh

po2resx --removeuntranslated --progress=none -t $template $translations $out
check_results
