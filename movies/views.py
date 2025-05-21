import requests
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST
from django.http import JsonResponse, HttpResponseBadRequest
from .models import Movie, Favorite, Comment, Genre
from .forms import CommentForm
from account_app.models import UserProfile
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

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
                messages.success(request, "Yorumun başarıyla eklendi!")  
                return redirect('movie_detail', movie_id=movie.tmdb_id)
        else:
            return redirect('account_login')
    else:
        form = CommentForm()

    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, movie=movie).exists()
        
    has_commented = Comment.objects.filter(movie=movie, user=request.user).exists() if request.user.is_authenticated else False


    return render(request, "movies/movie_page.html", {
        "movie": movie,
        "is_favorite": is_favorite,
        "comments": comments,
        "form": form,
        "average_rating": average_rating,
        "has_commented": has_commented,
    })


# KEŞFET SAYFASI (şimdilik TMDB'den direkt, sonra genre tabanlı filtreleme ekleyebiliriz)
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


# PROFİL
@login_required
def profile_view(request):
    favorites = Favorite.objects.filter(user=request.user)
    return render(request, 'account_app/profile.html', {'favorites': favorites})

#  FAVORİ EKLE / ÇIKAR
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

from datetime import datetime

@require_GET
def load_more_movies(request):
    page = int(request.GET.get("page", 1))
    genre_id = request.GET.get("genre_id")

    api_key = settings.TMDB_API_KEY
    url = f"https://api.themoviedb.org/3/discover/movie?api_key={api_key}&language=tr-TR&page={page}"
    if genre_id:
        url += f"&with_genres={genre_id}"

    response = requests.get(url)
    if response.status_code != 200:
        return JsonResponse({'error': 'API hatası'}, status=500)

    data = response.json()
    movies_data = []

    for movie_data in data.get('results', []):
        try:
            movie, _ = Movie.objects.get_or_create(
                tmdb_id=movie_data["id"],
                defaults={
                    'title': movie_data.get("title", "Bilinmeyen"),
                    'overview': movie_data.get("overview", ""),
                    'release_date': movie_data.get("release_date") or None,
                    'poster_url': f"https://image.tmdb.org/t/p/w500{movie_data.get('poster_path', '')}"
                    if movie_data.get('poster_path') else "",
                }
            )
        except Exception as e:
            print(f"Film oluşturulurken hata: {e}")
            continue

        release_date = movie.release_date
        if isinstance(release_date, str):
            release_date_str = release_date
        elif release_date:
            release_date_str = release_date.strftime('%Y-%m-%d')
        else:
            release_date_str = ''

        comments = movie.comments.all()
        all_averages = [c.average_rating() for c in comments if c.average_rating() is not None]
        avg_rating = round(sum(all_averages) / len(all_averages), 1) if all_averages else None

        movies_data.append({
            'id': movie.tmdb_id,
            'title': movie.title,
            'poster_url': movie.poster_url,
            'release_date': release_date_str,
            'like_count': movie.favorites.count(),
            'average_rating': avg_rating,
        })

    return JsonResponse({'movies': movies_data})
@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user == comment.user:
        comment.delete()
        messages.success(request, "Yorumunuz silindi.")
    else:
        messages.error(request, "Bu yorumu silmeye yetkiniz yok.")

    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
@require_POST
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    text = request.POST.get("text")
    acting = request.POST.get("acting")
    story = request.POST.get("story")
    cinematography = request.POST.get("cinematography")

    if text:
        comment.text = text
    if acting: comment.acting = acting
    if story: comment.story = story
    if cinematography: comment.cinematography = cinematography

    comment.edited = True
    comment.save()
    messages.success(request, "Yorum başarıyla güncellendi.")
    return redirect("movie_detail", movie_id=comment.movie.tmdb_id)

@require_POST
@login_required
def like_comment(request, comment_id):
    if request.headers.get('x-requested-with') != 'XMLHttpRequest':
        return HttpResponseBadRequest("Geçersiz istek.")

    comment = get_object_or_404(Comment, id=comment_id)
    user = request.user

    if user in comment.likes.all():
        comment.likes.remove(user)
    else:
        comment.likes.add(user)
        comment.dislikes.remove(user)

    return JsonResponse({
        'likes': comment.likes.count(),
        'dislikes': comment.dislikes.count()
    })

@require_POST
@login_required
def dislike_comment(request, comment_id):
    if request.headers.get('x-requested-with') != 'XMLHttpRequest':
        return HttpResponseBadRequest("Geçersiz istek.")

    comment = get_object_or_404(Comment, id=comment_id)
    user = request.user

    if user in comment.dislikes.all():
        comment.dislikes.remove(user)
    else:
        comment.dislikes.add(user)
        comment.likes.remove(user)

    return JsonResponse({
        'likes': comment.likes.count(),
        'dislikes': comment.dislikes.count()
    })
