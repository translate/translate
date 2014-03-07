#!/bin/bash

source $(dirname $0)/test.inc.sh

pofilter --manpage
check_results
