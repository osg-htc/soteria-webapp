# This Makefile is less a build system and more a means of making running
# some development tasks more convenient.

.PHONY: all build clean lint reformat

PY_FILES := set_version.py wsgi.py registry/
PY_WHEEL_BASENAME := soteria_webapp

all: reformat lint build

#---------------------------------------------------------------------------

reformat:
	poetry run isort $(PY_FILES)
	poetry run black $(PY_FILES)

lint:
	-poetry run bandit -qr $(PY_FILES)
	-poetry run mypy $(PY_FILES)
	-poetry run pylint $(PY_FILES)

requirements.txt: poetry.lock
	poetry export > requirements.txt

#---------------------------------------------------------------------------

build:
	poetry build

clean:
	rm -rf .mypy/ .pylint/
	rm -rf dist/$(PY_WHEEL_BASENAME)-*.tar.gz
	rm -rf dist/$(PY_WHEEL_BASENAME)-*.whl
