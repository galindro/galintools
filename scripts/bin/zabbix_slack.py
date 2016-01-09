#!/usr/bin/python
import argparse, os, json
from flask import Flask, request
from galintools import infra_common, monitoring
from galintools.settings import *

def exec_thread(t):
  t.start()
  return t

# Command line parsing
parser = argparse.ArgumentParser(description='Zabbix Slack Outgoing WebHook Parser')

parser.add_argument('-t','--token',
                    required=True, 
                    help='Slack Token')

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


app = Flask(__name__)

@app.route("/", methods=['POST'])
def slack_webhook():
    error = None
    if request.method == 'POST':
      request_token = request.form['token']

      if request_token != args.token:
        error_msg = "Invalid token: %s" % (request_token)
        logger.error(error_msg)
        return error_msg
      else:
        logger.info("Message received")
        
        zabbix = monitoring.Zabbix(server=config_parsed['url'],
                                   hostname=config_parsed['hostname'],
                                   logger=logger)

        zabbix.zabbix_sender(key=config_parsed['key'],
                             value=request.form['timestamp'])

        return "Message sent to zabbix server: %s" % (config_parsed['url'])

if __name__ == "__main__":
    app.run()
