#!/usr/bin/env just --justfile
set dotenv-load := true

default:
    just --list


run-tests:
    ruff check .
    pytest tests/ --doctest-modules  --pyargs src/


install-and-run-tests:
    just dev-install
    pytest tests


build-lockfile:
    poetry lock -vv


dev-install:
    just build-lockfile
    poetry install


launch-jupyter-lab:
    cd notebooks/  && jupyter lab
