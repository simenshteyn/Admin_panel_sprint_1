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
            query = curs.execute("""SELECT name
                                       FROM actors
                                      ORDER BY name
                                 """)
            while (actors_list := query.fetchmany(chunk_size)):
                yield actors_list
            curs.close()

        @timed
        def load_writers(self, chunk_size=500):
            curs = self.__connection.cursor()
            query = curs.execute("""SELECT name
                                       FROM writers
                                      ORDER BY name
                                 """)
            while (writers_list := query.fetchmany(chunk_size)):
                yield writers_list
            curs.close()

        @timed
        def load_directors(self, chunk_size=500):
            curs = self.__connection.cursor()
            query = curs.execute("""SELECT director
                                       FROM movies
                                      WHERE NOT (director='N/A')
                                      ORDER BY director
                                 """)
            while (dirty_directors_list := query.fetchmany(chunk_size)):
                directors_list = []
                for director_tuple in dirty_directors_list:
                    for director in director_tuple[0].split(', '):
                        if director.endswith('(co-director)'):
                            director = director[:-13]
                        directors_list.append(tuple([director]))
                yield directors_list
            curs.close()

        @timed
        def load_movies(self, chunk_size=100):
            curs = self.__connection.cursor()
            query = curs.execute("""SELECT title,
                                      CASE WHEN plot = 'N/A' THEN NULL
                                           ELSE plot
                                       END AS plot, 
                                      CASE WHEN imdb_rating = 'N/A' THEN NULL
                                           ELSE imdb_rating
                                       END AS imdb_rating 
                                       FROM movies
                                      ORDER BY title
                                 """)
            while (movies_list := query.fetchmany(chunk_size)):
                yield movies_list
            curs.close()

        @timed
        def load_genres(self):
            curs = self.__connection.cursor()
            query = curs.execute("""SELECT DISTINCT genre
                                       FROM movies
                                      ORDER BY genre
                                 """)
            dirty_genres_list = query.fetchall()
            result_set = set()
            for genre_tuple in dirty_genres_list:
                for genre in (genre_tuple[0].split(', ')):
                    result_set.add(genre)

            genre_list = []
            for genre in result_set:
                genre_list.append(tuple([genre]))
            curs.close()
            return genre_list

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
            curs.close()

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
            curs.close()

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
            curs.close()

        @timed
        def load_movie_writers(self, chunk_size=500):
            curs = self.__connection.cursor()
            query = curs.execute("""SELECT w.name, m.title
                                      FROM movies AS m
                                      JOIN writers AS w
                                        ON m.writer = w.id
                                           OR m.writers LIKE '%'||w.id||'%'
                                     WHERE NOT (w.name = 'N/A')
                                     ORDER BY w.name
                                 """)
            while (movie_writers := query.fetchmany(chunk_size)):
                writers_list = []
                for movie_writer in movie_writers:
                    writer = movie_writer + ('writer',)
                    writers_list.append(writer)
                yield writers_list
            curs.close()


    class PostgresSaver:
        def __init__(self, pg_conn: _connection):
            self.__connection = pg_conn

        @timed
        def save_people(self, data):
            curs = self.__connection.cursor()
            args = ','.join(curs.mogrify("(%s)",
                                         item).decode() for item in data)
            try:
                curs.execute(f"""INSERT INTO content.people (full_name)
                                 VALUES {args}
                                     ON CONFLICT DO NOTHING
                              """)
            except Exception as e:
                logger.debug(f'Error {e}')
            finally:
                curs.close()

        @timed
        def save_genres(self, data):
            curs = self.__connection.cursor()
            args = ','.join(curs.mogrify("(%s)",
                                         item).decode() for item in data)
            try:
                curs.execute(f"""INSERT INTO content.genres (genre_name)
                                 VALUES {args}
                                     ON CONFLICT DO NOTHING                           
                              """)
            except Exception as e:
                logger.debug(f'Error {e}')
            finally:
                curs.close()

        @timed
        def save_movies(self, data):
            curs = self.__connection.cursor()
            args = ','.join(curs.mogrify("(%s, %s, %s)",
                                         item).decode() for item in data)
            try:
                curs.execute(f"""INSERT INTO content.movies (movie_title,
                                                             movie_desc,
                                                             movie_rating)
                                 VALUES {args}
                                     ON CONFLICT DO NOTHING
                              """)
            except Exception as e:
                logger.debug(f'Error {e}')
            finally:
                curs.close()


        def save_movie_genres(self):
            pass

        def save_movie_people(self):
            pass

    loader = SQLiteLoader(sqlite_conn)
    saver = PostgresSaver(pg_conn)

    def save_people(loader: SQLiteLoader, saver: PostgresSaver):
        for actor in (actors := loader.load_actors()):
            saver.save_people(actor)
        for director in (directors := loader.load_directors()):
            saver.save_people(director)
        for writer in (writers := loader.load_writers()):
            saver.save_people(writer)
    save_people(loader, saver)

    def save_genres(loader: SQLiteLoader, saver: PostgresSaver):
        saver.save_genres(genres := loader.load_genres())
    save_genres(loader, saver)

    def save_movies(loader: SQLiteLoader, saver: PostgresSaver):
        for movie in (movies := loader.load_movies()):
            saver.save_movies(movie)
    save_movies(loader, saver)




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
