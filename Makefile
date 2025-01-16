.PHONY: clean-pyc clean-build

clean-pyc:
	find ./src ./tests ./examples -name '*.pyc' -exec rm -rf {} +
	find ./src ./tests ./examples -name '*.pyo' -exec rm -rf {} +

clean-build:
	rm -rf dist/

init:
	uv install

test:
	uv run coverage run -m unittest discover
	uv run coverage report -m

check:
	uv run ruff check

build:
	make test
	uv build

publish:
	make build
	uv publish
	rm -rf dist
