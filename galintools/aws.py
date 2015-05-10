#!/usr/bin/python
import boto.ec2, boto.ec2.autoscale, boto.utils, boto.support, time
from datetime import datetime, timedelta
from galintools.settings import *
from galintools import infra_common

class Ec2:

	def __init__(self, logger, boto_ec2=None, region=settings['DEFAULT_REGION']):
		self.logger = logger

		if not boto_ec2:
			self.ec2 = boto.ec2.connect_to_region(region)
		else:
			self.ec2 = boto_ec2

		logger.debug("Getting self instance id")
		try:
			self.instance_id = boto.utils.get_instance_metadata(timeout=2,num_retries=1)['instance-id']
			logger.debug("Self instance id - %s" % (self.instance_id))
		except Exception, e:
			logger.warning("Can't get self instance id")

	def get_images(self, image_ids=None):
		return_code = 0
		images = None

		try:
			self.logger.debug("Searching images")
			if image_ids:
				images = self.ec2.get_all_images(image_ids=image_ids)
			else:
				images = self.ec2.get_all_images()

		except Exception, e:
			self.logger.exception("Can't search images %s" % (str(image_ids)))
			return_code = 1

		if not images:
			self.logger.warning("No image found")
			return_code = 1

		return (return_code, images)

	def get_instance_obj(self, instance_ids=None, filters=None, dry_run=False, max_results=None):
		instances = []

		self.logger.debug("Searching instances")

		try:
			reservations = self.ec2.get_all_instances(instance_ids=instance_ids, 
													  filters=filters, 
													  dry_run=dry_run, 
													  max_results=max_results)

			instances = [i for r in reservations for i in r.instances]
		except Exception, e:
			self.logger.exception("Can't search instances")

		if not instances:
			self.logger.warning("Can't find any instance")

		return instances

	def get_instance_ids(self, instance_ids=None, filters=None, dry_run=False, max_results=None):
		instance_ids = []

		self.logger.debug("Searching instances ID")

		try:
			reservations = self.ec2.get_all_instances(instance_ids=instance_ids, 
													  filters=filters, 
													  dry_run=dry_run, 
													  max_results=max_results)

			instances = [i for r in reservations for i in r.instances]
			instance_ids = [i.id for i in instances]
		except Exception, e:
			self.logger.exception("Can't search instances")

		if not instance_ids:
			self.logger.warning("Can't find any instance")

		return instance_ids

	def get_instance_fields(self, instance_obj, fields=['id','state']):
		
		instance_fields = [
			'id',
			'groups',
			'public_dns_name',
			'private_dns_name',
			'state',
			'state_code',
			'previous_state',
			'previous_state_code',
			'key_name',
			'instance_type',
			'launch_time',
			'image_id',
			'placement',
			'placement_group',
			'placement_tenancy',
			'kernel',
			'ramdisk',
			'architecture',
			'hypervisor',
			'virtualization_type',
			'product_codes',
			'ami_launch_index',
			'monitored',
			'monitoring_state',
			'spot_instance_request_id',
			'subnet_id',
			'vpc_id',
			'private_ip_address',
			'ip_address',
			'platform',
			'root_device_name',
			'root_device_type',
			'block_device_mapping',
			'state_reason',
			'groups',
			'interfaces',
			'ebs_optimized',
			'instance_profile',
			'tags'
		]

		instance_list = []

		if isinstance(fields, list):
			for field in fields:

				if 'tags' in field:
					instance_list.append(instance_obj.tags[field.strip("tags'[]'")])

				elif field not in instance_fields:
					self.logger.error("'Instance' object has no attribute %s" % (field))
					continue

				elif field == 'groups':
					instance_list.append(instance_obj.groups[0].name)

				elif field == 'system_status':
					instance_list.append(self.ec2.get_all_instance_status(instance_ids=[instance_obj.id])[0].system_status.status)

				elif field == 'instance_status':
					instance_list.append(self.ec2.get_all_instance_status(instance_ids=[instance_obj.id])[0].instance_status.status)

				else:

					try:
						instance_list.append(getattr(instance_obj,field))
					except Exception, e:
						self.logger.exception("Can't get value of field %s. Details: %s" % (field, e))

		else:
			self.logger.error("fields parameter must be a list")

		if len(instance_list) == 1:
			return instance_list[0]
		else:
			return instance_list

	def delete_images(self, images, del_snap=False, del_image=False):
		return_code = 0

		if not del_image:
			while del_image != 'y' and del_image != 'n':
				del_image = raw_input("Deleting images. Are you sure (y/n)? ")
				del_image = del_image.lower()

			if del_image == 'y':
				del_image = True
			elif del_image == 'n':
				del_image = False

		if del_image:
			for image in images:
				try:
					image.deregister()
					self.logger.info("image: %s - Deleted successfully" % (image.id))

				except Exception, e:
					self.logger.exception("image %s - Can't delete image" % (image.id))
					return_code = 1
					continue

				if del_snap:
					try:
						self.logger.debug("image: %s - Deleting snapshots" % (image.id))

						for b in image.block_device_mapping.items():
							snap = b[1].snapshot_id
							self.ec2.delete_snapshot(snapshot_id=snap)
							self.logger.debug("snapshot: %s - Deleted successfully" % (snap))

						self.logger.info("image: %s - snapshots deleted successfully" % (image.id))

					except Exception, e:
						self.logger.exception("snapshot: %s - Can't delete snapshot" % (snap))
						return_code = 1

		else:
			self.logger.warning("Canceling image's deletion")
			return_code = 1

		return return_code

