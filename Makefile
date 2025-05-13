PYTHON = python3
PIP = pip3
PYTHONIOENCODING=utf8
PYTEST_ARGS = -vv

DOCKER_BASE_IMAGE ?= docker.io/ocrd/core:latest
DOCKER_TAG ?= ocrd/dinglehopper
DOCKER ?= docker

help:
	@echo
	@echo "  Targets"
	@echo
	@echo "    install Install full Python package via pip"
	@echo "    docker  Build the ocrd/dinglehopper docker image"

# Install Python package via pip
install:
	$(PIP) install .

install-dev:
	$(PIP) install -e .

test:
	pytest $(PYTEST_ARGS)

docker:
	$(DOCKER) build \
	--build-arg DOCKER_BASE_IMAGE=$(DOCKER_BASE_IMAGE) \
	--build-arg VCS_REF=$$(git rev-parse --short HEAD) \
	--build-arg BUILD_DATE=$$(date -u +"%Y-%m-%dT%H:%M:%SZ") \
	-t $(DOCKER_TAG) .

.PHONY: help install install-dev test docker
