
Documentation for configuration values used by the bot
This should be in config.json file in the root folder. see [config.json.tmpl](config.json.tmpl)

BOT_TOKEN
bot token 
this cam also be put in the environment

DATABASE_NAME
name of the bot database. 'botdata.db'


USER_WARNED_TIME
**300** // 300 seconds(5 minutes)
time user is warned before being  banned


DELETE_MESSAGE_TIME 
**60** // 1 minute
time to delete bot and user messages in seconds




**600** // 600 seconds(10 minutes)
time to delete bot and user messages in seconds, but longer than DELETE_MESSAGE_TIME


DELETE_MESSAGE_SHORT_TIME
**300** // 300 seconds(5 minutes)
time to delete bot and user messages in seconds, but shorter than DELETE_MESSAGE_LONG_TIME