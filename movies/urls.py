from django.urls import path
from .views import movie_detail, toggle_favorite, movie_list

urlpatterns = [
    path('<int:movie_id>/', movie_detail, name='movie_detail'),
    path('<int:movie_id>/favorite/', toggle_favorite, name='toggle_favorite'),
    path('', movie_list, name='movie_list'),
]
