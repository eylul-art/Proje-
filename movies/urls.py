from django.urls import path
from .views import movie_detail, toggle_favorite, movie_list, load_more_movies, delete_comment, edit_comment, like_comment, dislike_comment

urlpatterns = [
    path('<int:movie_id>/', movie_detail, name='movie_detail'),
    path('<int:movie_id>/favorite/', toggle_favorite, name='toggle_favorite'),
    path('', movie_list, name='movie_list'),
    path('api/load-more-movies/', load_more_movies, name='load_more_movies'),
    path('comment/delete/<int:comment_id>/', delete_comment, name='delete_comment'),
    path('yorum-duzenle/<int:comment_id>/', edit_comment, name='edit_comment'),
    path('comment/<int:comment_id>/like/', like_comment, name='like_comment'),
    path('comment/<int:comment_id>/dislike/', dislike_comment, name='dislike_comment'),

]
