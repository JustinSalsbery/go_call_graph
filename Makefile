INSTALL_NAME := flow
INSTALL_DIR := /usr/local/bin

SHELL := bash

.SILENT:

.PHONY: help options
help options:
	echo "options:"
	echo -e "\tinstall"
	echo -e "\tuninstall"
	echo -e "\toptions (this)"

.PHONY: install
install:
	cp main.py ${INSTALL_DIR}/${INSTALL_NAME}
	chmod +x ${INSTALL_DIR}/${INSTALL_NAME}

.PHONY: uninstall
uninstall:
	rm -f ${INSTALL_DIR}/${INSTALL_NAME}