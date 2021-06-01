Harbor User Registry
====================

Web application for managing the users of a Harbor_ instance

.. _Harbor: https://goharbor.io/


Overview
--------

<to be written>


Configuration
-------------

<to be written>


Quickstart: Development
-----------------------

<to be written>


Quickstart: Testing
-------------------

1. Build the image::

     docker build -t <TAG> .

2. Run the image in a new container::

     docker run -d --rm -p 8443:8443 --name <NAME> <TAG>

3. Visit `<https://localhost:8443/>`_.

4. Stop the container::

     docker stop <NAME>


Quickstart: Debugging
---------------------

Review the log files in:

* ``/var/log/httpd/``
* ``/srv/instance/log/``
