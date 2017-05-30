#!/bin/bash
INSTALL_DIR=`echo ${1} | sed -r 's,(.*)/$,\1,g'`
DATE=`date +%Y%m%d%H%M%S`

fn_help() {
	echo -e "\nUsage: $0 <installation_dir> <remove>\n"
	echo "If you want to upgrade this package, you need to inform the installation directory and if you want to remove it"
	echo "The default behaviour is to make a backup of it before the upgrade process"
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
	if [ "${2}" == "remove" ]; then
		echo -n "This script will upgrade galintools and will REMOVE the installation directory ${INSTALL_DIR}. Are you sure (y/n)? "
	else
		echo -n "This script will upgrade galintools and will make a backup of the installation directory ${INSTALL_DIR} and will mantain configuration files. Are you sure (y/n)? "
	fi
	read RESP
done

if [ "${RESP}" == "n" ]; then 
	echo "Operation canceled"
	exit 1
fi

if [ "${2}" == "remove" ]; then
	rm -rf ${INSTALL_DIR}
else
	mv ${INSTALL_DIR} ${INSTALL_DIR}_${DATE}
fi

pip uninstall -y galintools

./install.sh

if [ "${2}" != "remove" ]; then
	cp -f ${INSTALL_DIR}_${DATE}/etc/* ${INSTALL_DIR}/etc/
fi

