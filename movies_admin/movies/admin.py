from django.contrib import admin

from .models import Movies, People, Genres, MoviePeople, MovieGenres

class MovieGenresInline(admin.TabularInline):
    model = MovieGenres
    extra = 0
    show_change_link = True


class MoviePeopleInline(admin.TabularInline):
    model = MoviePeople
    extra = 0
    show_change_link = True

@admin.register(Genres)
class GenresAdmin(admin.ModelAdmin):
    search_fields = ['genre_name']
    ordering = ['genre_name']
    list_display = ['genre_name']


@admin.register(People)
class PeopleAdmin(admin.ModelAdmin):
    search_fields = ['full_name']
    ordering = ['full_name']
    inlines = [MoviePeopleInline]





@admin.register(Movies)
class MoviesAdmin(admin.ModelAdmin):
    list_display = ['movie_title', 'movie_rating']
    search_fields = ['movie_title']
    ordering = ['movie_title', 'movie_rating']
    inlines = [MovieGenresInline, MoviePeopleInline]