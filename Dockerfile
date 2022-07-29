FROM hub.opensciencegrid.org/opensciencegrid/software-base:3.6-el8-release


## Build arguments for embedding a version string within the image.


ARG GITHUB_REF
ENV GITHUB_REF="${GITHUB_REF:-}"

ARG GITHUB_SHA
ENV GITHUB_SHA="${GITHUB_SHA:-}"


## Set the Python version.


ARG PY_PKG=python39
ARG PY_EXE=python3.9


## Locale and Python settings required by Flask.


ENV LANG="en_US.utf8"
ENV LC_ALL="en_US.utf8"
ENV PYTHONUNBUFFERED=1


## Install core dependencies and configuration.


RUN yum module enable -y mod_auth_openidc ${PY_PKG} \
    && yum update -y \
    && yum install -y httpd mod_auth_openidc mod_ssl ${PY_PKG}-pip ${PY_PKG}-mod_wsgi \
    && yum clean all \
    && rm -rf /etc/httpd/conf.d/* /var/cache/yum/ \
    #
    && ${PY_EXE} -m pip install --no-cache-dir -U pip setuptools wheel

COPY etc /etc/


## Install the Flask and WSGI applications.


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
