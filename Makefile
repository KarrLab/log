# shortcuts. because i'm lazy. you should be too.

build:
	virtualenv -p python3 .env
	. .env/bin/activate
	pip install -e .
	pip install -e "file://$(shell pwd)#egg=log[dev]"
	pip install -e "file://$(shell pwd)#egg=log[arrow]"


test: build
	flake8
	py.test --cov log --cov-report term-missing tests


distribute: test
	python setup.py sdist upload
