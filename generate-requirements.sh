#!/usr/bin/env bash

# Skript to generate Python version specific requirements files in docker containers

for PY_VERSION in 3.5 3.6 3.7 3.8 3.9; do
    docker run --rm -it -v "${PWD}:/dinglehopper" python:${PY_VERSION} /bin/bash -c "cd /dinglehopper ; pip install pip-tools ; pip-compile --output-file py${PY_VERSION}-requirements.txt requirements.in"
done
