#!/bin/bash

set -eu

INSTALL_ROOT="$(cd -- "$(dirname -- "$0")" && pwd)"

export FLASK_APP="registry"
export FLASK_ENV="development"

cd -- "$INSTALL_ROOT" && flask run "$@"
