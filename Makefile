all: check test

check: lint type-check

lint:
	find cographs -type f -name "*.py" | xargs pylint

type-check:
	npx pyright 

test: test-small

test-small:
	python3 -m unittest cographs/test/*.py