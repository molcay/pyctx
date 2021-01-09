.PHONY: clean-pyc clean-build
clean-pyc:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +
	name '*~' -exec rm --force  {}
clean-build:
	rm --force --recursive build/
	rm --force --recursive dist/
	rm --force --recursive *.egg-info

init:
	pip install poetry --upgrade
	poetry install --dev

test:
	poetry run coverage run --source pyctx -m unittest discover
	poetry run coverage report -m

build:
	make test
	pip install 'twine>=1.5.0'
	python setup.py sdist bdist_wheel

publish:
	make build
	twine upload dist/*
	rm -fr build dist .egg pyctx.egg-info
