#!/bin/bash

source $(dirname $0)/test.inc.sh

flatxml2po --progress=none $one $out
check_results
