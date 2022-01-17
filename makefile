#!/usr/bin/make -f
# This is a GNU Makefile intended to be run from the command line.
# We group targets into the following section --
# 1. Targets for regular user.
# 2. Targets for developers of graphsat.


#######################################################################
#################### 1. Targets for regular user ######################
#######################################################################

## We start by defining some constants that can be modified by the user
PYRUN       = python -m
TEST_FOLDER = tests/


.PHONY: all
all: list

# Select your python binary.
PY = python3.8

.PHONY : test dev-tests install tags clean

# Run `make install` for installing graphsat and all its requirements.
.PHONY: install install-direnv install-pip-packages

.direnv: install
install: install-direnv install-pip-packages

install-direnv:
	@echo Installing direnv and hooking it to bash
	curl -sfL https://direnv.net/install.sh | bash
	direnv hook bash

	@echo Allowing direnv to pick correct python version
	direnv allow

install-pip-packages:
	@echo Installing packages listed in requirements.txt
	$(PYRUN) pip install -r requirements.txt
	$(PY) -m pip install -r requirements.txt


# Run `make test` for running all unit tests
.PHONY: test
test:
	$(PYRUN) pytest $(TEST_FOLDER)


# Run `make clean` to remove superfluous files. Can be run as often as
# needed.
.PHONY: clean distclean
clean:
	rm -rf **/__pycache__

# Run `make distclean` to remove all superfluous files as well as all
# installed packages. Run `make install` after running `make distclean`
distclean: clean
	rm -rf .direnv


#### 2. Targets for developers of graphsat ####

## We start by defining some constants that can be modified by the developer
COVERAGE_RC_FILE = .coveragerc
COVERAGE_RC_FLAG = --rcfile=$(COVERAGE_RC_FILE)

test :
	$(PY) -m pytest tests

# Run `make dev-tests` only if there are changes made to graphsat's source
# code. This has been tested against config files `mypy.ini` and
# `pytest.ini` -- files that are not part of this package release. Please
# contact the authors for a copy of our local mypy.ini and pytest.ini
# config files.
.PHONY: dev-tests test-mypy test-pylint test-coverage
dev-tests: test-mypy test-pylint test-coverage
dev-tests :
	$(PY) -m pytest tests

test-mypy:
	$(PYRUN) mypy -p graphsat

test-pylint:
	$(PYRUN) pylint graphsat

test-coverage:
	coverage run $(COVERAGE_RC_FLAG) -m pytest $(TEST_FOLDER)
	coverage report $(COVERAGE_RC_FLAG)


# Run `make tags` for creating etags for the files. Used for Emacs
# navigation.
tags:
	etags graphsat/*.py sio2/*.py

tangle: graphsat/cnf.py

weave: literate_docs/cnf.pdf

literate_docs/cnf.pdf: literate_docs/cnf.tex
	latexmk -pdflatex=lualatex -pdf -shell-escape $<

literate_docs/cnf.tex: literate_docs/cnf.org
	emacs -l lisp_code.el --batch $< -f org-latex-export-to-latex --kill


$(READY_FILES): literate_docs/cnf.org
	emacs --batch $< -f org-babel-tangle --kill
	cp literate_docs/*.py literate_docs/tests/*.py graphsat/
	black $(READY_FILES)
	chmod +x $(READY_FILES)

list:
	@grep "^.*:.*" makefile | grep -v ".PHONY"
# Run `make clean` to remove superfluous files.
clean :
	rm -rf graphsat/__pycache__
	rm -rf graphsat/test/__pycache__
	rm -rf .direnv

# Lint the entire project
lintall :
	isort graphsat/
	isort tests/
