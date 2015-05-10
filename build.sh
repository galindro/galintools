#!/bin/bash
EDIT_VERSION="${1}"
if [ "${EDIT_VERSION}" == "v" ]; then
	echo "Openning setup.py and CHANGES.txt to make version change"
	sleep 2
	vim setup.py
	vim CHANGES.txt
fi
rm -rf build/*
./setup.py build
