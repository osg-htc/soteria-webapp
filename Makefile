.PHONY: all check format

PY_FILES := set_version.py wsgi.py registry/

all: format check

check:
	-poetry run bandit -qr $(PY_FILES)
	-poetry run mypy $(PY_FILES)
	-poetry run pytype -j auto -k $(PY_FILES)
	-poetry run pylint $(PY_FILES)

format:
	poetry run isort $(PY_FILES)
	poetry run black $(PY_FILES)

requirements.txt: poetry.lock
	poetry export > requirements.txt
