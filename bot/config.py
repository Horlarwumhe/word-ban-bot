
import os

# BOT_TOKEN should not be put here. 
# Put it in environment
BOT_TOKEN = os.environ.get("BOT_TOKEN")
DATABASE_NAME = 'botdata.db'
USER_WARNED_TIME = 60*5