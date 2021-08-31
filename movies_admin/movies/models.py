import uuid

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(
        _('created at'), auto_now_add=True, null=True, blank=True
    )
    updated_at = models.DateTimeField(
        _('updated at'), auto_now=True, null=True, blank=True
    )

    class Meta:
        abstract = True


class Movies(TimeStampedModel, models.Model):
    movie_id = models.UUIDField(
        _('movie uuid'), primary_key=True, default=uuid.uuid4,
        editable=False, unique=True
    )
    movie_title = models.TextField(_('movie title'), blank=False)
    movie_desc = models.TextField(_('movie desc'), blank=True, null=True)
    movie_rating = models.DecimalField(
        _('rating'), max_digits=2, decimal_places=1,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        blank=True, null=True
    )

    def __str__(self):
        return self.movie_title

    class Meta:
        verbose_name = _('movie')
        verbose_name_plural = _('movies')
        db_table = 'content"."movies'


class People(TimeStampedModel, models.Model):
    person_id = models.UUIDField(
        _('movie uuid'), primary_key=True, default=uuid.uuid4,
        editable=False, unique=True
    )
    full_name = models.TextField(_('full name'), blank=False)
    person_desc = models.TextField(
        _('person description'), blank=True, null=True
    )
    birthday = models.DateField(_('birthday'), blank=True, null=True)

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = _('person')
        verbose_name_plural = _('people')
        db_table = 'content"."people'


class Genres(TimeStampedModel, models.Model):
    genre_id = models.UUIDField(
        _('genre uuid'), primary_key=True, default=uuid.uuid4,
        editable=False, unique=True
    )
    genre_name = models.TextField(_('genre name'), blank=False)
    genre_desc = models.TextField(
        _('genre description'), blank=True, null=True
    )

    def __str__(self):
        return self.genre_name

    class Meta:
        verbose_name = _('genre')
        verbose_name_plural = _('genres')
        db_table = 'content"."genres'


class MoviePeople(models.Model):

    class PersonRole(models.TextChoices):
        ACTOR = 'actor', _('actor')
        DIRECTOR = 'director', _('director')
        WRITER = 'writer', _('writer')

    movie_people_id = models.UUIDField(
        _('movie people uuid'), primary_key=True, default=uuid.uuid4,
        editable=False, unique=True
    )
    movie = models.ForeignKey(Movies, on_delete=models.CASCADE)
    person = models.ForeignKey(People, on_delete=models.CASCADE)
    person_role = models.CharField(max_length=10, choices=PersonRole.choices)

    def __str__(self):
        return f'{self.movie} ({self.person}, {self.person_role})'

    class Meta:
        verbose_name = _('movie person')
        verbose_name_plural = _('movie people')
        db_table = 'content"."movie_people'


class MovieGenres(models.Model):
    movie_genres_id = models.UUIDField(
        _('movie genres uuid'), primary_key=True, default=uuid.uuid4,
        editable=False, unique=True
    )
    movie = models.ForeignKey(Movies, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genres, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.movie} ({self.genre})'

    class Meta:
        verbose_name = _('movie genre')
        verbose_name_plural = _('movie genres')
        db_table = 'content"."movie_genres'