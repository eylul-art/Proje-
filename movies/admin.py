from django.contrib import admin
from .models import Movie, Favorite, Comment, Genre

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_date')

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie')
    
admin.site.register(Genre)
admin.site.register(Comment)