class Autoscaling():
	
	def __init__(self, logger, boto_autoscale=None, region=settings['DEFAULT_REGION']):
		self.logger = logger

		if not boto_autoscale:
			self.autoscale = boto.ec2.autoscale.connect_to_region(region)
		else:
			self.autoscale = boto_autoscale

		self.aws_ec2 = Ec2(logger=logger, region=region)

	def get_launch_configs(self, lcs=[], images=[], older=None):
		return_code = 0
		launchconfigs = []

		try:
			self.logger.debug("Searching launch configurations")
			if lcs:
				launchconfigs = self.autoscale.get_all_launch_configurations(names=lcs)
			else:
				launchconfigs = self.autoscale.get_all_launch_configurations()

			if images:
				if not isinstance(images, list):
					raise ValueError('images parameter must be a list')

				for lc in launchconfigs:
					if lc.image_id in images:
						lcs.append(lc)
				
				launchconfigs = lcs
				lcs = []

			if older:
				if not isinstance(older, list):
					raise ValueError('older parameter must be a list')

				quantity, datetype = older

				quantity = int(quantity)

				if datetype == 'days': 
					timedelta_obj = timedelta(days=quantity)
				elif datetype == 'hours':
					timedelta_obj = timedelta(hours=quantity)
				else:
					raise ValueError('Invalid datetype %s' % (datetype))

				olderthan_date = datetime.now() - timedelta_obj

				for lc in launchconfigs:
					if lc.created_time < olderthan_date:
						lcs.append(lc)

				launchconfigs = lcs

		except Exception, e:
			self.logger.exception("Can't search launch configurations %s" % (str(lcs)))
			return_code = 1

		if not launchconfigs:
			self.logger.error("No launch configurations found")
			return_code = 1

		return (return_code, launchconfigs)

	def delete_launch_configs(self, lcs, del_lc=False, del_image=False, del_snap=False):
		return_code = 0

		if not del_lc:
			while del_lc != 'y' and del_lc != 'n':
				del_lc = raw_input("Deleting launch configurations. Are you sure (y/n)? ")
				del_lc = del_lc.lower()

			if del_lc == 'y':
				del_lc = True
			elif del_lc == 'n':
				del_lc = False

		if del_lc:
			for lc in lcs:
				if del_image:
					images = self.aws_ec2.get_images(lc.image_id)
					if images[0] == 0:
						if self.aws_ec2.delete_images(images=images, del_snap=del_snap, del_image=del_image) != 0:
							return_code = 1
					else:
						return_code = 1

			try:
				lc.delete()
				self.logger.info("launch configuration: %s - Deleted successfully" % (lc.name))

			except Exception, e:
				self.logger.exception("launch configuration: %s - Can't delete launch configuration" % (lc.name))
				return_code = 1

		else:
			self.logger.warning("Canceling launch configuration's deletion")
			return_code = 1

		return return_code

	def count_as_instances(self, as_group):
		self.logger.debug("Counting instances running in autoscaling group %s" % (as_group))
		as_count = 0

		try:
			as_group = self.autoscale.get_all_groups(as_group.split())[0]
			as_count = len(as_group.instances)

		except Exception, e:
			self.logger.exception("Error counting instances running in autoscaling group %s. Details: %s" % (as_group, e))
			as_count = None

		return as_count

class TrustedAdvisor():

	def __init__(self, logger, boto_support=None, region=settings['DEFAULT_REGION']):
		self.logger = logger

		if not boto_support:
			boto.support.connect_to_region(region)
			self.support = boto.support.layer1.SupportConnection()
		else:
			self.support = boto_support

		self.status = None
		self.resources_flagged = None
		self.resources_processed = None
		self.resources_supressed = None
		self.resources_ignored = None

		self.estimated_percent_monthly_savings = None
		self.estimated_monthly_savings = None
	
	def get_trusted_advisor_check_summaries(self, check_id, check_name):
			check_id = check_id.split()

			self.logger.debug("Getting status of %s (%s)" % (check_name, check_id[0]))

			try:
				self.support.refresh_trusted_advisor_check(check_id[0])

				trusted_adv_refresh_status = self.support.describe_trusted_advisor_check_refresh_statuses(check_id)['statuses'][0]

				while trusted_adv_refresh_status['status'] != 'success':
					time.sleep(5)
					trusted_adv_refresh_status = self.support.describe_trusted_advisor_check_refresh_statuses(check_id)['statuses'][0]

				trusted_adv_check_result = self.support.describe_trusted_advisor_check_summaries(check_id)['summaries'][0]

				self.status = trusted_adv_check_result['status']
				self.resources_flagged = trusted_adv_check_result['resourcesSummary']['resourcesFlagged']
				self.resources_processed = trusted_adv_check_result['resourcesSummary']['resourcesProcessed']
				self.resources_supressed = trusted_adv_check_result['resourcesSummary']['resourcesSuppressed']
				self.resources_ignored = trusted_adv_check_result['resourcesSummary']['resourcesIgnored']

				if 'costOptimizing' in trusted_adv_check_result['categorySpecificSummary']:
					self.estimated_monthly_savings = trusted_adv_check_result['categorySpecificSummary']['costOptimizing']['estimatedMonthlySavings']
					self.estimated_percent_monthly_savings = trusted_adv_check_result['categorySpecificSummary']['costOptimizing']['estimatedPercentMonthlySavings']
				else:
					self.estimated_monthly_savings = None
					self.estimated_percent_monthly_savings = None

			except Exception, e:
				self.logger.exception("Error getting status of %s (%s). Details: %s" % (check_name, check_id[0], e))
