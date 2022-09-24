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
	# Check poetry installation and pyproject.toml is healthy.
	poetry check
	# Print environment being used by poetry.
	poetry env info
	# Make sure you are using Python >= 3.10

# Install all pip requirements for "graphsat" project.
install: check-py
	poetry install
	poetry run nbstripout --install
	# Consider running "just test" for testing the project.

# Update dependendencies (for package devs only).
update:
	poetry self update
	poetry update
	poetry run safety check

# Lint and check the codebase for style.
lint:
	poetry run autoflake --in-place --recursive --expand-star-imports --remove-all-unused-imports graphsat/* tests/*
	poetry run isort graphsat/ tests/
	poetry run pylint -vvv graphsat/ tests/
	poetry run pycodestyle graphsat/ tests/
	poetry run pydocstyle graphsat/ tests/
	poetry run interrogate -v --fail-under 82 graphsat/

# Typecheck the code using mypy.
typecheck files = "./stubs/ graphsat/ tests/":
	poetry run mypy {{files}}
	# poetry run nbqa mypy benchmarking/
	# Consider running "just lint" for linting the code.

# Run all the tests.
test flags = "--cov-report term-missing --cov=graphsat --cov-fail-under=62 --workers auto":
	# Helpful command for debugging: just test "-x --ff -v -s --pdb"
	poetry run pytest {{flags}}
	# To test Jupyter notebooks, uncomment the following:
	# poetry run pytest --nbmake --nbmake-timeout=30 benchmarking/*.ipynb
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


ORG_FILES := "benchmarking.org"
TEX_FILES := "benchmarking.tex"
PY_FILES := ""

# Convert org file to tex file using emacs script `lisp_code.el`
org2tex:
	cd benchmarking && emacs -l lisp_code.el --batch {{ORG_FILES}} -f org-latex-export-to-latex --kill


# Convert tex file to pdf file using latexmk.
tex2pdf:
	cd benchmarking && latexmk -pdflatex=lualatex -pdf -shell-escape {{TEX_FILES}}


# Convert org file to python and compare with direct-python copy.
org2py:
	emacs --batch {{ORG_FILES}} -f org-babel-tangle --kill
	git diff {{ORG_FILES}} {{PY_FILES}}
