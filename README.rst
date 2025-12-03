

Objects API Client (for Django)
===============================

:Version: 0.4.1
:Source: https://github.com/maykinmedia/objects-api-client-django
:Keywords: Objects API, Client, Django
:PythonVersion: 3.11

|build-status| |python-versions| |django-versions| |pypi-version|

About
=====

Easily integrate `Objects API`_ in your Django application. 

Installation
============

Requirements
------------

* Python 3.11 or newer
* Django 4.2 or newer


Install
-------

You can the install Objects API Client either via the Python Package Index (PyPI) or 
from source.

To install using ``pip``:

.. code-block:: bash

    pip install objects-api-client-django


Usage
=====

To use this with your project you need to follow these steps:

#. Add ``objectsapiclient`` to ``INSTALLED_APPS`` in your Django project's 
   ``settings.py``:

   .. code-block:: python

      INSTALLED_APPS = (
          # ...,
          "objectsapiclient",
      )


#. Configure your Objects API connection and settings in the admin, under 
   **Objects API client configuration**.

#. Done.


Development
===========

Install dependencies for development:

.. code-block:: bash

   pip install -e .[tests,release]

Running tests:

.. code-block:: bash

   # Run all tests
   pytest tests/

   # Run all checks (tests for all Python/Django combinations + linting)
   tox

Linting and formatting:

.. code-block:: bash

   # Check code quality
   ruff check .

   # Auto-fix issues
   ruff check --fix .

   # Format code
   ruff format .

   # Run via tox
   tox -e ruff

Licence
=======

Copyright © `Maykin Media B.V.`_, 2025

Licensed under the `MIT`_.

.. _`Maykin Media B.V.`: https://www.maykinmedia.nl
.. _`MIT`: LICENSE
.. _`Objects API`: https://github.com/maykinmedia/objects-api

.. |build-status| image:: https://github.com/maykinmedia/objects-api-client-django/workflows/Run%20CI/badge.svg
    :alt: Build status
    :target: https://github.com/maykinmedia/objects-api-client-django/actions?query=workflow%3A%22Run+CI%22

.. |python-versions| image:: https://img.shields.io/pypi/pyversions/objects-api-client-django.svg
    :alt: Supported Python versions
    :target: https://pypi.org/project/objects-api-client-django/

.. |django-versions| image:: https://img.shields.io/pypi/djversions/objects-api-client-django.svg
    :alt: Supported Django versions
    :target: https://pypi.org/project/objects-api-client-django/

.. |pypi-version| image:: https://img.shields.io/pypi/v/objects-api-client-django.svg
    :alt: Latest version on PyPI
    :target: https://pypi.org/project/objects-api-client-django/
