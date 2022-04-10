import sqlite3 as sqlite

from bot.db import DB
from bot.utils import (BANNED_WORDS_MESSAGE, check_admin_names,
                       check_banned_words, list_admin_names)
from telegram import Update
from telegram.ext import CallbackContext, Updater


def my_chat_member(update: Update, context: CallbackContext):
    chat_member = update.my_chat_member
    status = chat_member.new_chat_member.status
    if chat_member.chat.type == "private":
        # user block or unblock
        return
    if status == "member":
        text = "For the bot to function in this chat, make the bot admin of this chat"
        context.bot.send_message(chat_member.chat.id, text)


def new_chat_member(update: Update, context: CallbackContext) -> None:
    chat_member = update.chat_member
    status = chat_member.new_chat_member.status
    if status != 'member':
        return
    warned = False
    username = chat_member.new_chat_member.user.username or ''
    first_name = chat_member.new_chat_member.user.first_name or ''
    last_name = chat_member.new_chat_member.user.last_name or ''
    user = chat_member.new_chat_member.user
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
        warned = True
        message = (
            'Hello {user}, Your first name/last name {first_name}-{last_name}\n'
            'is similar to one of the admins of this chat ({similar_name})\n'
            "kindly change the name to something else.\n"
            "You will be removed after 5 mins if you dont change your name")
        message = message.format(user=name,
                                 first_name=first_name,
                                 last_name=last_name,
                                 similar_name=similar_name)
        context.bot.send_message(chat_member.chat.id,
                                 message,
                                 parse_mode="HTML")

    # check for banned words
    for details in (first_name,last_name,username):
        word = check_banned_words(details)
        if word:
            warned = True
            message = BANNED_WORDS_MESSAGE.format(user=name,
                                              name=details,
                                              word=word)
            context.bot.send_message(chat_member.chat.id,
                                 message,
                                 parse_mode="HTML")
            break

    if warned:
        context.job_queue.run_once(check_warned_user,
                                   20,
                                   context={
                                       "chat_id": chat_member.chat.id,
                                       'user_id': user.id
                                   },
                                   name=str(user.id))

# /start /help
def start(update:Update,context:CallbackContext):
    message = update.message
    text = """/add <word> to add new word
/remove <word> to remove word
/list to list all banned words
    """
    message.reply_text(text)

def add_word(update: Update, context: CallbackContext):
    message = update.message
    try:
        word = context.args[0]
    except IndexError:
        text = 'Add new word\nUsage: /add <word>'
        message.reply_text(text)
        return

    with DB() as db:
        c = 0
        for word in context.args:
            c += 1
            try:
                db.execute(
                    '''
                insert into banned_words(word) values(?);
                    ''', (word, ))
            except sqlite.IntegrityError:
                pass
    if c == 1:
        message.reply_text(f'{word} added to the list')
    elif c > 1:
        message.reply_text(f"New {c} words added to the list")


#/remove <word>
def remove_word(update: Update, context: CallbackContext):
    message = update.message
    try:
        word = context.args[0]
    except IndexError:
        text = 'Remove word\nUsage: /remove <word>'
        message.reply_text(text)
        return
    with DB() as db:
        db.execute(
            '''
            delete from banned_words where word=?;
                ''', (word, ))
        message.reply_text(f'{word} removed from the list')


#/list
def list_word(update: Update, context: CallbackContext):
    with DB() as db:
        cur = db.execute(
            'select word from banned_words where id > 0').fetchall()
        words = "Banned word list\n"+'\n'.join(row['word'] for row in cur)
        update.message.reply_text(words)


def check_warned_user(context: CallbackContext):
    user_id = context.job.context['user_id']
    chat_id = context.job.context['chat_id']

    user_member = context.bot.get_chat_member(chat_id=chat_id, user_id=user_id)
    if user_member and user_member.status != "member":
        # The user is no more member
        return
    if user_member:
        fname = check_banned_words(user_member.user.first_name or '')
        lname = check_banned_words(user_member.user.last_name or '')
        username = check_banned_words(user_member.user.first_name or '')
        if lname or fname or username:
            # user details in banned words
            # user has been warned
            context.bot.ban_chat_member(chat_id, user_id)
            return
        else:
            admins = list_admin_names(context.bot, chat_id)
            fname = check_admin_names(admins, user_member.user.first_name
                                      or '')
            lname = check_admin_names(admins, user_member.user.last_name or '')
            if lname or fname:
                context.bot.ban_chat_member(chat_id, user_id)
                return
