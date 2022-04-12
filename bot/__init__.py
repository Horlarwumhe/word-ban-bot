import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger("bot")

# logger = logging.getLogger('bot')
# stream = logging.StreamHandler()
# stream.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(asctime)s:%(levelname)s: %(message)s',
#                               datefmt='%d/%m/%Y %H:%M:%S %p')
# stream.setFormatter(formatter)
# logger.addHandler(stream)
# logger.setLevel(logging.DEBUG)
