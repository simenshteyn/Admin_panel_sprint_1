from rest_framework.viewsets import ReadOnlyModelViewSet

from movies.models import Movies
from movies.api.v1.serializers import MoviesSerializer


class MoviesViewSet(ReadOnlyModelViewSet):
    queryset = Movies.objects.all().prefetch_related('movie_genres',
                                                     'movie_people')
    serializer_class = MoviesSerializer
