# galintools
This is a simple python package that makes usage of some other python packages like [boto] and [azure] to provide functions and tools for manage some System Administrator's day-to-day tasks.

It is divided into some functions, classes and subpackages. It has some built-in scripts that can be used to make administrative operations.

# Installation

* Clone repository
```bash
$ git clone https://github.com/galindro/galintools.git
```

* Run install script as root
```bash
$ sudo ./install.sh
```

* To upgrade, update the repository working copy and then, run upgrade script as root
```bash
$ sudo ./upgrade.sh
```

* To uninstall, run uninstall script as root
```bash
$ sudo ./uninstall.sh
```

# Installed scripts
* as_zabbix: Provides autoregistration of AWS EC2 Autoscaling instances in Zabbix
* aws_zabbix: Provides AWS statistics (BETA). TODO: make a template...
* delete_image: Delete AWS EC2 images
* delete_lc: Delete AWS EC2 Launch Configurations
* ec2_state: Start, stop or terminate AWS EC2 instances

# Documentation
https://github.com/galindro/galintools/wiki. TODO: finish the documentation...

# License
GNU GENERAL PUBLIC LICENSE Version 2, June 1991
