-- Schema for content.
CREATE SCHEMA IF NOT EXISTS content;

CREATE TYPE person_role AS ENUM (
    'actor',
    'director',
    'writer'
);

CREATE TABLE IF NOT EXISTS content.movies (
    movie_id        uuid        PRIMARY KEY,
    movie_title     text        NOT NULL,
    movie_desc      text,
    movie_rating    decimal(2, 1),
    UNIQUE (movie_title, movie_desc, movie_rating)
);

CREATE TABLE IF NOT EXISTS content.people (
    person_id       uuid        PRIMARY KEY,
    full_name       text        NOT NULL,
    birthday        date,
    UNIQUE (full_name, birthday)
);

CREATE TABLE IF NOT EXISTS content.movie_people (
    movie_people_id uuid        PRIMARY KEY,
    movie_id        uuid        NOT NULL,
    person_id       uuid        NOT NULL,
    person_role     person_role,
    UNIQUE (movie_id, person_id, person_role)
);

CREATE TABLE IF NOT EXISTS content.genres (
    genre_id        uuid        PRIMARY KEY,
    genre_name      text        UNIQUE NOT NULL,
    genre_desc      text
);

CREATE TABLE IF NOT EXISTS content.movie_genres (
    movie_genres_id uuid        PRIMARY KEY,
    movie_id        uuid        NOT NULL,
    genre_id        uuid        NOT NULL,
    UNIQUE (movie_id, genre_id)
);

ALTER TABLE content.movie_people
        ADD FOREIGN KEY (movie_id) REFERENCES content.movies(movie_id);

ALTER TABLE content.movie_people
        ADD FOREIGN KEY (person_id) REFERENCES content.people(person_id);

ALTER TABLE content.movie_genres
        ADD FOREIGN KEY (movie_id) REFERENCES content.movies(movie_id);

ALTER TABLE content.movie_genres
        ADD FOREIGN KEY (genre_id) REFERENCES content.genres(genre_id);

CREATE INDEX ON content.movies(movie_title);

CREATE INDEX ON content.people(full_name);

