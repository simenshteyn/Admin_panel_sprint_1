from django.shortcuts import render

from rest_framework.viewsets import ModelViewSet

from movies.models import Movies
from movies.serializers import MoviesSerializer


class MoviesViewSet(ModelViewSet):
    queryset = Movies.objects.all()[:5]
    serializer_class = MoviesSerializer
