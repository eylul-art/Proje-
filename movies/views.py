import requests
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Movie
from account_app.models import UserProfile

def movie_detail(request, movie_id):
    """Belirtilen ID'ye sahip filmi detaylı gösterir veya TMDB API'den çekip kaydeder"""
    
    # Veritabanında bu TMDB ID'ye sahip film var mı?
    movie = Movie.objects.filter(tmdb_id=movie_id).first()

    if not movie:
        # Film yoksa TMDB API'den çekelim
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

    # Kullanıcının bu filmi favoriye ekleyip eklemediğini kontrol et
    is_favorite = False
    if request.user.is_authenticated:
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        is_favorite = profile.favorite_movies.filter(tmdb_id=movie.tmdb_id).exists()

    return render(request, "movies/movie_page.html", {"movie": movie, "is_favorite": is_favorite})


@login_required
def toggle_favorite(request, movie_id):
    """Kullanıcının bir filmi favorilerine ekleyip çıkarmasını yönetir"""

    print(f"Favori ekleme isteği alındı. Film ID: {movie_id}")  # Debug için

    # Film veritabanında var mı? Eğer yoksa TMDB API'den çekip kaydet
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
        else:
            return JsonResponse({"error": "Film TMDB API'de bulunamadı!"}, status=404)

    # Kullanıcının profilini al
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    # Kullanıcı favorilere eklediyse çıkar, eklemediyse ekle
    if profile.favorite_movies.filter(tmdb_id=movie.tmdb_id).exists():
        profile.favorite_movies.remove(movie)
        status = "removed"
    else:
        profile.favorite_movies.add(movie)
        status = "added"

    return JsonResponse({"status": status})
