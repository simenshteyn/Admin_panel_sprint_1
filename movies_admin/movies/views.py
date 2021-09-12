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
            'prev': self.page.previous_page_number(),
            'next': self.page.next_page_number(),
            'result': data,
        })

class MoviesViewSet(ReadOnlyModelViewSet):
    queryset = Movies.objects.all() #.prefetch_related('movie_genres',
                                    #                 'movie_people')
    serializer_class = MoviesSerializer
    pagination_class = CustomPagination

