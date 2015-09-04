#!/usr/bin/python
import ez_setup, glob
ez_setup.use_setuptools()

from setuptools import setup, find_packages
setup(
	name = "galintools",
	version = "0.0.3",
	packages = find_packages(),

	data_files=[
		('/opt/galintools/etc/', ['etc/galintools.json']),
		('/opt/galintools/etc/', glob.glob("scripts/etc/*.json")),
		('/opt/galintools/bin/', glob.glob("scripts/bin/*")),
		('/etc/profile.d/', ['etc/galintools.sh'])
	],

	install_requires = [
		"feedparser",
		"beautifulsoup4",
		"dnspython",
		"progressbar",
		"azure==0.10.0",
		"awscli",
		"boto",
		"zabbix-api"
	],
	
	author = "Bruno Galindro da Costa",
	author_email = "bruno.galindro@gmail.com",
	description = "Some tools for work with python",
	license = "GNU GPL",
	url = ""
)
