#!/bin/bash

source $(dirname $0)/test.inc.sh

pocount --csv $one
check_results
