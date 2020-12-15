SHELL		:= bash


.PHONY: format


format:
	black setup.py src
	isort setup.py src


requirements.txt: setup.py
