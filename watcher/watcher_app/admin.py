from django.contrib import admin
from .models import Film, Review, ReviewLike, ReviewReply, Favorite, Follow, UserStats, SearchLog

admin.site.register(Film)
admin.site.register(Review)
admin.site.register(ReviewLike)
admin.site.register(ReviewReply)
admin.site.register(Favorite)
admin.site.register(Follow)
admin.site.register(UserStats)
admin.site.register(SearchLog)
