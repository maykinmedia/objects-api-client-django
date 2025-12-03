=========
Changelog
=========


[0.4.1 (2025-12-03)]
====================

* Added CI check to publishing workflow to ensure the changelog is ready for
  release (must contain new version and release date)
* Added missing migration to rename related fields on ObjectsClientConfiguration


0.4.0 (2025-12-03)
==================

* Added ruff (replaces flake8, black, isort)
* Added bump-my-version (replaces bumpversion)
* Fixed version mismatch due to stale info in README
* Updated README with instructions for developers
* Removed unused docs section from pyproject.toml


0.3.0
=====

*November 25, 2025*

* Added lazy model field to prevent errors from HTTP requests during startup
* Dropped support for Python 3.9/3.10 and Django 3.2; added support for
  Python 3.11/3.12/3.13 and Django 4.2
* Added missing metadata (long_description_content_type) to setup.cfg and
  fixed syntax error in README that preventted PyPi publishing


0.2.3
=====

*November 22, 2022*

* Fixed startup errors due to no configuration present.
* Added more gotcha's to the README.

0.2.2
=====

*October 3, 2022*

* Fixed length of slugfield (default is now 100 instead of 50) which matches
  the slug length in Open Forms.


0.2.1
=====

*September 29, 2022*

* Fixed various documentation issues.


0.2.0
=====

*September 29, 2022*

* Added ``OpenFormsSlugField`` and renamed ``OpenFormsField`` to 
  ``OpenFormsUUIDField``.
* Added tests for templatetags.
* Fixed various documentation issues.


0.1.0
=====

*September 27, 2022*

* Initial release
