import logging
import os
import sqlite3 as sqlite
import time

from telegram import Update
from telegram.ext import CallbackContext
from telegram.message import Message
from telegram.chatmember import ChatMember
from telegram.chat import Chat

from bot.db import (add_banned_word, get_banned_words_list, get_chat_members, remove_banned_word, remove_chat_member)
from bot.utils import (chat_admin_only, check_banned_words, check_admin_names,
                       list_admin_names, log_chat_member, log_command,
                       sanitize_word, special_command)
from bot.config import config
import bot.messages as M

logger = logging.getLogger('bot')


def exception_handler(update: Update, context: CallbackContext):
    logger.exception(context.error or "Error")


def my_chat_member(update: Update, context: CallbackContext):
    chat_member = update.my_chat_member
    status = chat_member.new_chat_member.status
    if chat_member.chat.type == "private":
        # user block or unblock
        return
    if status == "member":
        text = "For the bot to function in this chat, make the bot admin of this chat"
        # the return message instance is not needed here
        post_message(chat_member.chat.id,
                     text,
                     context,
                     delete_time=config.DELETE_MESSAGE_SHORT_TIME)
    elif status == 'administrator':
        logger.info("Bot is now admin in the chat %s", chat_member.chat.title)


@log_chat_member
def new_chat_member(update: Update, context: CallbackContext) -> None:
    chat_member = update.chat_member
    # user = chat_member.new_chat_member.user
    status = chat_member.new_chat_member.status
    # chat_id = chat_member.chat.id
    if status != 'member':
        return
    # add_member(chat_id,user.id)
    check_user_details(chat_member.chat,chat_member.new_chat_member.user,context)
    


# /start /help
@log_command
@chat_admin_only
def start(update: Update, context: CallbackContext):
    message = update.message
    text = M.COMMAND_START_MESSAGE
    if message.chat.type == 'private':
        delete_time = None
    else:
        delete_time = config.DELETE_MESSAGE_TIME
    reply_message(message, text, context, delete_time=delete_time)


@log_command
@chat_admin_only
@special_command
def add_word(update: Update, context: CallbackContext):
    message = update.message
    args = context.args
    if message.chat.type == 'private':
        chat_link = args.pop()
        chat_id = context.bot.get_chat(chat_link).id
        delete_time = None

    else:
        chat_id = message.chat.id
        delete_time = config.DELETE_MESSAGE_TIME
    try:
        word = args[0]
    except IndexError:
        text = M.ADD_WORD_USAGE
        reply_message(message, text, context, delete_time=delete_time)
    else:
        banned_words = get_banned_words_list(chat_id)
        c = 0
        words = map(sanitize_word, args)
        for word in words:
            if word in banned_words:
                # already in the banned words
                continue
            add_banned_word(chat_id, word)
            c += 1
        if c == 1:
            # one word added
            text = M.WORD_ADDED_MESSAGE.format(word=word)
        elif c > 1:
            # more than one
            text = M.BANNED_WORDS_MESSAGE.format(word="New %s words " % c)
            # text = f"New {c} words added to the list"
        else:
            text = M.WORD_EXISTS_MESSAGE.format(word=word)
        reply_message(message, text, context, delete_time=delete_time)


#/remove <word>
@log_command
@chat_admin_only
@special_command
def remove_word(update: Update, context: CallbackContext):
    message = update.message
    args = context.args
    if message.chat.type == 'private':
        chat_link = args.pop()
        chat_id = context.bot.get_chat(chat_link).id
        delete_time = None
    else:
        delete_time = config.DELETE_MESSAGE_TIME
        chat_id = message.chat.id
    try:
        word = args[0]
    except IndexError:
        text = M.REMOVE_WORD_USAGE
    else:
        words = map(sanitize_word, args)
        c = 0
        for word in words:
            remove_banned_word(chat_id, word)
            c += 1
        word = word if c == 1 else f"New {c} words"
        text = M.WORD_REMOVED_MESSAGE.format(word=word)
    reply_message(message, text, context, delete_time=delete_time)


#/list
@log_command
@special_command
def list_word(update: Update, context: CallbackContext):
    message = update.message
    user_id = message.from_user.id
    args = context.args
    if message.chat.type == 'private':
        chat_link = args.pop()
        chat_id = context.bot.get_chat(chat_link).id
        delete_time = None
    else:
        delete_time = config.DELETE_MESSAGE_SHORT_TIME
        chat_id = message.chat.id
    banned_words = get_banned_words_list(chat_id)
    words = "Banned word list\n\n" + '\n'.join(banned_words)
    reply_message(message, words, context, delete_time=delete_time)


