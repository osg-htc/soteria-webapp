FROM opensciencegrid/software-base:release


## Build arguments for embedding a version string within the image.


ARG GITHUB_REF
ENV GITHUB_REF="${GITHUB_REF:-}"

ARG GITHUB_SHA
ENV GITHUB_SHA="${GITHUB_SHA:-}"


## Locale and Python settings required by Flask.


ENV LANG="en_US.utf8"
ENV LC_ALL="en_US.utf8"
ENV PYTHONUNBUFFERED=1


## Install core dependencies and configuration.


RUN yum update -y \
    && yum install -y httpd mod_auth_openidc mod_ssl python3-pip python3-mod_wsgi \
    && yum clean all \
    && rm -rf /etc/httpd/conf.d/* /var/cache/yum/ \
    #
    && python3 -m pip install --no-cache-dir -U pip setuptools wheel

COPY etc /etc/


## Install the Flask and WSGI applications.


COPY poetry.lock pyproject.toml requirements.txt /srv/
RUN python3 -m pip install --no-cache-dir -r /srv/requirements.txt

COPY set_version.py wsgi.py /srv/
COPY registry /srv/registry/

RUN (cd /srv/ && env FLASK_APP="registry" python3 -m flask assets build) \
    #
    && find /srv/ -name ".*" -exec rm -rf {} \; -prune \
    #
    && rm -rf /srv/instance/* \
    && chown apache:apache /srv/instance/ \
    && python3 /srv/set_version.py
