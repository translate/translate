#!/bin/bash

cd $(dirname $0)
for test in $(ls test_*.sh)
do
	echo -n "$test ... "
	eval ./$test
	result=$?
	if [ $result -ne 0 ]; then
		echo "FAIL"
	else
		echo "pass"
	fi
	failure=$(($failure + $result))
done
exit $failure