def check_warned_user(context: CallbackContext):
    user_id = context.job.context['user_id']
    chat_id = context.job.context['chat_id']

    user_member = context.bot.get_chat_member(chat_id=chat_id, user_id=user_id)
    if user_member and user_member.status != "member":
        # The user is no more member
        return
    banned = False
    if user_member:
        fname = check_banned_words(user_member.user.first_name or '', chat_id)
        lname = check_banned_words(user_member.user.last_name or '', chat_id)
        username = check_banned_words(user_member.user.first_name or '',
                                      chat_id)
        if lname or fname or username:
            # user details in banned words
            # user has been warned
            #reason = "Name is banned word list"
            context.bot.ban_chat_member(chat_id, user_id)
            banned = True
        else:
            admins = list_admin_names(context.bot, chat_id)
            fname = check_admin_names(admins, user_member.user.first_name
                                      or '')
            lname = check_admin_names(admins, user_member.user.last_name or '')
            if lname or fname:
                context.bot.ban_chat_member(chat_id, user_id)
                banned = True
        if banned:
            logger.info("User is banned '%s'\n ", user_member.user.first_name)


def check_user_details(chat:Chat,users,context:CallbackContext):

    if not isinstance(users,list):
        users = [users]
    warned = False
    chat_id = chat.id
    admin_names = list_admin_names(context.bot, chat_id)
    for user in users:
        username = user.username or ''
        first_name = user.first_name or ''
        last_name = user.last_name or ''
        reason = []
        if username:
            mention = "@{}".format(username)
        else:
            mention = '<a href="tg://user?id={id}"> {first_name} </a>'.format(
                id=user.id, first_name=user.first_name)
        similar_name = check_admin_names(admin_names, first_name)
        if not similar_name:
            similar_name = check_admin_names(admin_names, last_name)
        warning_time = str(config.USER_WARNED_TIME // 60)
        if similar_name:
            reason.append("user name similar to chat admins name")
            warned = True
            text = M.SIMILAR_NAME_MESSAGE.format(user=mention,
                                                admin=similar_name,
                                                time=warning_time)
            post_message(chat_id,
                        text,
                        context,
                        delete_time=config.USER_WARNED_TIME,
                        parse_mode="HTML")

        # check for banned words
        for details in (first_name, last_name, username):
            word = check_banned_words(details, chat_id)
            if word:
                reason.append("user name in banned word list")
                warned = True
                text = M.BANNED_WORDS_MESSAGE.format(user=mention,
                                                    time=warning_time,
                                                    word=word)
                post_message(chat_id,
                            text,
                            context,
                            delete_time=config.USER_WARNED_TIME,
                            parse_mode="HTML")
                break

        if warned:
            log = ("User details violate the chat policy in chat %s\n"
                "first_name = %s \n"
                "Reason: %s\n")
            logger.info(log, chat.title, user.first_name,
                        '\n'.join(reason))
            context.job_queue.run_once(check_warned_user,
                                    config.USER_WARNED_TIME,
                                    context={
                                        "chat_id": chat_id,
                                        'user_id': user.id
                                    },
                                    name=str(user.id))
        else:
            log = ("User %s is verified. no banned words in user details.\n"
                "user details not similar to the chat admins details.\n")
            logger.info(log, user.first_name)


def delete_message(context: CallbackContext):
    # delete a message after some minutes
    message = context.job.context
    message.delete()


def reply_message(message: Message,
                  text: str,
                  context: CallbackContext,
                  delete_time=None,
                  **kwargs):
    '''
    reply a message and delete both message and the reply
    '''
    reply = message.reply_text(text, **kwargs)
    if delete_time is not None:
        # delete the original message
        log = ("scheduling 2 background job\n"
               "function = bot.handlers.delete_message\n"
               "time = %s seconds\n")
        logger.info(log, delete_time)
        context.job_queue.run_once(delete_message,
                                   delete_time,
                                   context=message,
                                   name=str(message.from_user.id))

        # delete the bot reply
        context.job_queue.run_once(delete_message,
                                   delete_time,
                                   context=reply,
                                   name=str(message.from_user.id))


def post_message(chat_id,
                 text,
                 context: CallbackContext,
                 delete_time=None,
                 **kwargs):
    message = context.bot.send_message(chat_id, text, **kwargs)
    if delete_time is not None:
        context.job_queue.run_once(delete_message,
                                   delete_time,
                                   context=message,
                                   name=str(chat_id))
    return message
