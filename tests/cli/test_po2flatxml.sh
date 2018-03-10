#!/bin/bash

source $(dirname $0)/test.inc.sh

po2flatxml --progress=none $one $out
check_results
