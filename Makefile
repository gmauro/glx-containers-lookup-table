APPNAME=`cat src/APPNAME`
TARGETS=build clean dependencies deploy install uninstall
VERSION=`cat src/VERSION`

all:
	@echo "Try one of: ${TARGETS}"

build: clean dependencies
	python setup.py sdist
	python setup.py bdist_wheel --universal

clean:
	python setup.py clean --all
	find . -name '*.pyc' -delete
	rm -rf dist *.egg-info __pycache__ build

dependencies: requirements.txt
	pip install -r requirements.txt

deploy: build
	twine upload dist/*

install: build
	pip install dist/*.whl

tag:
	git tag v${VERSION}

uninstall:
	pip uninstall -y ${APPNAME}
