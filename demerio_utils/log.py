import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

steam_handler = logging.StreamHandler()
steam_handler.setLevel(logging.DEBUG)

logger.addHandler(steam_handler)
