import sqlite3


class Database():
    def __init__(self, db_name):
        try:
            conn = sqlite3.connect(
                "sqlite/{0}.db".format(db_name),
                check_same_thread=False)
            self.conn = conn
        except sqlite3.Error as e:
            print("[DB] Unable to create db for '{0}'".format(db_name))
            print(e)
