import functools
import logging
import re
import Levenshtein as lev

from telegram import Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext

from bot.db import get_banned_words_list, add_chat_member
import bot.messages as M

logger = logging.getLogger('bot')
str_clean_pattern = re.compile('[^a-z]+')

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
    name = ''.join(filter(str.isalpha, name)).lower()
    banned_words = get_banned_words_list(chat_id)
    for word in banned_words:
        if word in name:
            found = word
            break
    return found


def check_admin_names(admin_names, name):
    # remove no alphabetic character ,eg, _
    if not name:
        return
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


def list_admin_usernames(bot, chat_id):
    admins = bot.get_chat_administrators(chat_id)
    usernames = [u.user.username for u in admins if u.user.username]
    return usernames


def lower_case_letters(text):
    return str_clean_pattern.sub('', text.lower())


def check_admin_usernames(admins, username):
    if not username:
        return None
    username = lower_case_letters(username)
    for name in admins:
        name = lower_case_letters(name)
        ratio = lev.ratio(name, username)
        if ratio > 0.8:
            return name
    return None


# decorators
def log_command(func):

    @functools.wraps(func)
    def wrapper(update: Update, context: CallbackContext):
        message = update.message
        command = message.text.split()[0]
        user = message.from_user
        log = ("Bot command %s from\n"
               " user_id = %s\n"
               " username = %s\n"
               "first_name = %s\n")
        logger.info(log, command, user.id, user.username, user.first_name)
        add_chat_member(message.chat_id, user.id)
        return func(update, context)

    return wrapper


def log_chat_member(func):

    @functools.wraps(func)
    def wrapper(update: Update, context: CallbackContext):
        chat = update.chat_member.chat
        user = update.chat_member.new_chat_member.user
        status = update.chat_member.new_chat_member.status
        log = ("New chat member status in chat %s\n"
               "status = %s\n"
               "user_id = %s\n"
               "username = %s\n"
               "first_name = %s\n")
        logger.info(log, chat.title, status, user.id, user.username,
                    user.first_name)
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
            log = ("Ignoring command %s from %s in chat %s\n"
                   " Reason: Only admin can use this command\n")
            logger.info(log, command, user.first_name, message.chat.title)
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
        log = ("Ignoring command %s from %s\n"
               " Reason: Reason: Private chat only command\n")
        logger.info(log, command, user.first_name)

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
                message.reply_text(M.COMMAND_START_MESSAGE)
                return

        return func(update, context)

    return wrapper


def sanitize_word(word):
    '''
    sanitize word before adding it to database.
    currently, the word is only convert to lowercase
    '''
    return word.lower()
