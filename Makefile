# This Makefile is less a build system and more a means of making running
# some development tasks more convenient.

include .env

.PHONY: all build clean local lint reformat

PY_FILES := set_version.py wsgi.py registry/
PY_WHEEL_BASENAME := soteria_webapp

all: reformat lint build

#---------------------------------------------------------------------------

reformat:
	poetry run isort -q $(PY_FILES)
	poetry run black -q $(PY_FILES)

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
	rm -rf .mypy_cache/
	rm -rf dist/$(PY_WHEEL_BASENAME)-*.tar.gz
	rm -rf dist/$(PY_WHEEL_BASENAME)-*.whl
	-docker image rm soteria-webapp:dev

#---------------------------------------------------------------------------

local: \
		secrets/config.py \
		secrets/httpd.conf \
		secrets/oidc/id secrets/oidc/passphrase secrets/oidc/secret \
		secrets/tls.crt secrets/tls.key

	# Run `docker compose build --no-cache --pull` manually to ensure
	# that the base image and additional packages are up to date. The
	# build in this Makefile aims to be quick by using Docker's cache.

	docker compose build

	@echo ""
	@echo "Build and configuration complete."
	@echo ""
	@echo "Start your local instance of SOTERIA by running:"
	@echo ""
	@echo "    docker compose up -d"
	@echo ""
	@echo "The web application should be available at:"
	@echo ""
	@echo "    https://localhost:${SOTERIA_WEBAPP_PORT}/"
	@echo ""
	@echo "Stop and remove your local instance by running:"
	@echo ""
	@echo "    docker compose down"
	@echo ""

secrets/config.py:
	cp templates/config.py $@
	@echo
	@echo "ERROR: Please update '$@' with the SOTERIA configuration to use."
	@echo
	@exit 1

secrets/httpd.conf: \
		etc/httpd/conf.d/httpd.conf.tmpl \
		secrets/oidc/id \
		secrets/oidc/passphrase \
		secrets/oidc/secret

	# Individually bind mount each required secret because they
	# might be symlinked to somewhere outside of the build tree.

	docker run --rm \
	  -e SERVER_ADMIN=someone@example.com \
	  -e SERVER_NAME=localhost:${SOTERIA_WEBAPP_PORT} \
	  -v "$(PWD)"/etc/httpd/conf.d:/input \
	  -v "$(PWD)"/secrets:/output \
	  -v "$(PWD)"/secrets/oidc/id:/oidc/id \
	  -v "$(PWD)"/secrets/oidc/passphrase:/oidc/passphrase \
	  -v "$(PWD)"/secrets/oidc/secret:/oidc/secret \
	  hub.opensciencegrid.org/library/hairyhenderson/gomplate:alpine \
	  -d secrets=file:///oidc/ \
	  -f /input/httpd.conf.tmpl \
	  -o /output/httpd.conf

secrets/oidc/id:
	@echo
	@echo "ERROR: Please create '$@' with the OIDC Client ID to use."
	@echo
	@exit 1

secrets/oidc/passphrase:
	openssl rand -hex 32 > $@

secrets/oidc/secret:
	@echo
	@echo "ERROR: Please create '$@' with the OIDC Client Secret to use."
	@echo
	@exit 1

secrets/tls.crt secrets/tls.key:
	openssl req -x509 \
	  -subj "/CN=localhost" \
	  -newkey rsa:4096 \
	  -out secrets/tls.crt -keyout secrets/tls.key \
	  -days 365 -nodes -sha256 \
	  -extensions san -config secrets/tls.req
