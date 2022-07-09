#!/usr/bin/env just --justfile

# We use this justfile to organize frequently-run commands and recipes
# in one place.

# To use this justfile, you must install "just" from
# [[https://github.com/casey/just]]. After that, run the "just"
# command from a terminal or command prompt to see a list of available recipes.


# Use bash to execute backticked lines.
set shell := ["bash", "-uc"]

# (Default) list all the just recipes.
list:
	@just --list


# Check version of python.
check-py:
	python --version
	which python
	python -m pip --version
	@echo VIRTUAL_ENV = {{env_var('VIRTUAL_ENV')}}
	# Make sure you are using Python >= 3.10

# Install all pip requirements for "graphsat" project.
install: check-py
	python -m pip install --upgrade pip
	python -m pip install --upgrade --editable .[dev]
	-just typecheck > /tmp/mypy_output.txt
	python -m mypy --install-types
	python -m safety check
	# Consider running "just test" for testing the project.

# Lint and check the codebase for style.
lint:
	python -m autoflake --in-place --recursive --expand-star-imports --remove-all-unused-imports graphsat/* tests/*
	python -m isort graphsat/ tests/
	python -m pylint graphsat/ tests/
	python -m pycodestyle graphsat/ tests/
	python -m pydocstyle graphsat/ tests/

# Typecheck the code using mypy.
typecheck files = "":
	-python -m mypy ./stubs/ graphsat/ {{files}}
	# Consider running "just lint" for linting the code.

# Run all the tests.
test flags = "--cov-report term-missing --cov=graphsat --workers auto":
	# Helpful command for debugging: just test "-x --ff -v -s --pdb"
	python -m pytest {{flags}}
	# Consider running "just typecheck" for statically checking types.

# Run the "if __name__ == "__main__" block of all the scripts.
mains:
	python -m graphsat.cnf
	python -m graphsat.graph
	python -m graphsat.mhgraph
	python -m graphsat.sat


# Remove cache files.
clean:
	rm -rf **/__pycache__
	rm -rf graphsat/__pycache__
	rm -rf graphsat/test/__pycache__


# Create etags for Emacs navigation.
tags:
	etags graphsat/*.py


ORG_FILES := "literate_docs/cnf.org"
TEX_FILES := "literate_docs/cnf.tex"
PY_FILES := "literate_docs/cnf.py"

# Convert org file to tex file using emacs script `lisp_code.el`
org2tex:
	emacs -l lisp_code.el --batch {{ORG_FILES}} -f org-latex-export-to-latex --kill


# Convert tex file to pdf file using latexmk.
tex2pdf:
	latexmk -pdflatex=lualatex -pdf -shell-escape {{TEX_FILES}}


# Convert org file to python and compare with direct-python copy.
org2py:
	emacs --batch {{ORG_FILES}} -f org-babel-tangle --kill
	git diff {{ORG_FILES}} {{PY_FILES}}
