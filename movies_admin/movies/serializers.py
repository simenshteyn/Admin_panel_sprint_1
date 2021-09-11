from rest_framework.serializers import ModelSerializer

from movies.models import Movies


class MoviesSerializer(ModelSerializer):
    class Meta:
        model = Movies
        fields = '__all__'
