SHELL 			:= /bin/bash
.PHONY			:= test format

curdir          := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
VERSION 		:= $(shell python $(curdir)/setup.py --version)
CPU_TYPE 		:= amd64
SNAP_TARGET		:= $(curdir)/hacenada_$(VERSION)_$(CPU_TYPE).snap


format: # reformat source python files
	isort setup.py src
	black setup.py src


requirements.txt: setup.py
	python3 -m venv _virtual_tmp
	. _virtual_tmp/bin/activate \
		&& pip install wheel \
		&& pip install . \
		&& pip freeze | grep -v hacenada > $@
	rm -rf _virtual_tmp


snap: $(SNAP_TARGET)


$(SNAP_TARGET):
	snapcraft --use-lxd
