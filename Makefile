all: check

check: lint type-check

lint:
	find . -type f -not -path '*/\.*' -name "*.py" | xargs pylint

type-check:
	npx pyright 
