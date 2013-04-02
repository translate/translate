SRC_DIR = translate
FORMATS=--formats=bztar
VERSION=$(shell python setup.py --version)
FULLNAME=$(shell python setup.py --fullname)

.PHONY: all build publish test-publish

all: help

build:
	python setup.py sdist ${FORMATS}

publish-pypi:
	python setup.py sdist ${FORMATS} upload

test-publish-pypi:
	 python setup.py sdist ${FORMATS} upload -r https://testpypi.python.org/pypi

#scp translate-toolkit-1.10.0.tar.bz2 jsmith@frs.sourceforge.net:/home/frs/project/translate/Translate\ Toolkit/1.10.0/
publish-sourceforge:
	@echo "We don't trust automation that much.  The following is the command you need to run"
	@echo 'scp -p ${FULLNAME}.tar.bz2 jsmith@frs.sourceforge.net:"/home/frs/project/translate/Translate\ Toolkit/${VERSION}/"'
	@echo 'scp -p release/RELEASE-NOTES-${VERSION}.rst jsmith@frs.sourceforge.net:"/home/frs/project/translate/Translate\ Toolkit/${VERSION}/README.rst"'

publish: publish-pypi publish-sourceforge

help:
	@echo "Help"
	@echo "----"
	@echo
	@echo "  build - create sdist with required prep"
	@echo "  publish-pypi - publish on PyPI"
	@echo "  test-publish-pypi - publish on PyPI testing platform"
	@echo "  publish-sourceforge - publish on sourceforge"
	@echo "  publish - publish on PyPI and sourceforge"
