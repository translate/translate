#!/bin/bash

source $(dirname $0)/test.inc.sh

posegment --progress=none $one $out
check_results
