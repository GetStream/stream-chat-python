# stream-chat-python 

[![Build Status](https://travis-ci.com/GetStream/stream-chat-python.svg?token=WystDPP9vxKnwsd8NwW1&branch=master)](https://travis-ci.com/GetStream/stream-chat-python) [![codecov](https://codecov.io/gh/GetStream/stream-chat-python/branch/master/graph/badge.svg)](https://codecov.io/gh/GetStream/stream-chat-python) [![PyPI version](https://badge.fury.io/py/stream-chat.svg)](http://badge.fury.io/py/stream-chat)

stream-chat-python is the official Python client for Stream chat.

### Installation

stream-python supports:

- Python (3.4, 3.5, 3.6, 3.7)

#### Install from Pypi

```bash
pip install stream-chat
```

### Contributing

First, make sure you can run the test suite. Tests are run via py.test

```bash
STREAM_KEY=my_api_key STREAM_SECRET=my_api_secret py.test stream_chat/ -v
```

Install black and pycodestyle

```
pip install pycodestyle
pip install pycodestyle
```


### Releasing a new version

In order to release new version you need to be a maintainer on Pypi.

- Update CHANGELOG
- Make sure you have twine installed (pip install twine)
- Update the version on setup.py
- Commit and push to Github
- Create a new tag for the version (eg. `v2.9.0`)
- Create a new dist with python `python setup.py sdist`
- Upload the new distributable with wine `twine upload dist/stream-chat-VERSION-NAME.tar.gz`

If unsure you can also test using the Pypi test servers `twine upload --repository-url https://test.pypi.org/legacy/ dist/stream-chat-VERSION-NAME.tar.gz`
