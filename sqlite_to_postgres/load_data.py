import sqlite3

import logging
import time
from functools import wraps

import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor


def main(sqlite_conn: sqlite3.Connection, pg_conn: _connection):

    def logger_init():
        logger = logging.getLogger(__name__)
        logger.setLevel('DEBUG')
        handler = logging.StreamHandler()
        log_format = '%(asctime)s %(levelname)s -- %(message)s'
        formatter = logging.Formatter(log_format)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    logger = logger_init()

    def timed(func):
        """Prints execution time for given function."""

        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, *kwargs)
            end = time.time()
            logger.debug('{} ran in {}s'.format(func.__name__,
                                                round(end - start, 2)))
            return result
        return wrapper

    @timed
    def slow_fun():
        print('yoooo')

    slow_fun()



def load_from_sqlite(connection: sqlite3.Connection, pg_conn: _connection):
    """Основной метод загрузки данных из SQLite в Postgres"""
    #postgres_saver = PostgresSaver(pg_conn)
    #sqlite_loader = SQLiteLoader(connection)
    #data = sqlite_loader.load_movies()
    #postgres_saver.save_all_data(data)
    pass


if __name__ == '__main__':

    dsl = {'dbname': 'movies',
           'user': 'postgres',
           'password': 'yandex01',
           'host': '127.0.0.1',
           'port': 5432
           }

    with sqlite3.connect('db.sqlite') as sqlite_conn,\
         psycopg2.connect(**dsl, cursor_factory=DictCursor) as pg_conn:
             main(sqlite_conn, pg_conn)
