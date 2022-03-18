# MedOps Health Platform

MedOps is a platform for ingesting and managing patient care and records in a
medical organization.

## Repository Setup

### Requirements

This repository uses python3.9+.

It's recommended that you use a virtual environment when working with
the repository to avoid conflict between different environments. With
virtualenv installed you can create a new environment by running:

```
python -m virtualenv .venv
```

Then activate the environment:

```
source .venv/bin/activate (macOS/*nix)
.venv/bin/activate.cmd (Windows)
```


If you are running on linux with a strange architecture, you may need to install
`llvm-11`, `llvm-11-dev`, `llvm-11-tools`, `build-essential`, etc.
so that librosa can install properly. (Somehow llvm-lite ahs to get installed
but it's a big pain.)

Then install the requirements:

```
python -m pip install requirements
```

This repository is configured to use [pre-commit](https://pre-commit.com/) to
enforce coding styles, which will run flake8 and some other hooks to
automatically fix things like trailing whitespace, line endings. To activate the pre-commit hooks
run `pre-commit install` after  the dependencies have beeninstalled.


### Documentation

The system design documentation is in the `docs/` folder. While much of
it can be viewed in its source form, the documentation is also
[hosted here](https://ec530-project2.josephrossi.us/)

If you want to author or build documentation you'll need to install the dependencies from `docs/requirements.txt`. The documentation can then
be built using `make html`. You can then open the `_build/html/index.html`
to see the generated documentation.

## Development Guidelines

When working on the health platform, all branches should correspond to an open
issue. If an issue is not opened, you must open one first with a thorough
description of the work being done. Your branch should be named according to the
following convention:

`<github username>-medops-<issue number>/<summary>`

For example, if `medcoder` opens a PR for issue #33, which is about design
documentation for the devices API skeleton, an appropriate branch name would
be `medcoder-medops-33/device-api-design-docs`.

Before creating a PR, create an empty git commit with a summary that references
the issue number being referenced or fixed and the description should clearly
identify the work done. The branch should be rebased on the HEAD of the `main`
branch before being opened to ensure a linear revision history.

The above guidelines will ensure that committed work is traceable to product
requirements, defects or enhancements. If you start work that does not have an
issue associated with it, write it up and make sure to associate it with your commit.

Once your PR is merged into the `main` branch, it should be deleted.

### Testing

All implementations should have unit tests written to verify their
implementation. Tests should be added into files under `tests/` directory with
all the documentation necessary to explain the functionality being tested. This
repository uses `pytest` as its test runner.
