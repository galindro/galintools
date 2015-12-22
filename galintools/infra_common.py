#!/usr/bin/python

import time, json, threading, os, sys, subprocess, logging, logging.config

class Utils:
  """Class with functions for general usage"""
  def __init__(self):
    self.return_code = 0

  def create_new_logger(self, log_config, log_name=None):
    """Create a new logger object based on a dictonary
       https://docs.python.org/2/library/logging.config.html#logging.config.dictConfig
    """
    if log_name:
      log_config['loggers'] = {log_name:log_config['loggers']['logger']}

    #Get log configuration
    try:
      logging.config.dictConfig(log_config)
    except Exception, e:
      print "Error parsing log configuration. Details: %s" % (str(e))
      return 1

    #Get the logger from config
    try:
      if log_name:
        logger = logging.getLogger(log_name)
      else:
        logger = logging.getLogger("logger")
    except Exception, e:
      print "Error getting logger from configuration. Details: %s" % (str(e))
      return 1

    #Return the logger object
    return logger

  def get_timestamp(self):
    """Get current timestamp"""

    #Get current datetime
    now = time.time()
    localtime = time.localtime(now)
    milliseconds = '%03d' % int((now - int(now)) * 1000)

    #Format the result and return the string
    return time.strftime('%Y%m%d-%H%M%S-', localtime) + milliseconds

  def bytes_to(self,bytes,to,bsize=1024):
    """convert bytes to megabytes, etc.
       sample code:
         print('mb= ' + str(bytes_to(314575262000000, 'm')))
   
       sample output: 
         mb= 300002347.946

       Acceptable byte letters: k, m, g, t, p, e 
    """
   
    a = {'k' : 1, 'm': 2, 'g' : 3, 't' : 4, 'p' : 5, 'e' : 6 }
    r = float(bytes)
    for i in range(a[to]):
      r = r / bsize
   
    return(r)

  def set_return_code(self, code):
    """Function used by scripts to set exit / return code"""
    if code != 0:
      self.return_code = code

  def load_json_config(self, config):
    """Load a json config file into a dictonary"""

    #Try to open and parsing the file
    try:
      f = open(config)
      return json.loads(f.read())
    except Exception, e:
      print "Error parsing config %s. Details: %s" % (config, e)
      return {}

  def list_to_string(self, list_content, delimiter=" "):
    """Convert a list to a string, joining items with a delimiter.
       The default delimiter is a blank space
    """
    return str(delimiter.join('"{0}"'.format(w) for w in list_content))

  def exec_cmd(self, cmd):
    result = None
    return_code = None

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    result = p.communicate()
    return_code = p.returncode

    return (return_code, result[0])

  def upstart_service(self, service, action):   
    cmd = ['service',
         service,
         action]
    return self.exec_cmd(cmd)

  def restart_upstart_service(self, service, logger):
    logger.info("Restarting service %s" % (service))
    p = self.upstart_service(service, 'restart')

    if p[0] != 0:
      logger.warning("Error restarting service %s. Trying to stop first. Details: %s" % (service, p[1]))
      p = self.upstart_service(service, 'stop')

      if p[0] == 0:
        logger.info("Starting service %s" % (service))
        p = self.upstart_service(service, 'start')

        if p[0] != 0:
          logger.error("Error starting service %s. Details: %s" % (service, p[1]))
          return False

      else:
        logger.error("Error stopping service %s. Details: %s" % (service, p[1]))
        return False

    else:
      logger.info("Service %s started. Details: %s" % (service, p[1]))

    return True

class FilterInfoMessages(logging.Filter):
  """Class used to filter INFO messages to log handlers
     https://docs.python.org/2/library/logging.html#logging.Filter
  """
  def filter(self, rec):
    return rec.levelno == logging.INFO

class NewThread(threading.Thread):
  """Class used create a new thread
     http://www.tutorialspoint.com/python/python_multithreading.htm
  """
  def __init__(self, thread_name, function, *args):
    threading.Thread.__init__(self)
    self.name = thread_name
    self.args = args
    self.function = function

  def run(self):
    self.function(*self.args)

  def active_count(self):
    return threading.activeCount()
