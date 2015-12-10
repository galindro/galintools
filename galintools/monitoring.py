#!/usr/bin/python
import syslog, subprocess, feedparser, re, urllib2, json
import boto.ec2, boto.ec2.autoscale, boto.support
from bs4 import BeautifulSoup
from datetime import datetime
from galintools.settings import *
from galintools import infra_common, aws

class Zabbix():
	
	def __init__(self, logger, server=None, hostname=None, zabbix_sender_bin=settings['ZABBIX_SENDER_BIN']):
		self.server = server
		self.hostname = hostname
		self.zabbix_sender_bin = zabbix_sender_bin
		self.logger = logger

	def get_ids(self, names, zapi_method, api_filter_param, api_id_result_key, result_type="dict"):
		zbx_ids = []
		result_types = ['dict','list']

		if result_type not in result_types:
			self.logger.error("result_type parameter must be %s or %s" %(result_types[0], result_types[1]))

		if not isinstance(names, list):
			self.logger.error("Paramenter names must be a list")

		else:
			for name in names:
				self.logger.debug("Getting id of %s. Method: %s.%s" %(name, zapi_method.__dict__['data']['prefix'], 'get'))
			
				try:
					result = getattr(zapi_method,'get')({"filter":{api_filter_param:[name]}})

					if result:
						zbx_id = result[0][api_id_result_key]
						
						if result_type == "dict":
							zbx_ids.append({api_id_result_key : zbx_id})
						elif result_type == "list":
							zbx_ids.append(zbx_id)

					else:
						self.logger.warn("Can't get ID of %s from zabbix. Details: Object not exists" % (name))

				except Exception, e:
					self.logger.error("Error getting ID of %s from zabbix. Details: %s" % (name, str(e)))
					continue

		return zbx_ids

	def zabbix_sender(self, key, value):
		if not self.server:
			logger.error("Server attribute isn't set")
			return 1

		if not self.hostname:
			logger.error("Hostname attribute isn't set")
			return 1

		cmd = [self.zabbix_sender_bin,
			   "-vv",
			   "-z",
			   self.server,
			   "-s",
			   self.hostname,
			   "-k",
			   key,
			   "-o",
			   str(value)]

		self.logger.debug("Inserting value %s in key %s" % (value, key))

		p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		
		p.wait()

		if p.returncode != 0:
			self.logger.error("Error sending data to zabbix server. Error detail: %s" % (str(p.stderr.readlines())))
		
		return p

	def aws_status_page_discovery(self, url=settings['AWS_STATUS_PAGE']):
		html_parsed = {}
		urls = []
		result = {}

		self.logger.debug("Parsing amazon status page: %s" % (url))

		try:	

			url_content = urllib2.urlopen(url).read()

			soup = BeautifulSoup(url_content)
	
			rss_uris = soup.findAll(href=re.compile('rss$'))

			for rss_uri in rss_uris:
				html_parsed['{#FEED_NAME}'] = rss_uri['href'].split('/')[2].rstrip('.rss')
				html_parsed['{#FEED_URL}'] = url + rss_uri['href']
				urls.append(html_parsed.copy())

			result['data'] = urls

		except Exception, e:
			result = {}
			self.logger.exception("Error parsing amazon status page: %s" % (url))

		return result

	def aws_autoscaling_discovery(self, region=settings['DEFAULT_REGION']):
		as_group_info = {}
		as_groups = []
		result = {}

		self.logger.debug("Discovering autoscaling group names")

		try:
			autoscale = boto.ec2.autoscale.connect_to_region(region)

			for as_group in autoscale.get_all_groups():
				as_group_info['{#ASGROUPNAME}'] = as_group.name
				as_groups.append(as_group_info.copy())
			
			result['data'] = as_groups

		except Exception, e:
			result = {}
			self.logger.exception("Error discovering autoscaling group names. Details: %s" % (e))

		return json.dumps(result, indent=2)

	def aws_ec2_discovery(self, region=settings['DEFAULT_REGION']):
		ec2_instances_info = {}
		ec2_instances = []
		result = {}

		self.logger.debug("Discovering ec2 instances")

		try:
			aws_ec2 = aws.Ec2(logger=self.logger, region=region)
			ec2 = boto.ec2.connect_to_region(region)

			for instance in aws_ec2.get_instance_obj():
				ec2_instances_info['{#INSTANCE_ID}'] = instance.id
				ec2_instances_info['{#INSTANCE_NAME}'] = instance.tags['Name']
				ec2_instances_info['{#INSTANCE_TYPE}'] = instance.instance_type
				ec2_instances_info['{#INSTANCE_AVAILABILITY_ZONE}'] = instance.placement
				ec2_instances_info['{#INSTANCE_STATE}'] = instance.state
				try:
					ec2_instances_info['{#INSTANCE_SYSTEM_STATUS}'] = ec2.get_all_instance_status(instance_ids=[instance.id])[0].system_status.status
					ec2_instances_info['{#INSTANCE_SYSTEM_STATUS}'] = ec2.get_all_instance_status(instance_ids=[instance.id])[0].instance_status.status
				except Exception, e:
					pass
				ec2_instances_info['{#INSTANCE_PUBLIC_DNS}'] = instance.public_dns_name
				ec2_instances_info['{#INSTANCE_PUBLIC_IP}'] = instance.ip_address
				ec2_instances_info['{#INSTANCE_KEY_NAME}'] = instance.key_name
				ec2_instances_info['{#INSTANCE_MONITORING}'] = str(instance.monitored)
				ec2_instances_info['{#INSTANCE_LAUNCH_TIME}'] = instance.launch_time
				ec2_instances_info['{#INSTANCE_SECURITY_GROUPS}'] = instance.groups[0].name
				ec2_instances.append(ec2_instances_info.copy())
			
			result['data'] = ec2_instances

		except Exception, e:
			result = {}
			self.logger.exception("Error discovering ec2 instances. Details: %s" % (e))

		return json.dumps(result, indent=2)

	def aws_trusted_advisor_discovery(self, category, region=settings['DEFAULT_REGION']):
		aws_trusted_advisor_info = {}
		aws_trusted_advisor = []
		result = {}

		self.logger.debug("Discovering aws trusted advisor checks")

		try:
			boto.support.connect_to_region(region)

			support = boto.support.layer1.SupportConnection()

			trusted_adv_checks = support.describe_trusted_advisor_checks('en')

			for trusted_adv_check in trusted_adv_checks['checks']:
				if trusted_adv_check['category'] == category:
					aws_trusted_advisor_info['{#TRUSTED_ADV_NAME}'] = trusted_adv_check['name']
					aws_trusted_advisor_info['{#TRUSTED_ADV_ID}'] = trusted_adv_check['id']
				aws_trusted_advisor.append(aws_trusted_advisor_info.copy())

			result['data'] = aws_trusted_advisor

		except Exception, e:
			result = {}
			self.logger.exception("Error discovering aws trusted advisor checks. Details: %s" % (e))

		return result

	def get_feed_status(self, rssfeed):
		result = None

		self.logger.debug("Getting rss feed from %s" % (rssfeed))
		
		myfeed = feedparser.parse(rssfeed)
		
		#Grabs only the newest entry.
		feednumber = 0 

		if myfeed['entries']:
			if myfeed['entries'][feednumber]['title']:
				title = myfeed['entries'][feednumber]['title']
				description = myfeed['entries'][feednumber]['description']
				link = myfeed['entries'][feednumber]['link']
				feeddate = myfeed['entries'][feednumber]['updated_parsed']

				now = datetime.utcnow()
				orderedfeeddate = datetime(feeddate.tm_year, feeddate.tm_mon, feeddate.tm_mday, feeddate.tm_hour, feeddate.tm_min)
				orderednowdate = datetime(now.year, now.month, now.day, now.hour, now.minute)
				timediff = orderednowdate - orderedfeeddate
				hourssinceposted = timediff.days * 24 + timediff.seconds / 60 / 60

				result = 'Posted in %s (%s hrs ago) ; Title: %s ; Description: %s ; Link: %s' % (orderedfeeddate, hourssinceposted, title,  description, link)

			else:
				self.logger.error("Error getting rss feed from %s. Details: %s" % (rssfeed, myfeed['feed']['summary']))
		else:
			self.logger.info('No feeds where posted in url %s' % (rssfeed))

		return result