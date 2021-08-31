import uuid

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.
class Movies(models.Model):
    movie_id = models.UUIDField(_('movie uuid'),
                                primary_key=True,
                                default=uuid.uuid4,
                                editable=False,
                                unique=True)
    movie_title = models.TextField(_('movie title'))
    movie_desc = models.TextField(_('movie desc'),
                                  blank=True,
                                  )
    movie_rating = models.DecimalField(_('rating'),
                                   max_digits=2,
                                   decimal_places=1,
                                   validators=[MinValueValidator(0),
                                               MaxValueValidator(10)],
                                   blank=True)
    created_at = models.DateTimeField(_('created at'),
                                      auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'),
                                      auto_now=True,
                                      blank=True)

    class Meta:
        verbose_name = _('movie')
        verbose_name_plural = _('movies')
        db_table = 'content"."movies'
