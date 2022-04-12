import sqlite3 as sqlite
from bot import config


class DB:

    def __init__(self, name=None):
        if not name:
            self.name = config.DATABASE_NAME
        else:
            self.name = name
        self.con = sqlite.connect(self.name)
        self.con.row_factory = sqlite.Row
        self.cursor = self.con.cursor()

    def __enter__(self):
        return self.cursor

    def __exit__(self, *args):
        self.con.commit()
        self.con.close()


def get_db(name=None):
    if not name:
        name = 'botdata.db'

    con = sqlite.connect(name)
    con.row_factory = sqlite.Row
    return con


def init_db():
    with DB() as db:
        db.execute('''
  create table if not exists
   banned_words(id integer primary key,word text, chat_id integer);
   ''')


def remove_banned_word(chat_id, word):
    with DB() as db:
        db.execute(
            '''
                delete from banned_words where word=? and chat_id=?;
                ''', (word, chat_id))


def get_banned_words_list(chat_id):
    with DB() as db:
        rows = db.execute('select word from banned_words where chat_id=?',
                          (chat_id, )).fetchall()
    return [row['word'] for row in rows]


def add_banned_word(chat_id, word):
    with DB() as db:
        db.execute(
            '''
                insert into banned_words(word,chat_id) values(?,?);
                ''', (word, chat_id))


def get_banned_word(chat_id, word):
    with DB() as db:
        row = db.execute(
            'select word from banned_words where chat_id=?  and word=?',
            (chat_id, word)).fetchone()
    if row:
        return row['word']
    return
