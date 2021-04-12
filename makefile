.PHONY : test init tags

init :
	direnv allow
	python -m pip install -r requirements.txt

tags :
	etags graphsat/*.py graphsat/*.py sio2/*.py

test :
	python -m pytest

clean :
	rm -rf graphsat/__pycache__
	rm -rf graphsat/test/__pycache__
