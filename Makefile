all: check

check: lint type-check

lint:
	find src -type f -name "*.py" | xargs pylint

type-check:
	npx pyright 
