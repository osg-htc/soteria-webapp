SOTERIA Web Application
=======================

Web application for managing the users of a Harbor_ instance

.. _Harbor: https://goharbor.io/


Overview
--------

The web application is implemented using Flask_.

.. _Flask: https://flask.palletsprojects.com/


Configuration
-------------

The web application is configured using Python files placed in the
application's `instance folder`_. The files are sorted by name and then
loaded in that order.

.. _Instance folder: https://flask.palletsprojects.com/en/2.1.x/config/#instance-folders

See `<templates/config.py>`_ for a sample configuration that documents the
available configuration knobs. Usernames and passwords can be overridden via
environment variables, which may be helpful when running in a container.


Quickstart: Development Environment
-----------------------------------

The steps below are but one way to set up a development environment.
Anything that results in a Python 3.9 environment with the dependencies
listed in `<pyproject.toml>`_ installed should work.

1. Install `Poetry`_. It is used by this project for packaging and managing
   dependencies.

2. Create a virtual environment using `pyenv`_. With pyenv, there is no need
   to explicitly activate and deactivate the virtual environment.

   a. Install `pyenv`_ and `pyenv-virtualenv`_.

   b. Create the virtual environment::

        pyenv install 3.9.7  # for EL8
        pyenv virtualenv 3.9.7 soteria-webapp
        pyenv rehash

        cd <location of your clone of this repository>
        pyenv local soteria-webapp

   c. Ensure that ``pip`` and friends are up to date::

        python3 -m pip install -U pip setuptools wheel

3. Install this project's dependencies and development tools::

     poetry install --remove-untracked
     pyenv rehash
     pre-commit install

.. _Poetry: https://python-poetry.org/
.. _pyenv: https://github.com/pyenv/pyenv
.. _pyenv-virtualenv: https://github.com/pyenv/pyenv-virtualenv


Quickstart: Testing on localhost
--------------------------------

Prerequisites:

- A CILogon OIDC Client ID and Secret
- A Docker installation

Steps:

1. Build and configure a local instance of SOTERIA::

     make local

   This command reports missing configuration files one by one, so you will
   need to run it several times until it completes successfully. It does not
   check whether the configuration files contain "valid" values.

   - ``secrets/config.py``: The `<Makefile>`_ creates this file based on
     a `template <templates/config.py>`_. Replace the placeholder values
     from the template as needed.

   - ``secrets/oidc/id``: This file should contain the CILogon OIDC Client
     ID to use. The OIDC client must be configured to allow
     ``https://localhost:9801/callback`` as a callback URL. (If you update
     the default port specified in `<.env>`_, update the port number in the
     callback URL to match.)

   - ``secrets/oidc/passphrase``: This file should contain the CILogon OIDC
     Client Secret for the above Client ID.

2. When the previous step completes without errors, the final output will
   end with instructions for starting and stopping the local instance.
