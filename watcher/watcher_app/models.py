from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

# Kullanıcı Modeli
class User(AbstractUser):
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    favorite_genres = models.ManyToManyField('Genre', blank=True, related_name='users')
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',  # Change this to avoid clash
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions_set',  # Change this to avoid clash
        blank=True,
    )

# Film Türü Modeli
class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name

# Film Modeli
class Movie(models.Model):
    title = models.CharField(max_length=255)
    director = models.CharField(max_length=255, blank=True, null=True)
    release_date = models.DateField(blank=True, null=True)
    genres = models.ManyToManyField(Genre, related_name='movies')
    description = models.TextField(blank=True, null=True)
    poster = models.ImageField(upload_to='movie_posters/', blank=True, null=True)

    def __str__(self):
        return self.title

# Film Yorum ve Puanlama Modeli
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)  # Geçici çözüm
    text = models.TextField()
    score = models.PositiveIntegerField()  # 1-10 arasında puan
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'movie')  # Kullanıcı bir filme sadece bir yorum/puan bırakabilir

    def __str__(self):
        return f"{self.user.username} - {self.movie.title}"
    
# Yorum Beğenme ve Yanıt Modeli
class CommentInteraction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='interactions')
    liked = models.BooleanField(default=False)
    reply = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

# Favori Filmler Modeli
class FavoriteMovie(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'movie')

# Kullanıcı Takip Modeli
class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('follower', 'following')