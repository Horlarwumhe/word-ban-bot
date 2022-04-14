import random
import string
import os
import sys
letters = string.ascii_letters + string.digits


path = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0,path)

from bot.db import add_banned_word,get_banned_words_list,remove_banned_word,init_db
from bot.config import config
db_name = 'bot_test_data.db'
config.DATABASE_NAME = db_name

def test_insert():
    init_db()
    words = []
    for i in range(5):
        word = ''.join(random.choice(letters) for _ in range(6))
        words.append(word)
    chat_id = -int(''.join(random.choice(string.digits) for _ in range(10)))
    for word in words:
        add_banned_word(chat_id,word)

    banned_words = get_banned_words_list(chat_id)
    banned_words.sort()
    words.sort()

    assert words == banned_words
    os.remove(db_name)

def test_remove():
    init_db()
    words = []
    for i in range(5):
        word = ''.join(random.choice(letters) for _ in range(6))
        words.append(word)
    chat_id = int(''.join(random.choice(string.digits) for _ in range(10)))
    for word in words:
        add_banned_word(chat_id,word)

    to_remove = words[:2] # remove first 2 words
    for word in to_remove:
        remove_banned_word(chat_id,word)

    banned_words = get_banned_words_list(chat_id)
    
    assert len(words) - len(banned_words) == 2
    for word in to_remove:
        assert not word in banned_words

    os.remove(db_name)

def test_remove_all():
    init_db()
    words = []
    for i in range(5):
        # generate five random banned words
        word = ''.join(random.choice(letters) for _ in range(6))
        words.append(word)
    chat_id = int(''.join(random.choice(string.digits) for _ in range(10)))
    for word in words:
        add_banned_word(chat_id,word)

    for word in words:
        remove_banned_word(chat_id,word)

    banned_words = get_banned_words_list(chat_id)

    assert len(banned_words) == 0
    os.remove(db_name)





