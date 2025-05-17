from django.db import models
from django.db import models
from django.contrib.auth.models import User

class Genre(models.Model):
    tmdb_id = models.IntegerField(unique=True)  # TMDB API'deki Tür ID'si
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
class Movie(models.Model):
    tmdb_id = models.IntegerField(unique=True)  # TMDB API'deki Film ID'si
    title = models.CharField(max_length=255)
    overview = models.TextField()
    release_date = models.DateField()
    poster_url = models.URLField()
    genres = models.ManyToManyField(Genre, blank=True)  
    popularity = models.FloatField(default=0) 
    
    def total_favorites(self):
        return self.favorites.count() 

    def __str__(self):
        return self.title
    


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="favorites")

    class Meta:
        unique_together = ('user', 'movie')  # Aynı kullanıcı bir filmi sadece bir kez favorilere ekleyebilir

    def __str__(self):
        return f"{self.user.username} - {self.movie.title}"
    
class Comment(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    acting = models.PositiveIntegerField(null=True, blank=True)
    story = models.PositiveIntegerField(null=True, blank=True)
    cinematography = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)
    dislikes = models.ManyToManyField(User, related_name='disliked_comments', blank=True)
  
    class Meta:
        unique_together = ('movie', 'user')

    def average_rating(self):
        if self.acting and self.story and self.cinematography:
            return round((self.acting + self.story + self.cinematography) / 3, 2)
        return None

    def __str__(self):
        return f"{self.user.username} - {self.movie.title}"
