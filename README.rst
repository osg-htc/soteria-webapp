Harbor User Registry
====================

Web application for managing the users of a Harbor_ instance

.. _Harbor: https://goharbor.io/


Overview
--------

<to be written>


Configuration
-------------

See `<examples/config.py>`_.

<additional details to be written>


Quickstart: Development
-----------------------

1. Install `Poetry <https://python-poetry.org/>`_.

2. Install dependencies::

     poetry install


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

The steps below are useful mainly for testing the Docker image itself. To
configure the web application, you can create the instance directory, as
when testing on localhost (see above), and then modify the ``Dockerfile`` to
``COPY instance /srv/instance/`` as its last step.

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
