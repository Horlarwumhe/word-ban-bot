import logging
from logging.handlers import TimedRotatingFileHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger('bot')
stream = TimedRotatingFileHandler("logs/bot.log",
                                  when="D",
                                  encoding="utf-8")
stream.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(name)s %(asctime)s:%(levelname)s: %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S %p')
stream.setFormatter(formatter)
logger.addHandler(stream)

error_log = TimedRotatingFileHandler("logs/bot.error.log",
                                  when="D",
                                  encoding="utf-8")
error_log.setLevel(logging.ERROR)
error_log.setFormatter(formatter)
logger.addHandler(error_log)
logger.setLevel(logging.DEBUG)