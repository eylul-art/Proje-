import requests
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import Movie, Favorite
from django.shortcuts import redirect

def movie_detail(request, movie_id):
    """Belirtilen ID'ye sahip filmi detaylı gösterir"""
    movie = Movie.objects.filter(tmdb_id=movie_id).first()

    if not movie:
        api_key = settings.TMDB_API_KEY
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=tr-TR"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            movie = Movie.objects.create(
                tmdb_id=data["id"],
                title=data.get("title", "Bilinmeyen"),
                overview=data.get("overview", "Açıklama bulunamadı."),
                release_date=data.get("release_date", None),
                poster_url=f"https://image.tmdb.org/t/p/w500{data.get('poster_path', '')}"
            )

    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, movie=movie).exists()

    return render(request, "movies/movie_page.html", {"movie": movie, "is_favorite": is_favorite})

@login_required
def toggle_favorite(request, movie_id):
    """Kullanıcı favorilere ekleme veya çıkarma işlemi yapar"""
    movie = get_object_or_404(Movie, tmdb_id=movie_id)
    
    favorite, created = Favorite.objects.get_or_create(user=request.user, movie=movie)

    if not created:
        favorite.delete()

    return redirect('movie_detail', movie_id=movie_id)

