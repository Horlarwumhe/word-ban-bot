import sqlite3 as sqlite


class DB:
    def __init__(self, name=None):
        if not name:
            self.name = 'botdata.db'
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
   banned_words(id integer primary key,word unique);
   ''')
