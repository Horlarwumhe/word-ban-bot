
Documentation for configuration values used by the bot
This should be in config.json file in the root folder. see [config.json.tmpl]
(/config.json.tmpl)

BOT_TOKEN os.environ.get("BOT_TOKEN")

DATABASE_NAME
name of the bot database. 'botdata.db'


USER_WARNED_TIME
**300** 5 minutes 
time user is warned before being  banned


DELETE_MESSAGE_TIME 
**60** 1 minute
time to delete bot and user messages in seconds



DELETE_MESSAGE_LONG_TIME
**60** 1 minutes
time to delete bot and user messages in seconds, but longer than DELETE_MESSAGE_TIME


DELETE_MESSAGE_SHORT_TIME
**60 * 5** 5 minutes
time to delete bot and user messages in seconds, but shorter than DELETE_MESSAGE_LONG_TIME