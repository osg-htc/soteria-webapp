Harbor User Registry
====================

Web application for managing the users of a Harbor_ instance

.. _Harbor: https://goharbor.io/


Overview
--------

The web application is implemented using Flask_.

<additional details to be written>

.. _Flask: https://flask.palletsprojects.com/


Configuration
-------------

The web application is configured using Python files placed in the
application's `instance folder`_. The files are sorted by name and then
loaded in that order.

.. _Instance folder: https://flask.palletsprojects.com/en/2.0.x/config/#instance-folders

See `<examples/config.py>`_ for a sample configuration that documents the
available configuration knobs. Usernames and passwords can be overriden via
environment variables, which may be helpful when running in a container.

The application can be configured for local development and testing, where
OIDC callbacks may not be possible, or where credentials for a Harbor
instance may not be available. Set ``REGISTRY_DEBUG = True``, and then copy
the following files into the instance folder, as needed:

* `<examples/mock_harbor_api.py>`_:

* `<examples/mock_user_with_orcid.py>`_:

* `<examples/mock_user_without_orcid.py>`_:

Note that this mock data contains only enough information for the web
application to function successfully.


Quickstart: Development Environment
-----------------------------------

This project uses Poetry for packaging and dependency management.

1. Install `Poetry`_.

2. Create a virtual environment using pyenv. This is more convenient than
   letting Poetry create the virtual environment, because with pyenv, there
   is no need for explicitly activating and deactivating the environment.

   a. Install `pyenv`_ and `pyenv-virtualenv`_.

   b. Create the virtual environment::

        pyenv install 3.6.8  # for EL7
        pyenv virtualenv 3.6.8 harbor-user-registry
        pyenv rehash
        pyenv local harbor-user-registry

   c. Ensure that ``pip`` and friends are up to date::

        python3 -m pip install -U pip setuptools wheel

3. Install the project's dependencies and development tools::

     poetry install --remove-untracked
     pyenv rehash
     pre-commit install

.. _Poetry: https://python-poetry.org/
.. _pyenv: https://github.com/pyenv/pyenv
.. _pyenv-virtualenv: https://github.com/pyenv/pyenv-virtualenv


Quickstart: Testing on localhost
--------------------------------

1. Create the Flask application's instance directory::

     mkdir instance

2. Copy ``examples/config.py`` to ``instance/config.py``.

3. Edit ``instance/config.py``.

4. Run the Flask application using a local development server::

     poetry run ./run.sh


Quickstart: Testing on Docker
-----------------------------

The steps below are useful mainly for testing the Docker image itself and
the configuration for httpd (sans authentication via OIDC). To configure the
web application, you can create the instance directory, as when testing on
localhost (see above), and then modify the ``Dockerfile`` to ``COPY instance
/srv/instance/`` as its last step.

1. Build the image::

     docker build -t <TAG> .

2. Run the image in a new container::

     docker run -d --rm -p 8443:8443 --name <NAME> <TAG>

3. Visit `<https://localhost:8443/>`_.

4. To debug errors, review the log files in:

   * ``/var/log/httpd/``
   * ``/srv/instance/log/``

5. Stop the container::

     docker stop <NAME>
