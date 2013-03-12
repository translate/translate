SRC_DIR = translate
FORMATS=--formats=bztar

all:

build:
	python setup.py sdist ${FORMATS}

publish:
	python setup.py sdist ${FORMATS} upload

test-publish:
	 python setup.py sdist ${FORMATS} upload -r https://testpypi.python.org/pypi
