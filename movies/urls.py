from django.urls import path
from .views import movie_detail, toggle_favorite

urlpatterns = [
    path('<int:movie_id>/', movie_detail, name='movie_detail'),
    path('<int:movie_id>/favorite/', toggle_favorite, name='toggle_favorite'),
]
