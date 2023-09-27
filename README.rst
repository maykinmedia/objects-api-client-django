

Objects API Client (for Django)
==============================

:Version: 0.1.0
:Source: https://github.com/maykinmedia/objects-api-client-django
:Keywords: Objects API, Client, Django
:PythonVersion: 3.9

|build-status|

|python-versions| |django-versions| |pypi-version|

About
=====

Easily integrate `Objects API`_ in your Django application. 

Installation
============

Requirements
------------

* Python 3.9 or newer
* Django 3.2 or newer


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


Licence
=======

Copyright © `Maykin Media B.V.`_, 2023

Licensed under the `MIT`_.

.. _`Maykin Media B.V.`: https://www.maykinmedia.nl
.. _`MIT`: LICENSE
.. _`Objects API`: https://github.com/maykinmedia/objects-api

.. |build-status| image:: https://github.com/maykinmedia/objects-api-client-django/workflows/Run%20CI/badge.svg
    :alt: Build status
    :target: https://github.com/maykinmedia/objects-api-client-django/actions?query=workflow%3A%22Run+CI%22
