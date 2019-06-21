#!/bin/bash

source $(dirname $0)/test.inc.sh

flatxml2po --progress=none $one $out --root "wrong"
check_results
