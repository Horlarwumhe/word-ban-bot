import os

# BOT_TOKEN should not be put here.
# Put it in environment
BOT_TOKEN = os.environ.get("BOT_TOKEN")
DATABASE_NAME = 'botdata.db'

# time user is warned before being
USER_WARNED_TIME = 60 * 5 

# time to delete bot commands and bot messages
DELETE_MESSAGE_TIME = 60 * 1 

# time to delete bot commands and bot messages, but longer than DELETE_MESSAGE_TIME
DELETE_MESSAGE_LONG_TIME = 60 * 10

# time to delete bot commands and bot messages, but shorter than DELETE_MESSAGE_LONG_TIME
DELETE_MESSAGE_SHORT_TIME = 60 * 5 