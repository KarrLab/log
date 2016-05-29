# shortcuts. because i'm lazy. you should be too.

build:
	rm -r .env
	virtualenv -p python3 .env
	. .env/bin/activate
	pip install -e .


build-dev: build
	pip install -e "file://$(shell pwd)#egg=log[dev]"


test: build-dev
	flake8
	py.test --cov log --cov-report term-missing tests


push-feature: test
	git push origin $(shell git rev-parse --abbrev-ref HEAD)


distribute: test
	python setup.py sdist upload
