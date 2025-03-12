# :recycle: Contributing

Contributions to this project are very much welcome, please make sure that your code changes are tested and that they follow Python best-practices.

## Getting started

### Install dependencies

```shell
$ pip install ".[test, ci]"
```

### Required environmental variables

The tests require at least two environment variables: `STREAM_KEY` and `STREAM_SECRET`. There are multiple ways to provide that:
- simply set it in your current shell (`export STREAM_KEY=xyz`)
- you could use [direnv](https://direnv.net/)

### Run tests

Make sure you can run the test suite. Tests are run via `pytest`.

```shell
$ export STREAM_KEY=my_api_key
$ export STREAM_SECRET=my_api_secret
$ make test
```

> 💡 If you're on a Unix system, you could also use [direnv](https://direnv.net/) to set up these env vars.

### Run linters

We use Black (code formatter), isort (code formatter), flake8 (linter) and mypy (static type checker) to ensure high code quality. To execute these checks, just run this command in your virtual environment:

```shell
$ make lint
```

### Using Docker for development

You can also use Docker to run tests and linters without setting up a local Python environment. This is especially useful for ensuring consistent behavior across different environments.

#### Available Docker targets

- `lint_with_docker`: Run linters in Docker
- `lint-fix_with_docker`: Fix linting issues in Docker
- `test_with_docker`: Run tests in Docker
- `check_with_docker`: Run both linters and tests in Docker

#### Specifying Python version

You can specify which Python version to use by setting the `PYTHON_VERSION` environment variable:

```shell
$ PYTHON_VERSION=3.9 make lint_with_docker
```

The default Python version is 3.8 if not specified.

#### Accessing host services from Docker

When running tests in Docker, the container needs to access services running on your host machine (like a local Stream Chat server). The Docker targets use `host.docker.internal` to access the host machine, which is automatically configured with the `--add-host=host.docker.internal:host-gateway` flag.

> ⚠️ **Note**: The `host.docker.internal` DNS name works on Docker for Mac, Docker for Windows, and recent versions of Docker for Linux. If you're using an older version of Docker for Linux, you might need to use your host's actual IP address instead.

For tests that need to access a Stream Chat server running on your host machine, the Docker targets automatically set `STREAM_HOST=http://host.docker.internal:3030`.

#### Examples

Run linters in Docker:
```shell
$ make lint_with_docker
```

Fix linting issues in Docker:
```shell
$ make lint-fix_with_docker
```

Run tests in Docker:
```shell
$ make test_with_docker
```

Run both linters and tests in Docker:
```shell
$ make check_with_docker
```

## Commit message convention

Since we're autogenerating our [CHANGELOG](./CHANGELOG.md), we need to follow a specific commit message convention.
You can read about conventional commits [here](https://www.conventionalcommits.org/). Here's how a usual commit message looks like for a new feature: `feat: allow provided config object to extend other configs`. A bugfix: `fix: prevent racing of requests`.

## Release (for Stream developers)

Releasing this package involves two GitHub Action steps:

- Kick off a job called `initiate_release` ([link](https://github.com/GetStream/stream-chat-python/actions/workflows/initiate_release.yml)).

The job creates a pull request with the changelog. Check if it looks good.

- Merge the pull request.

Once the PR is merged, it automatically kicks off another job which will publish the package to Pypi, create the tag and created a GitHub release.