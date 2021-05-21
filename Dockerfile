ARG IMAGE_BASE_TAG=release

FROM opensciencegrid/software-base:$IMAGE_BASE_TAG

LABEL maintainer OSG Software <support@opensciencegrid.org>

RUN yum update -y \
    && yum install -y httpd mod_auth_openidc mod_ssl python3-pip python3-mod_wsgi \
    && yum clean all \
    && rm -rf /var/cache/yum

COPY poetry.lock requirements.txt /srv/
RUN pip3 install -r /srv/requirements.txt

COPY etc/supervisord.d/* /etc/supervisord.d/
COPY wsgi.py /srv/
COPY registry /srv/registry/

ENV LANG="en_US.utf8"
ENV LC_ALL="en_US.utf8"
ENV PYTHONUNBUFFERED=1
