#!/bin/bash

source $(dirname $0)/test.inc.sh

# out == fr-af.po
poswap --progress=none -t $af $fr $out
check_results
