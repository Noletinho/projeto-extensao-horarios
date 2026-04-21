import pymysql
import pymysql.cursors
import os
from urllib.parse import urlparse


class _Conn:
    def __init__(self, conn):
        self._c = conn

    def cursor(self):
        return self._c.cursor()

    def commit(self):
        self._c.commit()

    def rollback(self):
        self._c.rollback()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, *_):
        if exc_type:
            self._c.rollback()
        self._c.close()
        return False


def conectar():
    url = urlparse(os.environ['DATABASE_URL'])
    conn = pymysql.connect(
        host=url.hostname,
        user=url.username,
        password=url.password or '',
        database=url.path.lstrip('/'),
        port=url.port or 3306,
        cursorclass=pymysql.cursors.DictCursor,
        charset='utf8mb4',
    )
    return _Conn(conn)
