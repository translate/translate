#!/bin/bash

source $(dirname $0)/test.inc.sh

pocount $one --no-color
check_results
