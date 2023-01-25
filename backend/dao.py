import sqlite3
from contextlib import contextmanager


# Either commit or rollback the transaction
@contextmanager
def ensure(conn):
    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    else:
        conn.commit()


class Database:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

        self.cur = self.conn.cursor()

        self._create()

    def _create(self):
        with ensure(self.conn):
            ...

    def close(self):
        self.conn.close()
