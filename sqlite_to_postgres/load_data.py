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

    class SQLiteLoader:
        def __init__(self, connection: sqlite3.Connection):
            self.__connection = connection

        @timed
        def load_actors(self, chunk_size=500):
            curs = self.__connection.cursor()
            result = curs.execute("""SELECT name
                                       FROM actors
                                      ORDER BY name
                                  """)
            while (actors_list := result.fetchmany(chunk_size)):
                yield actors_list

        @timed
        def load_writers(self, chunk_size=500):
            curs = self.__connection.cursor()
            result = curs.execute("""SELECT name
                                       FROM writers
                                      ORDER BY name
                                  """)
            while (writers_list := result.fetchmany(chunk_size)):
                yield writers_list

        @timed
        def load_directors(self, chunk_size=500):
            curs = self.__connection.cursor()
            result = curs.execute("""SELECT director
                                       FROM movies
                                      WHERE NOT (director='N/A')
                                      ORDER BY director
                                  """)
            while (directors_list := result.fetchmany(chunk_size)):
                yield directors_list

        @timed
        def load_movies(self, chunk_size=100):
            curs = self.__connection.cursor()
            result = curs.execute("""SELECT title, plot, imdb_rating
                                       FROM movies
                                      ORDER BY title
                                  """)
            while (movies_list := result.fetchmany(chunk_size)):
                yield movies_list

        @timed
        def load_genres(self):
            curs = self.__connection.cursor()
            result = curs.execute("""SELECT DISTINCT genre
                                       FROM movies
                                      ORDER BY genre
                                  """)
            dirty_genres_list = result.fetchall()
            result_set = set()
            for genre_tuple in dirty_genres_list:
                for genre in (genre_tuple[0].split(', ')):
                    result_set.add(genre)
            while result_set:
                yield tuple(result_set)

        @timed
        def load_movie_genres(self):
            curs = self.__connection.cursor()
            query = curs.execute("""SELECT title, genre
                                       FROM movies
                                      ORDER BY title
                                  """)
            while (result := query.fetchone()):
                result = (result[0], tuple(result[1].split(', '), ))
                yield result

        @timed
        def load_movie_actors(self, chunk_size=500):
            curs = self.__connection.cursor()
            query = curs.execute("""SELECT a.name, m.title
                                      FROM movie_actors
                                      JOIN movies AS m
                                        ON m.id = movie_actors.movie_id
                                      JOIN actors AS a
                                        ON a.id = movie_actors.actor_id
                                     WHERE NOT (a.name = 'N/A')
                                     ORDER BY a.name
                                  """)
            while (movie_actors := query.fetchmany(chunk_size)):
                actors_list = []
                for movie in movie_actors:
                    actor = movie + ('actor',)
                    actors_list.append(actor)
                yield actors_list

        @timed
        def load_movie_directors(self, chunk_size=500):
            curs = self.__connection.cursor()
            query = curs.execute("""SELECT director, title
                                      FROM movies
                                     WHERE NOT (director = 'N/A')
                                     ORDER BY director
                                  """)
            while (movie_directors := query.fetchmany(chunk_size)):
                directors_list = []
                for movie_director in movie_directors:
                    director = movie_director + ('director',)
                    directors_list.append(director)
                yield directors_list

        @timed
        def load_movie_writers(self, chunk_size=500):
            curs = self.__connection.cursor()
            query = curs.execute("""SELECT w.name, m.title
                                      FROM movies AS m
                                      JOIN writers AS w
                                        ON m.writer = w.id
                                     WHERE NOT (w.name = 'N/A')
                                     ORDER BY w.name
                                  """)
            while (movie_writers := query.fetchmany(chunk_size)):
                writers_list = []
                for movie_writer in movie_writers:
                    writer = movie_writer + ('writer',)
                    writers_list.append(writer)
                yield writers_list




    loader = SQLiteLoader(sqlite_conn)
    # loader.load_actors()
    # loader.load_writers()
    # loader.load_directors()
    # loader.load_movies()
    # loader.load_genres()
    # loader.load_movie_genres()
    # movie_genres = loader.load_movie_genres()
    # for movie_genre in movie_genres:
    #     print(movie_genre)
    movie_writers= loader.load_movie_writers()
    for m in movie_writers:
        print(m)




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
