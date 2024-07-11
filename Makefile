INSTALL_NAME := flow
INSTALL_DIR := /usr/local/bin

SHELL := bash

.PHONY: help options
help options:
	echo "options:"
	echo -e "\tinstall"
	echo -e "\tuninstall"
	echo -e "\toptions (this)"

.PHONY: install
install:
	sudo cp main.py ${INSTALL_DIR}/${INSTALL_NAME}
	sudo chmod +x ${INSTALL_DIR}/${INSTALL_NAME}

.PHONY: uninstall
uninstall:
	sudo rm -f ${INSTALL_DIR}/${INSTALL_NAME}