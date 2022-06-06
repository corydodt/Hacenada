#!/usr/bin/env make

SHELL 				:= /usr/bin/env bash
PROG				:= Hacenada
SOURCES				:= src/**/*.py conftest.py pyproject.toml poetry.lock pytest.ini tox.ini
TAGGED_VERSION		:= $(shell tools/describe-version)
PYPROJECT_VERSION	:= $(shell poetry version -s)
SDIST				:= dist/$(PROG)-$(PYPROJECT_VERSION).tar.gz
WHEEL				:= dist/$(PROG)-$(PYPROJECT_VERSION)-py3-none-any.whl
RELEASE_ARTIFACTS	:= $(SDIST) $(WHEEL)


.PHONY: format sdist clean test print-release-artifacts


format: # reformat source python files
	isort conftest.py src
	black conftest.py src


requirements.txt: pyproject.toml
	poetry export -o requirements.txt 


$(RELEASE_ARTIFACTS) &: $(SOURCES)
	@if [[ $(TAGGED_VERSION) != "v$(PYPROJECT_VERSION)" ]]; then \
		echo "** Warning: pyproject.toml version v$(PYPROJECT_VERSION) != git tag version $(TAGGED_VERSION)" 1>&2; \
		echo "** The files produced cannot be released" 1>&2; \
	fi
	poetry build


print-release-artifacts: $(RELEASE_ARTIFACTS)
	@echo $(RELEASE_ARTIFACTS)


clean:
	rm -f $(RELEASE_ARTIFACTS)


test:
	tox
