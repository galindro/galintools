# galintools
This is a simple python package that makes usage of some other python packages like [boto] and [azure] to provide functions and tools for manage some System Administrator's day-to-day tasks.

It is divided into some functions, classes and subpackages and provides some built-in tools (scripts) that can be used to make administrative operations.

## Package Reference Guide:

### Packages

#### aws.ec2
This package provides exclusive classes and functions to work with aws ec2

##### Classes and Functions

```Python
class awstools.aws.ec2.Ec2(self, logger, boto_ec2=None, region=settings.DEFAULT_REGION)
```
* **Parameters:** 
  * logger - instance of python logging.getLogger()
  * boto_ec2 - instance of boto.ec2
  * region (string) - aws region

* **Returns:** an instance of awstools.aws.ec2.Ec2 class

```Python
def awstools.aws.ec2.Ec2.get_images(self, image_ids)
```
* **Parameters:** 
  * image_ids (list of strings) - list of images to search

* **Returns:** a list of boto.ec2.image.Image

```Python
def awstools.aws.ec2.Ec2.delete_images(self, images, del_snap=False, del_image=False)
```
* **Parameters:** 
  * images - a list of boto.ec2.image.Image
  * del_snap (boolean) - delete snapshots associated with image?
  * del_image (boolean) - if true, it will delete images without confirmation

* **Returns:** 0 if everything is OK, 1 if an error was ocurred

```Python
class awstools.aws.ec2.Autoscaling(self, logger, boto_autoscale=None, region=settings.DEFAULT_REGION)
```
* **Parameters:** 
  * logger - instance of python logging.getLogger()
  * boto_ec2 - instance of boto.ec2.autoscale
  * region (string) - aws region

* **Returns:** an instance of awstools.aws.ec2.Autoscaling class

```Python
def awstools.aws.ec2.Autoscaling.get_launch_configs(self, lcs)
```
* **Parameters:** 
  * lcs (list of strings) - list of launch configuration names to search

* **Returns:** List of boto.ec2.autoscale.launchconfig.LaunchConfiguration instances.

#### monitoring.zabbix
This package provides exclusive classes and functions to work with zabbix monitoring tool

#### windows_azure.windows_azure_storage
This package provides exclusive classes and functions to work with microsoft windows azure storage

### Files
#### settings.py

[boto]:https://github.com/boto/boto
[azure]:https://github.com/Azure/azure-sdk-for-python/
