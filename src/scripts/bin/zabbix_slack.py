#!/usr/bin/python
import argparse, os, json
from flask import Flask, request
from galintools import infra_common, monitoring
from galintools.settings import *

# Command line parsing
parser = argparse.ArgumentParser(description='Zabbix Slack Outgoing WebHook Parser')

parser.add_argument('-c','--config', 
                    required=True, 
                    help='Config file')

args = parser.parse_args()

utils = infra_common.Utils()

config_parsed = utils.load_json_config(args.config)
if config_parsed == {}:
  exit(1)

try:
  logger = utils.create_new_logger(log_config=config_parsed['log'],
                                   log_name=os.path.basename(__file__))
except Exception, e:
  logger = utils.create_new_logger(log_config=settings['log'],
                                   log_name=os.path.basename(__file__))

if logger == 1:
  exit(1)

if 'slack_token' not in config_parsed:
  logger.error("Add the Outgoing WebHook token to the slack_token key in config file before start this script")
  exit(1)

app = Flask(__name__)

@app.route("/", methods=['POST'])
def slack_webhook():
    error = None
    if request.method == 'POST':
      request_token = request.form['token']

      if request_token != config_parsed['slack_token']:
        error_msg = "Invalid token: %s" % (request_token)
        logger.error(error_msg)
        return error_msg
      else:
        logger.info("Message received")
        
        zabbix = monitoring.Zabbix(server=config_parsed['zabbix_server'],
                                   hostname=config_parsed['host_name'],
                                   logger=logger)

        zabbix.zabbix_sender(key=config_parsed['key'],
                             value=request.form['timestamp'])

        return "Message sent to zabbix server: %s" % (config_parsed['zabbix_server'])

if __name__ == "__main__":
    app.run()
