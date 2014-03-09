#!/bin/bash

source $(dirname $0)/test.inc.sh

pocount --short --csv .
check_results
