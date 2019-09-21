import logging
from tornado.log import LogFormatter as TornadoLogFormatter

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

if len(logger.handlers) == 0:
    handler = logging.StreamHandler()
    formatter = TornadoLogFormatter()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    