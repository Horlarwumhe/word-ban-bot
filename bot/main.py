import logging
import os

from telegram.ext import (CallbackContext, ChatMemberHandler, CommandHandler,
                          Updater)

import bot.handlers as handlers
from bot.config import config
from bot.db import init_db

logger = logging.getLogger('bot')


def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        token = config.BOT_TOKEN
    if not token:
        logger.info("BOT_TOKEN token not set\nexisting....")
        exit(1)

    init_db()
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", handlers.start))
    dispatcher.add_handler(CommandHandler("help", handlers.start))
    dispatcher.add_handler(CommandHandler("list", handlers.list_word))
    dispatcher.add_handler(CommandHandler("add", handlers.add_word))
    dispatcher.add_handler(CommandHandler("remove", handlers.remove_word))
    dispatcher.add_handler(
        ChatMemberHandler(handlers.my_chat_member,
                          ChatMemberHandler.MY_CHAT_MEMBER))
    dispatcher.add_handler(
        ChatMemberHandler(handlers.new_chat_member,
                          ChatMemberHandler.CHAT_MEMBER))

    # Start the Bot
    updater.start_polling(
        allowed_updates=['my_chat_member', 'chat_member', 'message'])

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()
