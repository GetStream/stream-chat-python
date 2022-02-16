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

## Commit message convention

Since we're autogenerating our [CHANGELOG](./CHANGELOG.md), we need to follow a specific commit message convention.
You can read about conventional commits [here](https://www.conventionalcommits.org/). Here's how a usual commit message looks like for a new feature: `feat: allow provided config object to extend other configs`. A bugfix: `fix: prevent racing of requests`.

## Release (for Stream developers)

Releasing this package involves two GitHub Action steps:

- Kick off a job called `initiate_release` ([link](https://github.com/GetStream/stream-chat-python/actions/workflows/initiate_release.yml)).

The job creates a pull request with the changelog. Check if it looks good.

- Merge the pull request.

Once the PR is merged, it automatically kicks off another job which will publish the package to Pypi, create the tag and created a GitHub release.