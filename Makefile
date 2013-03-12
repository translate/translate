SRC_DIR = translate
FORMATS=--formats=bztar

.PHONY: all build publish test-publish

all: help

build:
	python setup.py sdist ${FORMATS}

publish:
	python setup.py sdist ${FORMATS} upload

test-publish:
	 python setup.py sdist ${FORMATS} upload -r https://testpypi.python.org/pypi

help:
	@echo "Help"
	@echo "----"
	@echo
	@echo "  build - create sdist with required prep"
	@echo "  publish - publish on PyPI"
	@echo "  test-publish - publish on PyPI testing platform"
