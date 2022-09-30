#!/bin/bash

# Import the test framework
source $(basename $0)/test.inc.sh

# You can put any extra preperation here

# Your actual command line to test No need for redirecting to /dev/stdout as
# the test framework will do that automatically
myprogram $one $two -o $out

# Check that the results of the test match your reference resulst
check_results  # does start_check and diff_all

# OR do the following
# start_checks - begin checking
# has_stdout|has_stderr|has $file - checks that the file exists we don't care for content
# startswith $file|startswith_stderr|startswith_stdout - the output starts with some expression
# startswithi $file|startswithi_stderr|startswithi_stdout - case insensitive startswith
# end_checks
