import requests
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Movie, Favorite, Comment, Genre
from .forms import CommentForm
from account_app.models import UserProfile
from django.contrib import messages

# 🎬 FILM DETAY
def movie_detail(request, movie_id):
    movie = Movie.objects.filter(tmdb_id=movie_id).first()
    id=int(movie_id)

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

    # 🌟 Ortalama puanı hesapla
    average_rating = None
    all_averages = [comment.average_rating() for comment in comments if comment.average_rating() is not None]
    if all_averages:
        average_rating = round(sum(all_averages) / len(all_averages), 2)

    if request.method == 'POST':
        if request.user.is_authenticated:
            existing_comment = Comment.objects.filter(user=request.user, movie=movie).first()
            if existing_comment:
                # 🌟 Hata mesajı gösterelim
                messages.error(request, "Bu filme zaten yorum yaptın!")
                return redirect('movie_detail', movie_id=movie.tmdb_id)

            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.user = request.user
                comment.movie = movie
                comment.save()
                messages.success(request, "Yorumun başarıyla eklendi!")  # İstersen başarı mesajı da
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
        "form": form,
        "average_rating": average_rating,
    })


# 🎞 KEŞFET SAYFASI (şimdilik TMDB'den direkt, sonra genre tabanlı filtreleme ekleyebiliriz)
def movie_list(request):
    selected_genre = request.GET.get('genre_id')
    genres = Genre.objects.all()

    movies = Movie.objects.all().prefetch_related('genres')

    if selected_genre:
        selected_genre = int(selected_genre)
        movies = movies.filter(genres__tmdb_id=selected_genre)

    for movie in movies:
        comments = movie.comments.all()
        if comments:
            all_averages = [comment.average_rating() for comment in comments if comment.average_rating() is not None]
            if all_averages:
                movie.average_rating = round(sum(all_averages) / len(all_averages), 2)
            else:
                movie.average_rating = None
        else:
            movie.average_rating = None


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

# searchbar
def search_movies(request):
    query = request.GET.get('q', '').strip()
    movies = Movie.objects.filter(title__icontains=query) if query else []

    # Eğer kendi veritabanımızda film yoksa TMDB'den çekelim
    if query and not movies.exists():
        api_key = settings.TMDB_API_KEY
        url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={query}&language=tr-TR"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            tmdb_movies = data.get('results', [])
            movies = []

            for movie_data in tmdb_movies:
                # Eğer istersen burada database'e kaydedebilirsin
                movie = Movie(
                    tmdb_id=movie_data["id"],
                    title=movie_data.get("title", "Bilinmeyen"),
                    overview=movie_data.get("overview", "Açıklama yok."),
                    release_date=movie_data.get("release_date") or None,
                    poster_url=f"https://image.tmdb.org/t/p/w500{movie_data.get('poster_path', '')}" if movie_data.get('poster_path') else "",
                )
                movies.append(movie)
                # movie.save()  # istersen database'e kaydet!

    return render(request, 'movies/searchbar.html', {
        'movies': movies,
        'query': query
    })

