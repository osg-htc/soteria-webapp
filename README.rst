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


Quickstart: Development
-----------------------

The project's dependencies are managed using Poetry_. If you are doing
significant development on the project's Python code, it might be worthwhile
to use Poetry to install the project's "dev" dependencies and tools.

.. _Poetry: https://python-poetry.org/

1. Create a virtual environment with pyenv_ and pyenv-virtualenv_::

     pyenv install 3.6.8
     pyenv virtualenv 3.6.8 harbor-user-registry
     pyenv local harbor-user-registry

2. Install the project's dependencies::

     python3 -m pip install -U pip setuptools wheel
     python3 -m pip install -U -r requirements.txt
     pyenv rehash

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
