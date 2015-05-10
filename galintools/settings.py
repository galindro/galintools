import json, boto.ec2

config = "/opt/galintools/etc/galintools.json"
regions = []

#Try to open and parsing the file
try:
	f = open(config)
	settings = json.loads(f.read())
except Exception, e:
	print "Error parsing config %s. Details: %s" % (config, str(e))

try:
	for r in boto.ec2.regions():
		regions.append(r.name)

	settings['REGIONS'] = regions
except Exception, e:
	print "Error getting amazon regions. Details: %s" % (str(e))
