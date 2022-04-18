import sqlite3 as sqlite
import time
from bot.config import config


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
        sql = (
            "create table if not exists "
            "banned_words(id integer primary key,word text, chat_id integer);")
        db.execute(sql)
        sql = (
            "create table if not exists "
            "members(id integer primary key, chat_id integer, user_id integer,last_checked integer default 0);"
        )
        db.execute(sql)


def remove_banned_word(chat_id, word):
    with DB() as db:
        db.execute("delete from banned_words where word=? and chat_id=?;",
                   (word, chat_id))


def get_banned_words_list(chat_id):
    with DB() as db:
        rows = db.execute("select word from banned_words where chat_id=?",
                          (chat_id, )).fetchall()
    return [row['word'] for row in rows]


def add_banned_word(chat_id, word):
    with DB() as db:
        db.execute("insert into banned_words(word,chat_id) values(?,?);",
                   (word, chat_id))


def get_banned_word(chat_id, word):
    with DB() as db:
        row = db.execute(
            "select word from banned_words where chat_id=?  and word=?",
            (chat_id, word)).fetchone()
    if row:
        return row['word']
    return


def add_chat_member(chat_id, user_id):
    if get_chat_member(chat_id, user_id):
        return False
    with DB() as db:
        db.execute("insert into members(chat_id,user_id) values(?,?)",
                   (chat_id, user_id))
    return True


def get_chat_member(chat_id, user_id):
    with DB() as db:
        row = db.execute("select * from members where chat_id=? and user_id=?",
                         (chat_id, user_id)).fetchone()
        if row:
            return row["chat_id"]


def get_chat_members(chat_id):
    with DB() as db:
        rows = db.execute("select * from members where chat_id=?",
                          (chat_id, )).fetchall()
    return rows


def remove_chat_member(chat_id, user_id):
    with DB() as db:
        db.execute("delete from members where chat_id=? and user_id=?;",
                   (chat_id, user_id))


def get_chat_members_by_last_check(chat_id, limit=1000, time_frame=60 * 5):
    time_frame = int(time_frame)
    # select users with lowest last check limit by N limit
    with DB() as db:
        now = int(time.time())
        sql = ("select * from members where chat_id=? "
               "and ? - last_checked >= ? "
               "order by last_checked limit ?;")
        rows = db.execute(sql, (chat_id, now, time_frame, limit)).fetchall()
    return rows


def update_chat_member_last_check(chat_id, user_id, last_check=None):
    if not last_check:
        now = int(time.time())
    else:
        now = last_check

    with DB() as db:
        db.execute(
            "update  members set last_checked=? where chat_id=? and user_id=?",
            (now, chat_id, user_id))


# def select_chat_members(chat_id):
#     with DB() as db:
#         now = int(time.time())
#         rows = db.execute(
#             "select * from members where chat_id=? order by user_id limit 100",(chat_id,now)
#         ).fetchall()
#     return dict(rows)
