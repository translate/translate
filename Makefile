SRC_DIR = translate
DOCS_DIR = docs
FORMATS=--formats=bztar
VERSION=$(shell python setup.py --version)
FULLNAME=$(shell python setup.py --fullname)
SFUSERNAME=$(shell egrep -A5 sourceforge ~/.ssh/config | egrep -m1 User | cut -d" " -f2)

.PHONY: all build docs requirements help publish sort-imports test-publish

all: help

build: docs
	python setup.py sdist ${FORMATS}

docs:
	# The following creates the HTML docs.
	# NOTE: cd and make must be in the same line.
	cd ${DOCS_DIR}; make SPHINXOPTS="-W -q" html ${TAIL}

publish-pypi:
	python setup.py sdist ${FORMATS} upload

sort-imports:
	isort -rc .

test-publish-pypi:
	 python setup.py sdist ${FORMATS} upload -r https://testpypi.python.org/pypi

#scp translate-toolkit-1.10.0.tar.bz2 jsmith@frs.sourceforge.net:/home/frs/project/translate/Translate\ Toolkit/1.10.0/
publish-sourceforge:
	@echo "We don't trust automation that much.  The following is the command you need to run"
	@echo 'scp -p dist/${FULLNAME}.tar.bz2 ${SFUSERNAME}@frs.sourceforge.net:"/home/frs/project/translate/Translate\ Toolkit/${VERSION}/"'
	@echo 'scp -p docs/releases/${VERSION}.rst ${SFUSERNAME}@frs.sourceforge.net:"/home/frs/project/translate/Translate\ Toolkit/${VERSION}/README.rst"'

publish: publish-pypi publish-sourceforge

help:
	@echo "Help"
	@echo "----"
	@echo
	@echo "  build - create sdist with required prep"
	@echo "  requirements - (re)generate pinned and minimum requirements"
	@echo "  sort-imports - sort Python imports"
	@echo "  publish-pypi - publish on PyPI"
	@echo "  test-publish-pypi - publish on PyPI testing platform"
	@echo "  publish-sourceforge - publish on sourceforge"
	@echo "  publish - publish on PyPI and sourceforge"
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
