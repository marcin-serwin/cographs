all: check

check:
	find . -type f -not -path '*/\.*' -name "*.py" | xargs pylint --indent-string='    ' --disable=missing-docstring,duplicate-code,fixme --max-line-length=79
