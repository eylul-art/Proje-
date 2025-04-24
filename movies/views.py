import requests
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Movie, Favorite, Comment, Genre
from .forms import CommentForm
from account_app.models import UserProfile

# 🎬 FILM DETAY
def movie_detail(request, movie_id):
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

            # 🎯 Türleri kaydet
            for genre_data in data.get("genres", []):
                genre, _ = Genre.objects.get_or_create(
                    tmdb_id=genre_data["id"],
                    defaults={"name": genre_data["name"]}
                )
                movie.genres.add(genre)
        else:
            return render(request, "404.html", status=404)

    comments = movie.comments.all().order_by('-created_at')

    if request.method == 'POST':
        if request.user.is_authenticated:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.user = request.user
                comment.movie = movie
                comment.save()
                return redirect('movie_detail', movie_id=movie.tmdb_id)
        else:
            return redirect('account_login')
    else:
        form = CommentForm()

    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, movie=movie).exists()

    return render(request, "movies/movie_page.html", {
        "movie": movie,
        "is_favorite": is_favorite,
        "comments": comments,
        "form": form
    })

# 🎞 KEŞFET SAYFASI (şimdilik TMDB'den direkt, sonra genre tabanlı filtreleme ekleyebiliriz)
def movie_list(request):
    selected_genre = request.GET.get('genre_id')
    genres = Genre.objects.all()

    movies = Movie.objects.all().prefetch_related('genres')

    if selected_genre:
        selected_genre = int(selected_genre)
        print("🌸 Seçilen tür TMDB ID:", selected_genre)
        movies = movies.filter(genres__tmdb_id=selected_genre)
        print("🎬 Filtrelenmiş film sayısı:", movies.count())

    context = {
        'movies': movies,
        'genres': genres,
        'selected_genre': selected_genre,
    }
    return render(request, 'movies/movie_list.html', context)

# ❤️ PROFİL
@login_required
def profile_view(request):
    favorites = Favorite.objects.filter(user=request.user)
    return render(request, 'account_app/profile.html', {'favorites': favorites})

# 💖 FAVORİ EKLE / ÇIKAR
def toggle_favorite(request, movie_id):
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

            for genre_data in data.get("genres", []):
                genre, _ = Genre.objects.get_or_create(
                    tmdb_id=genre_data["id"],
                    defaults={"name": genre_data["name"]}
                )
                movie.genres.add(genre)
        else:
            return redirect('error_page')

    favorite, created = Favorite.objects.get_or_create(user=request.user, movie=movie)

    if not created:
        favorite.delete()
    return redirect('movie_detail', movie_id=movie.tmdb_id)
