#!/bin/bash

source $(dirname $0)/test.inc.sh

pocount missing.po
check_results
