#!/bin/bash

source $(dirname $0)/test.inc.sh

prop2po $one $out
check_results
