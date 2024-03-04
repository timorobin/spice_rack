#!/usr/bin/env just --justfile
set dotenv-load := true

default:
    just --list

dev-env-setup:
    poetry lock -vv
    poetry install


launch-jupyter-lab:
    cd notebooks/  && jupyter lab


unit-tests:
    pytest tests/ --doctest-modules  --pyargs src/


all-tests:
    poetry run ruff check .
    # poetry run mypy src/
    poetry run pytest tests/ --doctest-modules  --pyargs src/
