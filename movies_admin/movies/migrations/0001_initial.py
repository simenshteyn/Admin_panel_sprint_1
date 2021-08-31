# Generated by Django 3.2.6 on 2021-08-31 10:04

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Genres',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='updated at')),
                ('genre_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='genre uuid')),
                ('genre_name', models.TextField(verbose_name='genre name')),
                ('genre_desc', models.TextField(blank=True, null=True, verbose_name='genre description')),
            ],
            options={
                'verbose_name': 'genre',
                'verbose_name_plural': 'genres',
                'db_table': 'content"."genres',
            },
        ),
        migrations.CreateModel(
            name='Movies',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='updated at')),
                ('movie_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='movie uuid')),
                ('movie_title', models.TextField(verbose_name='movie title')),
                ('movie_desc', models.TextField(blank=True, null=True, verbose_name='movie desc')),
                ('movie_rating', models.DecimalField(blank=True, decimal_places=1, max_digits=2, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)], verbose_name='rating')),
            ],
            options={
                'verbose_name': 'movie',
                'verbose_name_plural': 'movies',
                'db_table': 'content"."movies',
            },
        ),
        migrations.CreateModel(
            name='People',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='updated at')),
                ('person_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='movie uuid')),
                ('full_name', models.TextField(verbose_name='full name')),
                ('person_desc', models.TextField(blank=True, null=True, verbose_name='person description')),
                ('birthday', models.DateField(blank=True, null=True, verbose_name='birthday')),
            ],
            options={
                'verbose_name': 'person',
                'verbose_name_plural': 'people',
                'db_table': 'content"."people',
            },
        ),
        migrations.CreateModel(
            name='MoviePeople',
            fields=[
                ('movie_people_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='movie people uuid')),
                ('person_role', models.CharField(choices=[('actor', 'actor'), ('director', 'director'), ('writer', 'writer')], max_length=10)),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='movies.movies')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='movies.people')),
            ],
            options={
                'verbose_name': 'movie person',
                'verbose_name_plural': 'movie people',
                'db_table': 'content"."movie_people',
            },
        ),
        migrations.CreateModel(
            name='MovieGenres',
            fields=[
                ('movie_genres_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='movie genres uuid')),
                ('genre', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='movies.genres')),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='movies.movies')),
            ],
            options={
                'verbose_name': 'movie genre',
                'verbose_name_plural': 'movie genres',
                'db_table': 'content"."movie_genres',
            },
        ),
    ]
