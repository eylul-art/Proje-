import requests
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Movie, Favorite
from account_app.models import UserProfile
from django.shortcuts import redirect

def movie_detail(request, movie_id):
    """Belirtilen ID'ye sahip filmi detaylı gösterir veya TMDB API'den çekip kaydeder"""

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

    return render(request, "movies/movie_page.html", {
        "movie": movie,
        "is_favorite": is_favorite
    })

def movie_list(request):
    api_key = settings.TMDB_API_KEY
    selected_genre = request.GET.get('genre_id')

    # Fetch genres
    genre_url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={api_key}&language=tr-TR"
    genres_response = requests.get(genre_url)
    genres = genres_response.json().get('genres', [])

    # Fetch multiple pages of popular movies
    movies = []
    for page in range(1, 4):  # Fetch page 1, 2, 3 (each has 20 movies)
        movie_url = f"https://api.themoviedb.org/3/movie/popular?api_key={api_key}&language=tr-TR&page={page}"
        response = requests.get(movie_url)
        page_movies = response.json().get('results', [])
        movies.extend(page_movies)

    # Filter by genre
    if selected_genre:
        selected_genre = int(selected_genre)
        movies = [m for m in movies if selected_genre in m['genre_ids']]

    context = {
        'movies': movies,
        'genres': genres,
        'selected_genre': selected_genre,
    }
    return render(request, 'movies/movie_list.html', context)

@login_required
def profile_view(request):
    favorites = Favorite.objects.filter(user=request.user)
    return render(request, 'account_app/profile.html', {'favorites': favorites})

def toggle_favorite(request, movie_id):
    """Kullanıcının bir filmi favorilere eklemesini veya çıkarmasını yönetir"""

    # Film veritabanında var mı?
    movie = Movie.objects.filter(tmdb_id=movie_id).first()

    # Yoksa TMDB API'den çekip veritabanına kaydet
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
            # Film bulunamazsa bir hata sayfasına yönlendirilebilir
            return redirect('error_page')  # veya render(request, 'error.html', ...)

    # Favori verisini kontrol et / oluştur
    favorite, created = Favorite.objects.get_or_create(user=request.user, movie=movie)

    if not created:
        # Zaten varsa kaldır
        favorite.delete()
        status = "removed"
    else:
        # Yoksa ekle
        status = "added"

    # Film detay sayfasına geri dön
    return redirect('movie_detail', movie_id=movie.tmdb_id)
