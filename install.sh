#!/bin/bash
ZABBIX_VERSION="2.4"
ZABBIX_RELEASE="${ZABBIX_VERSION}-1"
ZABBIX_PACKAGE_URL="http://repo.zabbix.com/zabbix/${ZABBIX_VERSION}/ubuntu/pool/main/z/zabbix-release"
ZABBIX_PACKAGE_NAME="zabbix-release_${ZABBIX_RELEASE}+`lsb_release -c -s`_all.deb"

if [ "$EUID" -ne 0 ]; then 
	echo "Please run as root"
	exit 1
fi

if ! dpkg -l |grep -q zabbix-sender; then
	wget ${ZABBIX_PACKAGE_URL}/${ZABBIX_PACKAGE_NAME} -O /tmp/${ZABBIX_PACKAGE_NAME}
	dpkg -i /tmp/${ZABBIX_PACKAGE_NAME}
	apt-get update
	apt-get install python-pip python-dev zabbix-sender
fi

./build.sh
./setup.py install --force
