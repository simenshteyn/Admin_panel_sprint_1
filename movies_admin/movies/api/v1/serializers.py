from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from movies.models import Movies


class MoviesSerializer(ModelSerializer):
    id = serializers.UUIDField(source='movie_id')
    class Meta:
        model = Movies
        fields = ['id',
                  'movie_title',
                  'movie_desc',
                  'created_at',
                  'movie_rating']