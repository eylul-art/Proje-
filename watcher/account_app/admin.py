from django.contrib import admin
from .models import UserProfile, Post

# Register your models here.

admin.site.register(UserProfile)
admin.site.register(Post)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio')
    filter_horizontal = ('favorite_movies',)  # ManyToManyField için güzel bir UI sağlar

