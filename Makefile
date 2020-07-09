all: check

check: lint type-check

lint:
	find cographs -type f -name "*.py" | xargs pylint

type-check:
	npx pyright 
