.PHONY: all clean

all: README.html requirements.txt

clean:
	rm -f README.html

requirements.txt: pyproject.toml
	poetry export > requirements.txt

%.html: %.rst
	poetry run rst2html.py $< $@
