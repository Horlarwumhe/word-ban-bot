import logging
from logging.handlers import TimedRotatingFileHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger('bot')
stream = TimedRotatingFileHandler("logs/bot.log",
                                  when="D",
                                  encoding="utf-8",
                                  errors="ignore")
stream.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(name)s %(asctime)s:%(levelname)s: %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S %p')
stream.setFormatter(formatter)
logger.addHandler(stream)
logger.setLevel(logging.DEBUG)
