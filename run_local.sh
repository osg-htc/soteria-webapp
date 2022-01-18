#!/bin/bash

set -eu

INSTALL_ROOT="$(cd -- "$(dirname -- "$0")" && pwd)"

export FLASK_APP="registry"
export FLASK_ENV="development"
export FLASK_DEBUG=1

cd -- "$INSTALL_ROOT" && flask run --port=8000 "$@"
