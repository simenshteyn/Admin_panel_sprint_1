from rest_framework.viewsets import ReadOnlyModelViewSet

from movies.models import Movies
from movies.api.v1.serializers import MoviesSerializer


class MoviesViewSet(ReadOnlyModelViewSet):
    queryset = Movies.objects.all()
    serializer_class = MoviesSerializer
