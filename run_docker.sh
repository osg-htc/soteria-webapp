#!/bin/bash

set -eu

INSTALL_ROOT="$(cd -- "$(dirname -- "$0")" && pwd)"

CONTAINER="soteria-webapp"
IMAGE="$(whoami)/soteria-webapp:testing"
VOLUMES=()


# Identify configuration files that should be bind mounted. We cannot bind
# mount the entire instance directory because then it would become writable
# only by ``root``.


for f in "$INSTALL_ROOT"/instance/*.py; do
  VOLUMES+=(-v "$f":/srv/instance/"$(basename -- "$f")")
done


docker build --pull -t "$IMAGE" "$INSTALL_ROOT"
docker run -d --name "$CONTAINER" -p 8443:8443 "${VOLUMES[@]}" "$IMAGE"


printf '%s\n' ""
printf '%s\n' "Now running as '$CONTAINER'. To stop the container:"
printf '%s\n' ""
printf '%s\n' "    docker stop $CONTAINER"
printf '%s\n' "    docker commit $CONTAINER <new image>  # for debugging"
printf '%s\n' "    docker rm $CONTAINER"
