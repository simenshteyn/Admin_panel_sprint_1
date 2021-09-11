import debug_toolbar
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import SimpleRouter

from movies.views import MoviesViewSet

urlpatterns = [
    path('admin/', admin.site.urls),
    path('__debug__/', include(debug_toolbar.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('api/', include('movies.api.urls')),
    ]
