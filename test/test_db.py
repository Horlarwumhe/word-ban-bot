import random
import string
import os
import sys
import time
letters = string.ascii_letters + string.digits


path = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0,path)

from bot.db import add_banned_word, add_chat_member,get_banned_words_list, get_chat_members, get_chat_members_by_last_check,remove_banned_word,init_db, remove_chat_member, update_chat_member_last_check
from bot.config import config
db_name = 'bot_test_data.db'
config.DATABASE_NAME = db_name


class Test:

    def __enter__(self):
        init_db()

    def __exit__(self,*args):
        os.remove(db_name)

def test_insert():
    with Test():
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

def test_remove():
    
    with Test():
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


def test_remove_all():
    with Test():
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

def test_add_member():
    with Test():
        users = [ 64823232,7832323,3465232,28978672 , 3534334]
        chat_id = 4343323234323

        for user in users:
            add_chat_member(chat_id,user)
            update_chat_member_last_check(chat_id,user)
        

        rows = get_chat_members(chat_id)
        assert len(users) == len(rows)
        
        users_id = users[:2]
        for user in users_id:
            remove_chat_member(chat_id,user)

        rows = get_chat_members(chat_id)
        assert len(users) - 2  == len(rows)
    
        time_frame = 60 * 1
        rows = get_chat_members_by_last_check(chat_id,5,time_frame)
        assert len(rows) == 0
        time.sleep(2)
        time_frame = 60
        rows = get_chat_members_by_last_check(chat_id,5,time_frame)
        assert len(rows) == 0

        time.sleep(2)
        time_frame = 2
        rows = get_chat_members_by_last_check(chat_id,5,time_frame)
        assert len(rows) == 3