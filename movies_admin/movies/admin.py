from django.contrib import admin

#Register your models here.
from .models import Movies, People, Genres, MoviePeople, MovieGenres

admin.site.register(Movies)
admin.site.register(People)
admin.site.register(Genres)
admin.site.register(MoviePeople)
admin.site.register(MovieGenres)