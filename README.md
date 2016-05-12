The Open Permissions Platform Onboarding Service
================================================

Useful Links
============
* [Open Permissions Platform](http://openpermissions.org)
* [Low level Design](https://github.com/openpermissions/onboarding-srv/blob/master/documents/markdown/low-level-design.md)
* [API Documentation](https://github.com/openpermissions/onboarding-srv/blob/master/documents/apiary/api.md)
* [How to use the Onboarding Service](https://github.com/openpermissions/onboarding-srv/blob/master/documents/markdown/how-to-onboard.md)

Service Overview
================
This repository contains an On-Boarding application which allows you to
on-board ("upload") assets to the Open Permissions Platform and generate a Hub Key for each
uploaded asset.

Running locally
---------------
To run the service locally:

```
pip install -r requirements/dev.txt
python setup.py develop
python onboarding/
```

To show a list of available CLI parameters:

```
python onboarding/ -h [--help]
```

To start the service using test.service.conf:

```
python onboarding/ -t [--test]
```

Running tests and generating code coverage
------------------------------------------
To have a "clean" target from build artifacts:

```
make clean
```

To install requirements. By default prod requirement is used:

```
make requirements [REQUIREMENT=dev|prod]
```

To run all unit tests and generate a HTML code coverage report along with a
JUnit XML report in tests/unit/reports:

```
make test
```

To run pyLint and generate a HTML report in tests/unit/reports:

```
make pylint
```

To run create the documentation for the service in _build:

```
make docs
```
