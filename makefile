SHELL 			:= /bin/bash
.PHONY			:= test format


format: # reformat source python files
	isort setup.py src
	black setup.py src


test: # run automated tests
	tox


requirements.txt: setup.py
	python3 -m venv _virtual_tmp
	. _virtual_tmp/bin/activate \
		&& pip install wheel \
		&& pip install . \
		&& pip freeze | grep -v hacenada > $@
	rm -rf _virtual_tmp
