from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from movies.models import Movies, Genres, People


class GenresSerializer(serializers.RelatedField):
    def to_representation(self, value):
        return value.genre_name

    class Meta:
        model = Genres


# class ActorsSerializer(serializers.RelatedField):
#     def to_representation(self, value):
#         return value.full_name
#
#     class Meta:
#         model = People


class MoviesSerializer(ModelSerializer):
    id = serializers.UUIDField(source='movie_id')
    title = serializers.CharField(source='movie_title')
    description = serializers.CharField(source='movie_desc')
    creation_date = serializers.DateTimeField(format='%Y-%m-%d',
                                              source='created_at')
    rating = serializers.FloatField(source='movie_rating')
    genres = GenresSerializer(source='movie_genres', read_only=True, many=True)
    #actors = ActorsSerializer(source='movie_people', read_only=True, many=True)

    class Meta:
        model = Movies
        fields = ['id',
                  'title',
                  'description',
                  'creation_date',
                  'rating',
                  'genres',
                  'actors',
                  'directors',
                  'writers',
                  ]

    # def get_actors(self, instance):
    #     actors_instances = instance.movie_people.filter(person_role="actor")
    #     return ActorSerializer(actors_instances, many=True).data


