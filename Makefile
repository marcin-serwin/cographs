all: check

check:
	find . -type f -name "*.py" | xargs pylint --indent-string='  ' --variable-naming-style=any --argument-naming-style=any --class-attribute-naming-style=any --disable=missing-docstring,too-many-arguments,duplicate-code,fixme,arguments-out-of-order --max-line-length=80
