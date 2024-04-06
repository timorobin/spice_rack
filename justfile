#!/usr/bin/env just --justfile
set dotenv-load := true

default:
    just --list

dev-env-setup:
    poetry lock -vv
    poetry install --all-extras


launch-jupyter-lab:
    cd notebooks/  && jupyter lab

unit-tests:
    pytest tests/ --doctest-modules  --pyargs src/


lint:
    ruff check .


run-tests:
    poetry run ruff check .
    # poetry run mypy src/
    poetry run pytest tests/ --doctest-modules  --pyargs src/

make-docs:
    #!/usr/bin/env bash
    cd docs
    make clean
    make html
