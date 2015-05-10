#!/bin/bash
INSTALL_DIR="${1}"

fn_help() {
	echo -e "\nUsage: $0 <installation_dir>\n"
	exit 1
}

if [ "$EUID" -ne 0 ]; then 
	echo "Please run as root"
	exit 1
fi

if [ "$#" -lt 1 ]; then
	fn_help
fi

if ! [ -d "${1}" ]; then
	echo "Installation directory ${1} not exists"
	exit 1
fi

while [ "${RESP}" != "y" ] && [ "${RESP}" != "n" ]; do
	echo -n "This script will REMOVE galintools. Are you sure (y/n)? "
	read RESP
done

if [ "${RESP}" == "n" ]; then 
	echo "Operation canceled"
	exit 1
fi

rm -rf ${INSTALL_DIR}

pip uninstall -y galintools
