from django.contrib import admin

from .models import Movies, People, Genres, MoviePeople, MovieGenres


admin.site.register(People)
admin.site.register(Genres)


class MovieGenresInline(admin.StackedInline):
    model = MovieGenres


class MoviePeopleInline(admin.StackedInline):
    model = MoviePeople


@admin.register(Movies)
class MoviesAdmin(admin.ModelAdmin):
    inlines = [MovieGenresInline, MoviePeopleInline]