.PHONY: all tests clean weave

COVERAGE_RCFILE = /home/vaibhav/.coveragerc

all : weave tangle test

weave : cnf.tex cnf.pdf

cnf.pdf : cnf.tex
	lualatex -shell-escape $<
	lualatex -shell-escape $<
	lualatex -shell-escape $<

test : cnf.py tests/test_cnf.py
	python -m mypy cnf.py
	python -m pylint cnf.py
	coverage run --rcfile=$(COVERAGE_RCFILE) -m pytest ../tests/
	coverage report --rcfile=$(COVERAGE_RCFILE)

clean :
	rm -rf cnf.pdf _minted-cnf auto cnf.toc cnf.log cnf.aux cnf.out
