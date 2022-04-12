import logging
import os
import sqlite3 as sqlite

from telegram import Update
from telegram.ext import CallbackContext

from bot.db import (add_banned_word, get_banned_words_list, remove_banned_word)
from bot.utils import (BANNED_WORDS_MESSAGE, chat_admin_only,
                       check_banned_words, check_admin_names, list_admin_names,
                       log_chat_member, log_command, special_command)

logger = logging.getLogger('bot')


def my_chat_member(update: Update, context: CallbackContext):
    chat_member = update.my_chat_member
    status = chat_member.new_chat_member.status
    if chat_member.chat.type == "private":
        # user block or unblock
        return
    if status == "member":
        text = "For the bot to function in this chat, make the bot admin of this chat"
        message = context.bot.send_message(chat_member.chat.id, text)
        context.job_queue.run_once(delete_message, 60 * 10, context=message)
    elif status == 'administrator':
        logger.info("Bot is now admin in the chat %s", chat_member.chat.title)


@log_chat_member
def new_chat_member(update: Update, context: CallbackContext) -> None:
    chat_member = update.chat_member
    user = chat_member.new_chat_member.user
    status = chat_member.new_chat_member.status
    chat_id = chat_member.chat.id
    reason = []
    if status != 'member':
        return
    warned = False
    username = chat_member.new_chat_member.user.username or ''
    first_name = chat_member.new_chat_member.user.first_name or ''
    last_name = chat_member.new_chat_member.user.last_name or ''
    # bot = context.bot.send_message(message,chat_id=chat_member.chat.id)

    if username:
        name = "@{}".format(username)
    else:
        name = '''<a href='tg://user?id={id}'> {first_name} </a>'''.format(
            id=user.id, first_name=user.first_name)
    admin_names = list_admin_names(context.bot, chat_member.chat.id)
    similar_name = check_admin_names(admin_names, first_name)
    if not similar_name:
        similar_name = check_admin_names(admin_names, last_name)
    if similar_name:
        reason.append("user name similar to chat admins name")
        warned = True
        message = (
            'Hello {user}, Your first name/last name {first_name}-{last_name}\n'
            'is similar to one of the admins of this chat ({similar_name})\n'
            "kindly change the name to something else.\n"
            "You will be removed after 5 mins if you dont change your name")
        text = message.format(user=name,
                              first_name=first_name,
                              last_name=last_name,
                              similar_name=similar_name)
        message = context.bot.send_message(chat_member.chat.id,
                                           text,
                                           parse_mode="HTML")
        context.job_queue.run_once(delete_message,
                                   60 * 5,
                                   context=message,
                                   name=str(user.id))

    # check for banned words
    for details in (first_name, last_name, username):
        word = check_banned_words(details, chat_id)
        if word:
            reason.append("user name in banned word list")
            warned = True
            text = BANNED_WORDS_MESSAGE.format(user=name,
                                               name=details,
                                               word=word)
            message = context.bot.send_message(chat_member.chat.id,
                                               text,
                                               parse_mode="HTML")
            context.job_queue.run_once(delete_message,
                                       60 * 5,
                                       context=message,
                                       name=str(user.id))
            break

    if warned:
        logger.info(
            """
        User details violate the chat policy in chat %s
        first_name = %s
        Reason: %s

        """, chat_member.chat.title, user.first_name, '\n'.join(reason))
        t = os.environ.get("USER_WARNED_TIME", 300)
        context.job_queue.run_once(check_warned_user,
                                   int(t),
                                   context={
                                       "chat_id": chat_member.chat.id,
                                       'user_id': user.id
                                   },
                                   name=str(user.id))
    else:
        logger.info(
            '''
User is %s verified. no banned words in user details.
user details not similar to the chat admins details.
''', user.first_name)


# /start /help


@log_command
@chat_admin_only
def start(update: Update, context: CallbackContext):
    message = update.message
    text = """/add <word> to add new word
/remove <word> to remove word
/list to list all banned words
    """
    message = message.reply_text(text)
    if message.chat.type != 'private':
        context.job_queue.run_once(delete_message, 60 * 5, context=message)


@log_command
@chat_admin_only
@special_command
def add_word(update: Update, context: CallbackContext):
    message = update.message
    args = context.args
    user_id = message.from_user.id
    if message.chat.type == 'private':
        chat_link = args.pop()
        chat_id = context.bot.get_chat(chat_link).id

    else:
        chat_id = message.chat.id
        context.job_queue.run_once(delete_message,
                                   60 * 1,
                                   context=message,
                                   name=str(user_id))
    try:
        word = args[0]
    except IndexError:
        text = 'Add new word\nUsage: /add <word>'
        message = message.reply_text(text)
    else:
        banned_words = get_banned_words_list(chat_id)
        c = 0
        for word in args:
            if word in banned_words:
                # already in the banned words
                continue
            add_banned_word(chat_id, word)
            c += 1
    if c == 1:
        # one word added
        message = message.reply_text(f'{word} added to the list')
    elif c > 1:
        # more than one
        message = message.reply_text(f"New {c} words added to the list")
    else:
        message = message.reply_text(f"{word} already exist")

    if message.chat.type != 'private':
        context.job_queue.run_once(delete_message,
                                   60 * 1,
                                   context=message,
                                   name=str(user_id))


#/remove <word>
@log_command
@chat_admin_only
@special_command
def remove_word(update: Update, context: CallbackContext):
    message = update.message
    user_id = message.from_user.id
    args = context.args
    if message.chat.type == 'private':
        chat_link = args.pop()
        chat_id = context.bot.get_chat(chat_link).id
    else:
        context.job_queue.run_once(delete_message,
                                   60 * 1,
                                   context=message,
                                   name=str(user_id))
        chat_id = message.chat.id
    try:
        word = args[0]
    except IndexError:
        text = 'Remove word\nUsage: /remove <word>'
        message = message.reply_text(text)
    else:
        remove_banned_word(chat_id, word)
        message = message.reply_text(f'{word} removed from the list')
    if message.chat.type != "private":
        context.job_queue.run_once(delete_message,
                                   60 * 1,
                                   context=message,
                                   name=str(user_id))


#/list
@log_command
@chat_admin_only
@special_command
def list_word(update: Update, context: CallbackContext):
    message = update.message
    user_id = message.from_user.id
    args = context.args
    if message.chat.type == 'private':
        chat_link = args.pop()
        chat_id = context.bot.get_chat(chat_link).id
    else:
        chat_id = message.chat.id
        context.job_queue.run_once(delete_message,
                                   60 * 1,
                                   context=message,
                                   name=str(user_id))
    banned_words = get_banned_words_list(chat_id)
    words = "Banned word list\n\n" + '\n'.join(banned_words)
    message = update.message.reply_text(words)
    #context.job_queue.run_once(delete_message,30,context=message,name=str(user_id))
    if message.chat.type != 'private':
        context.job_queue.run_once(delete_message,
                                   60 * 10,
                                   context=message,
                                   name=str(user_id))


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
            logger.info("User is banned '%s' ",user_member.user.first_name)


def delete_message(context: CallbackContext):
    # delete a message after some minutes
    message = context.job.context
    message.delete()
