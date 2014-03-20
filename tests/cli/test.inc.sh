#!/bin/bash

# Config
basedir=$(dirname $0)
data=data
results=results
base_data_dir=$basedir/$data
base_results_dir=$basedir/$results


# Automatic variable setup
test_name=$(basename $0 .sh)
datadir=$base_data_dir/$test_name
resultsdir=$base_results_dir/$test_name

function _make_file {
	base=$1
	name=$2
	ext=${3:-"txt"}
	echo ${base}/${name}.${ext}
}

function make_result_file {
	_make_file $resultsdir $1 $2
}

function make_data_file {
	_make_file $datadir $1 $2
}

function _make_dir {
	base=$1
	name=$2
	echo ${base}/${name}
}

function make_result_dir {
	_make_dir $resultdir $1
}

function make_data_dir {
	_make_dir $datadir $1
}

# Create automatic variables
# Find files in $datadir that match the test name
# Create a variable name after $test/$var.ext
# For results files e.g. stdout, stderr and out we create those in the $results
# dir and create a $var_expected for the $data dir
# So you can diff $out $out_expected etc
for file in $(ls ${datadir}/*)
do
	[[ -f $file ]] && var=$(basename $file | sed "s/\([^.]*\)[.][^.]*$/\1/")
	[[ -d $file ]] && var=$file
	if [[ ("$var" == "out") || ("$var" == "stdout") || ("$var" == "stderr") ]]; then
		eval ${var}_expected=$file
		file=$(echo $file | sed "s/$data/$results/")
	fi
	eval $var=$file
done
if [[ ! "$out" ]]; then
	out=$(make_result_file out)
	out_expected=/dev/null
fi
if [[ ! "$stdout" ]]; then
	stdout=$(make_result_file stdout)
	stdout_expected=/dev/null
fi
if [[ ! "$stderr" ]]; then
	stderr=$(make_result_file stderr)
	stderr_expected=/dev/null
fi


# Redirecting stdout and stderr

function redirect {
	exec 5>&1
	exec 6>&2
	exec 1>$stdout
	exec 2>$stderr
}

function unredirect {
	exec 1>&5 5>&-
	exec 2>&6 6>&-
}

function redirect_for_prep {
	stdout=$(echo $stdout | sed "s/$results/$data/")
	stderr=$(echo $stderr | sed "s/$results/$data/")
}


# Commands

function tdiff {
	# Special test diff that will do special adaptations depending on what
	# format it is diffing and that will recurse when dealing with
	# directories
	options="-u -N"
	[[ -d $1 ]] && options="$options -r"
	[[ "$*" ]] && diff $options --ignore-matching-lines='^"POT-Creation'  --ignore-matching-lines='^"X-Generator' $*
}

# Handle failures

function FAIL {
	failures=$(($failures + 1))
}

# Check resuls of the tests
function start_checks {
	unredirect
}

function end_checks {
	exit $failures
}

function check_results {
	unredirect
	if [[ ! "$prepmode" ]]; then
		tdiff $out_expected $out || FAIL && rm -rf $out
		tdiff $stdout_expected $stdout || FAIL && rm -rf $stdout
		tdiff $stderr_expected $stderr || FAIL && rm -rf $stderr
	fi
	if [[ "$prepmode" ]]; then
		[[ ! -s "$stdout" ]] && rm $stdout
		[[ ! -s "$stderr" ]] && rm $stderr
	fi
	end_checks
}

function has {
	file=$1
	[[ -f $1 ]] || FAIL
}

function has_stdout {
	has $stdout
}

function has_stderr {
	has $stderr
}

function startswith {
	file=$1
	search_string=$2
	(head -1 $file | egrep -q "^$search_string") || FAIL
}

function startswithi {
	file=$1
	search_string=$2
	head -1 $file | egrep -q -i "^$search_string" || FAIL
}

function startswith_stdout {
	startswith $stdout $1
}

function startswith_stderr {
	startswith $stderr $1
}

function startswithi_stdout {
	startswithi $stdout $1
}

function startswithi_stderr {
	startswithi $stderr $1
}

function contains {
	file=$1
	search_string=$2
	egrep -q "$search_string" || FAIL
}

function contains_stdout {
	contains $stdout $1
}

function contains_stderr {
	contains $stderr $1
}

function containsi {
	file=$1
	search_string=$2
	egrep -q -i "$search_string" || FAIL
}

function containsi_stdout {
	containsi $stdout $1
}

function contains_stderr {
	containsi $stderr $1
}

function endswith {
	file=$1
	search_string=$2
	(tail -1 $file | egrep -q "$search_string$") || FAIL
}

function endswithi {
	file=$1
	search_string=$2
	tail -1 $file | egrep -q -i "$search_string$" || FAIL
}

function endswith_stdout {
	endswith $stdout $1
}

function endswith_stderr {
	endswith $stderr $1
}

function endswithi_stdout {
	endswithi $stdout $1
}

function endswithi_stderr {
	endswithi $stderr $1
}

# Options

function usage {
	echo
	echo "Usage: $(basename $0)"
	echo 
	echo "With no options the test will run and show diffs for any failures"
	echo "--help - show this help"
	echo "--prep - prepare files, i.e. don't check but intialise output files"
	echo
	exit 0
}

function check_options {
	for option in $*
	do
		case $option in
			--help)
				usage
				;;
			--prep)
				prepmode="yes"
				redirect_for_prep
				shift
				;;
			*)
				break
				;;
		esac
	done
}

#####################
# Execution
####################

check_options $*

# Initial setup
mkdir -p $resultsdir

# Need to do this on source'ing this file so that tests redirect correcly but
# after all the data is setup
redirect
