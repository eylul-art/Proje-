from django.contrib import admin
from .models import User, Genre, Movie, Review, CommentInteraction, FavoriteMovie, Follow

admin.site.register(User)
admin.site.register(Genre)
admin.site.register(Movie)
admin.site.register(Review)
admin.site.register(CommentInteraction)
admin.site.register(FavoriteMovie)
admin.site.register(Follow)
