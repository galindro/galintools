#!/usr/bin/python

from galintools import infra_common, monitoring, aws
from galintools.settings import *

utils = infra_common.Utils()

logger = utils.create_new_logger(log_config=settings['log'],log_name='a')

aws_ec2 = aws.Ec2(logger=logger)

fields = ['id','state']

for i in aws_ec2.get_instance_obj():
	for field in fields:
		print getattr(i, field)
