import sqlite3

import logging
import time
from functools import wraps

import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor


def logger_init():
    """Start logging for debug and measure performance."""
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
    """Decorator @timed prints execution time for given function."""
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
def main(sqlite_conn: sqlite3.Connection, pg_conn: _connection):

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
        def load_movie_genres(self, chunk_size=250):
            curs = self.__connection.cursor()
            query = curs.execute("""SELECT title, genre
                                       FROM movies
                                      ORDER BY title
                                 """)
            while (dirty_movie_genres := query.fetchmany(chunk_size)):
                movie_genres_list = []
                for movie_genre in dirty_movie_genres:
                    movies = (movie_genre[0],
                              tuple(movie_genre[1].split(', '),)
                              )
                    for movie in movies[1]:
                        movie_genres_list.append(tuple([movies[0], movie]))
                yield movie_genres_list
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

        @timed
        def save_movie_genres(self, data):
            curs = self.__connection.cursor()
            args = ','.join(curs.mogrify("(%s, %s)",
                                         item).decode() for item in data)
            try:
                curs.execute(f"""CREATE TABLE IF NOT EXISTS content.mg_tmp (
                                     movie_title    text,
                                     genre_name     text,
                                     UNIQUE (movie_title, genre_name)
                                 )
                              """)
                curs.execute(f"""INSERT INTO content.mg_tmp
                                 VALUES {args}
                                     ON CONFLICT DO NOTHING
                              """)
                curs.execute(f"""INSERT INTO content.movie_genres(movie_id,
                                                                  genre_id)
                                 SELECT m.movie_id, g.genre_id
                                   FROM content.mg_tmp AS t
                                   JOIN content.genres AS g
                                     ON g.genre_name = t.genre_name
                                   JOIN content.movies AS m
                                     ON m.movie_title = t.movie_title
                                  ORDER BY m.movie_title
                                     ON CONFLICT DO NOTHING
                              """)
                curs.execute(f"""DROP TABLE content.mg_tmp""")
            except Exception as e:
                logger.debug(f'Error {e}')
            finally:
                curs.close()

        @timed
        def save_movie_people(self, data):
            curs = self.__connection.cursor()
            args = ','.join(curs.mogrify("(%s, %s, %s)",
                                         item).decode() for item in data)
            try:
                curs.execute(f"""CREATE TABLE IF NOT EXISTS content.mp_tmp (
                                     person_name    text,
                                     movie_title    text,
                                     person_role    content.person_role,
                                     UNIQUE (movie_title,
                                             person_name,
                                             person_role)
                                 )
                              """)
                curs.execute(f"""INSERT INTO content.mp_tmp
                                 VALUES {args}
                                     ON CONFLICT DO NOTHING
                              """)
                curs.execute(f"""INSERT INTO 
                                        content.movie_people(
                                            movie_id,                      
                                            person_id,
                                            person_role)
                                 SELECT m.movie_id, p.person_id, t.person_role
                                   FROM content.mp_tmp AS t
                                   JOIN content.people AS p
                                     ON p.full_name = t.person_name
                                   JOIN content.movies AS m
                                     ON m.movie_title = t.movie_title
                                  ORDER BY m.movie_title
                                     ON CONFLICT DO NOTHING
                              """)
                curs.execute(f"""DROP TABLE content.mp_tmp""")
            except Exception as e:
                logger.debug(f'Error {e}')
            finally:
                curs.close()


    class DatabaseMigrator:
        def __init__(self, loader: SQLiteLoader, saver: PostgresSaver):
            self.__loader = loader
            self.__saver = saver

        def __save_people(self):
            for actor in (actors := self.__loader.load_actors()):
                self.__saver.save_people(actor)
            for director in (directors := self.__loader.load_directors()):
                self.__saver.save_people(director)
            for writer in (writers := self.__loader.load_writers()):
                self.__saver.save_people(writer)

        def __save_genres(self):
            self.__saver.save_genres(genres := self.__loader.load_genres())

        def __save_movies(self):
            for movie in (movies := self.__loader.load_movies()):
                self.__saver.save_movies(movie)

        def __save_movie_genres(self):
            for movie_genre in (movie_genres := self.__loader.load_movie_genres()):
                self.__saver.save_movie_genres(movie_genre)

        def __save_movie_people(self):
            for director in (directors := self.__loader.load_movie_directors()):
                self.__saver.save_movie_people(director)
            for actor in (actors := self.__loader.load_movie_actors()):
                self.__saver.save_movie_people(actor)
            for writer in (writers := self.__loader.load_movie_writers()):
                self.__saver.save_movie_people(writer)

        def migrate(self):
            try:
                self.__save_people()
                self.__save_genres()
                self.__save_movies()
                self.__save_movie_genres()
                self.__save_movie_people()
            except Exception as e:
                logger.debug(f'Migration error {e}')


    loader = SQLiteLoader(sqlite_conn)
    saver = PostgresSaver(pg_conn)
    migrator = DatabaseMigrator(loader, saver)
    migrator.migrate()


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