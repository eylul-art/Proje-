from django.contrib import admin
from .models import Admin, UserProfile, Post

# Register your models here.
admin.site.register(Admin)
admin.site.register(UserProfile)
admin.site.register(Post)
