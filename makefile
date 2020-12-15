SHELL		:= bash


.PHONY: format


format:
	black setup.py src
	isort setup.py src


requirements.txt: setup.py
	python3 -m venv _virtual_tmp
	. _virtual_tmp/bin/activate \
		&& pip install wheel \
		&& pip install . \
		&& pip freeze | grep -v hacenada > $@
	rm -rf _virtual_tmp
