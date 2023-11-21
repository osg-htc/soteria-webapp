FROM almalinux:9

# Reference: https://github.com/hadolint/hadolint/wiki/DL4006

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Configure the build.

ARG GITHUB_REF
ARG GITHUB_SHA
ARG PY_EXE=python3.9
ARG PY_PKG=python3

# Configure the environment.

ENV GITHUB_REF=${GITHUB_REF}
ENV GITHUB_SHA=${GITHUB_SHA}
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8
ENV PYTHONUNBUFFERED=1

# Install essential packages and utilities.

USER root
WORKDIR /tmp
RUN true \
    && dnf install -y \
        dnf-plugins-core \
        epel-release \
    && dnf config-manager --set-enabled crb \
    && dnf update -y \
    && dnf install -y --allowerasing \
        ca-certificates \
        curl \
        glibc-langpack-en \
        httpd \
        mod_auth_openidc \
        mod_ssl \
        procps \
        ${PY_PKG}-pip \
        ${PY_PKG}-mod_wsgi \
        supervisor \
    && dnf install -y \
        https://research.cs.wisc.edu/htcondor/repo/current/htcondor-release-current.el9.noarch.rpm \
    && dnf install -y \
        condor \
    && dnf clean all \
    && rm -rf /etc/httpd/conf.d/* /var/cache/dnf/* \
    #
    && ${PY_EXE} -m pip install -U --no-cache-dir pip setuptools wheel \
    && true

COPY etc /etc/

# Install the application.

COPY poetry.lock pyproject.toml requirements.txt /srv/
RUN ${PY_EXE} -m pip install --ignore-installed --no-cache-dir -r /srv/requirements.txt

COPY registry /srv/registry/
COPY set_version.py wsgi.py /srv/

RUN (cd /srv/ && env FLASK_APP="registry" ${PY_EXE} -m flask assets build) \
    #
    && find /srv/ -name ".*" -exec rm -rf {} \; -prune \
    #
    && rm -rf /srv/instance/* \
    && chown apache:apache /srv/instance/ \
    && ${PY_EXE} /srv/set_version.py

# Configure container startup.

WORKDIR /srv
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf", "-n"]
