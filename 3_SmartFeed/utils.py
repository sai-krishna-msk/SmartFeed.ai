

import logging

def getLogger( name, level=logging.INFO):
  formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
  logger = logging.getLogger(name)
  handler_console = logging.StreamHandler()
  handler_console.setFormatter(formatter)
  logger.addHandler(handler_console)
  logger.setLevel(level)
  return logger









