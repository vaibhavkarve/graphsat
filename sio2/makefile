SHELL = /bin/sh

.SUFFIXES:
.SUFFIXES: .py .sage .dat .log

.PHONY: all clean fullclean test

all :
	./make.py all 5 3 10 Mixed Uni

fullclean :
	rm -rf */*
	rmdir *

test :
	mypy *.py
	py.test
