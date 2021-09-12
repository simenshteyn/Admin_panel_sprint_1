from rest_framework import pagination
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from movies.models import Movies
from movies.api.v1.serializers import MoviesSerializer


class CustomPagination(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'prev': self.page.previous_page_number() if self.page.number > 1
            else None,
            'next': self.page.next_page_number()
            if self.page.number < self.page.paginator.num_pages else None,
            'result': data,
        })


class MoviesViewSet(ReadOnlyModelViewSet):
    queryset = Movies.objects.prefetch_related('movie_genres')
    serializer_class = MoviesSerializer
    pagination_class = CustomPagination
