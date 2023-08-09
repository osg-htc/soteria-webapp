FROM almalinux:9

# Build arguments for embedding a version string within the image.

ARG GITHUB_REF
ENV GITHUB_REF="${GITHUB_REF:-}"

ARG GITHUB_SHA
ENV GITHUB_SHA="${GITHUB_SHA:-}"

# Set the Python version.

ARG PY_PKG=python3
ARG PY_EXE=python3.9

# Locale and Python settings required by Flask.

ENV LANG="en_US.utf8"
ENV LC_ALL="en_US.utf8"
ENV PYTHONUNBUFFERED=1

# Reference: https://github.com/hadolint/hadolint/wiki/DL4006

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install core dependencies and configuration.

RUN dnf install -y epel-release \
    && dnf update -y \
    && dnf install -y \
        glibc-langpack-en \
        httpd \
        mod_auth_openidc \
        mod_ssl \
        procps \
        ${PY_PKG}-pip \
        ${PY_PKG}-mod_wsgi \
        supervisor \
    && dnf clean all \
    && rm -rf /etc/httpd/conf.d/* /var/cache/dnf/

COPY etc /etc/

# Install the Flask and WSGI applications.

COPY poetry.lock pyproject.toml requirements.txt /srv/
RUN ${PY_EXE} -m pip install --no-cache-dir -r /srv/requirements.txt

COPY registry /srv/registry/
COPY set_version.py wsgi.py /srv/

RUN (cd /srv/ && env FLASK_APP="registry" ${PY_EXE} -m flask assets build) \
    #
    && find /srv/ -name ".*" -exec rm -rf {} \; -prune \
    #
    && rm -rf /srv/instance/* \
    && chown apache:apache /srv/instance/ \
    && ${PY_EXE} /srv/set_version.py

# Everything runs under Supervisor.

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf", "-n"]
