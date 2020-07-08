all: check

check: lint type-check

lint:
	find . -type f -not -path '*/\.*' -name "*.py" | xargs pylint --indent-string='    ' --disable=missing-docstring,duplicate-code,fixme --max-line-length=79 ;

type-check:
	npx pyright 
