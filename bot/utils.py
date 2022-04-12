import functools
import logging

from telegram import Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext

from bot.db import DB

logger = logging.getLogger('bot')
BANNED_WORDS_MESSAGE = (
    'Hello {user},Your name {name}\n'
    'is among the banned words for this chat\n'
    '{word} is banned in this chat\n'
    "kindly change the name to something else.\n"
    "You will be removed after 5 mins if you dont change your name")


def check_banned_words(name, chat_id):
    found = None
    if not name:
        return
    logger.info("Checking for user name '%s' in the chat banned word list",
                name)
    name = ''.join(filter(str.isalpha, name)).lower()
    with DB() as db:
        cur = db.execute(
            'select word from banned_words where id > 0 and chat_id=?',
            (chat_id, ))
        banned_words = [row['word'].lower() for row in cur]
        for word in banned_words:
            if word in name:
                found = word
                break
    return found


def check_admin_names(admin_names, name):
    # remove no alphabetic character ,eg, _
    if not name:
        return
    logger.info(
        "Checking for similarity between user name '%s' and names of the admins",
        name)
    username = ''.join(filter(str.isalpha, name)).lower()
    for admin in admin_names:
        try:
            fname, lname = map(str.lower, admin.split())
        except ValueError:
            fname = lname = admin.split()[0]
        if fname.lower() in username or lname.lower() in username:
            return admin
    return None


def list_admin_names(bot, chat_id):
    admins = bot.get_chat_administrators(chat_id)
    admins = [
        "%s %s" % (u.user.first_name or '', u.user.last_name or '')
        for u in admins
    ]
    return admins


# decorators
def log_command(func):

    @functools.wraps(func)
    def wrapper(update: Update, context: CallbackContext):
        message = update.message
        command = message.text.split()[0]
        user = message.from_user
        logger.info(
            '''
            Bot command %s from
            user_id = %s
            username = %s
            first_name = %s
            ''', command, user.id, user.username, user.first_name)
        return func(update, context)

    return wrapper


def log_chat_member(func):

    @functools.wraps(func)
    def wrapper(update: Update, context: CallbackContext):
        chat = update.chat_member.chat
        user = update.chat_member.new_chat_member.user
        status = update.chat_member.new_chat_member.status
        logger.info(
            '''
            New chat member status in chat %s
            status = %s
            user_id = %s
            username = %s
            first_name = %s
            ''', chat.title, status, user.id, user.username, user.first_name)
        return func(update, context)

    return wrapper


def chat_admin_only(func):
    '''admin only commands
       if the chat is private, the callback function is called'''

    @functools.wraps(func)
    def wrapper(update: Update, context: CallbackContext):
        chat_type = update.message.chat.type
        if chat_type == 'private':
            return func(update, context)
        message = update.message
        command = message.text.split()[0]
        chat_id = message.chat.id
        admins = [
            admin.user.id
            for admin in context.bot.get_chat_administrators(chat_id)
        ]
        user = message.from_user
        if not user.id in admins:
            logger.info(
                '''
                Ignoring command %s from %s
                Reason: Only admin can use this command
                ''', command, user.first_name)
            return
        else:
            return func(update, context)

    return wrapper


def private_only(func):

    @functools.wraps(func)
    def wrapper(update: Update, context: CallbackContext):
        message = update.message
        user = message.from_user
        chat_type = message.chat.type
        command = message.text.split()[0]
        if chat_type == 'private':
            return func(update, context)

        logger.info(
            '''
                Ignoring command %s from %s
                Reason: Private chat only command
                ''', command, user.first_name)

    return wrapper


#
def special_command(func):
    '''decorator to validate /list /add /remove and other commands
    '''

    @functools.wraps(func)
    def wrapper(update: Update, context: CallbackContext):
        args = context.args
        message = update.message
        cmd = message.text.split()[0]
        user_id = message.from_user.id
        if message.chat.type == "private":
            if len(args) > 0:
                # private chat
                # /list @chatname
                arg = args[-1]
                try:
                    chat = context.bot.get_chat(arg)
                    bot_id = context.bot.get_me().id
                    admins = [
                        admin.user.id for admin in
                        context.bot.get_chat_administrators(chat.id)
                    ]
                except BadRequest as e:
                    logger.info(e)
                    message.reply_text("chat not found")
                    return
                if not user_id in admins or not bot_id in admins:
                    message.reply_text(
                        "You and the bot and need to be admin of %s to use this command"
                        % arg)
                    return
            else:
                message.reply_text(
                    'To use this command in private chat\nspecify target chat @<chatname>'
                )
                return

        return func(update, context)

    return wrapper
