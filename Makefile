DOCS_DIR = docs
FORMATS=--formats=bztar

.PHONY: all build docs requirements help publish-pypi sort-imports

all: help

build: docs
	python setup.py sdist ${FORMATS}

docs:
	# The following creates the HTML docs.
	# NOTE: cd and make must be in the same line.
	cd ${DOCS_DIR}; make SPHINXOPTS="-W -q" html ${TAIL}

docs-review: docs
	python -mwebbrowser file://$(shell pwd)/${DOCS_DIR}/_build/html/index.html

publish-pypi:
	python setup.py sdist ${FORMATS} upload

sort-imports:
	isort -rc .

help:
	@echo "Help"
	@echo "----"
	@echo
	@echo "  build - create sdist with required prep"
	@echo "  docs - build Sphinx docs"
	@echo "  docs-review - launch webbrowser to review docs"
	@echo "  requirements - (re)generate pinned and minimum requirements"
	@echo "  sort-imports - sort Python imports"
	@echo "  publish-pypi - publish on PyPI"
	@echo "  test - run unit test suite"
	@echo "  test-functional - run the functional test suite"

# Perform forced build using -W for the (.PHONY) requirements target
requirements:
	$(MAKE) -W $(REQFILE) requirements/min-versions.txt requirements.txt

REQS=.reqs
REQFILE=requirements/recommended.txt

requirements.txt: $(REQFILE)
	@set -e;							\
	 case `pip --version` in					\
	   "pip 0"*|"pip 1.[012]"*)					\
	     virtualenv --no-site-packages --clear $(REQS);		\
	     source $(REQS)/bin/activate;				\
	     echo starting clean install of requirements from PyPI;	\
	     pip install --use-mirrors -r $(REQFILE);			\
	     : trap removes partial/empty target on failure;		\
	     trap 'if [ "$$?" != 0 ]; then rm -f $@; fi' 0;		\
	     pip freeze | grep -v '^wsgiref==' | sort > $@ ;;		\
	   *)								\
	     : only pip 1.3.1+ processes --download recursively;	\
	     rm -rf $(REQS); mkdir $(REQS);				\
	     echo starting download of requirements from PyPI;		\
	     pip install --download $(REQS) -r $(REQFILE);		\
	     : trap removes partial/empty target on failure;		\
	     trap 'if [ "$$?" != 0 ]; then rm -f $@; fi' 0;		\
	     (cd $(REQS) && ls *.tar* |					\
	      sed -e 's/-\([0-9]\)/==\1/' -e 's/\.tar.*$$//') > $@;	\
	 esac; 

requirements/min-versions.txt: requirements/*.txt
	@if grep -q '>[0-9]' $^; then				\
	   echo "Use '>=' not '>' for requirements"; exit 1;	\
	 fi
	@echo "creating $@"
	@echo "# Automatically generated: DO NOT EDIT" > $@
	@echo "# Regenerate using 'make requirements'" >> $@
	@echo "# ====================================" >> $@
	@echo "# Minimum Requirements" >> $@
	@echo "# ====================================" >> $@
	@echo "#" >> $@
	@echo "# These are the minimum versions of dependencies that the developers" >> $@
	@echo "# claim will work." >> $@
	@echo "#" >> $@
	@echo "# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~" >> $@
	@echo "#" >> $@
	@echo >> $@
	@cat $^ | sed -n '/=/{s/>=/==/;s/,<.*//;s/,!=.*//;p;};/^[-#]/d;/^$$/d;/=/d;p;' >> $@

test:
	@py.test --boxed -r EfsxX

test-functional:
	@tests/cli/run_tests.sh
