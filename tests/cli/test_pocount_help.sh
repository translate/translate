#!/bin/bash

source $(dirname $0)/test.inc.sh

pocount -h
start_checks
has_stdout
end_checks
