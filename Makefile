PYTHON = python3
PIP = pip3
PYTHONIOENCODING=utf8

DOCKER_BASE_IMAGE = docker.io/ocrd/core:v2.69.0
DOCKER_TAG = ocrd/dinglehopper

help:
	@echo
	@echo "  Targets"
	@echo
	@echo "    install Install full Python package via pip"
	@echo "    docker  Build the ocrd/dinglehopper docker image"

# Install Python package via pip
install:
	$(PIP) install .

docker:
	docker build \
	--build-arg DOCKER_BASE_IMAGE=$(DOCKER_BASE_IMAGE) \
	--build-arg VCS_REF=$$(git rev-parse --short HEAD) \
	--build-arg BUILD_DATE=$$(date -u +"%Y-%m-%dT%H:%M:%SZ") \
	-t $(DOCKER_TAG) .

.PHONY: help install docker
