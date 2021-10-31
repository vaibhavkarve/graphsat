# Select your python binary.
PY = python3.8

.PHONY : test dev-tests install tags clean

# Run `make install` for installing graphsat and all its requirements.
install :
	@echo Installing direnv and hooking it to bash
	curl -sfL https://direnv.net/install.sh | bash
	direnv hook bash

	@echo Allowing direnv to pick correct python version
	direnv allow

	@echo Installing packages listed in requirements.txt
	$(PY) -m pip install -r requirements.txt

# Run `make tags` for creating etags for the files. Used for
# Emacs-navigation.
tags :
	etags graphsat/*.py graphsat/*.py sio2/*.py

# Run `make test` for running all unit tests
test :
	$(PY) -m pytest tests

# Run `make dev-tests` only if there are changes made to graphsat's source
# code. This has been tested against config files `mypy.ini` and
# `pytest.ini` -- files that are not part of this package release. Please
# contact the authors for a copy of our local mypy.ini and pytest.ini
# config files.
dev-tests :
	$(PY) -m pytest tests


# Run `make clean` to remove superfluous files.
clean :
	rm -rf graphsat/__pycache__
	rm -rf graphsat/test/__pycache__
	rm -rf .direnv
