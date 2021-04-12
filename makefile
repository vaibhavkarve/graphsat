.PHONY : test dev-tests install tags clean

# Run `make install` for installing graphsat and all its requirements.
install :
	@echo Installing direnv and hooking it to bash
	curl -sfL https://direnv.net/install.sh | bash
	direnv hook bash

	@echo Allowing direnv to pick correct python version
	direnv allow

	@echo Installing packages listed in requirements.txt
	python -m pip install -r requirements.txt

tags :
	etags graphsat/*.py graphsat/*.py sio2/*.py

test :
	python -m pytest

clean :
	rm -rf graphsat/__pycache__
	rm -rf graphsat/test/__pycache__
