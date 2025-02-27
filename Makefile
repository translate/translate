DOCS_DIR = docs

.PHONY: all docs help test test-functional

all: help

docs:
	# The following creates the HTML docs.
	make -C ${DOCS_DIR} SPHINXOPTS="--show-traceback --fail-on-warning --jobs auto" html ${TAIL}

docs-review: docs
	python -mwebbrowser file://$(shell pwd)/${DOCS_DIR}/_build/html/index.html

help:
	@echo "Help"
	@echo "----"
	@echo
	@echo "  docs - build Sphinx docs"
	@echo "  docs-review - launch webbrowser to review docs"
	@echo "  test - run unit test suite"
	@echo "  test-functional - run the functional test suite"

test:
	@uv run pytest --cov=. -r EfsxX

test-functional:
	@tests/cli/run_tests.sh
