#!/bin/bash

source $(dirname $0)/test.inc.sh

pofilter --listfilters
check_results
