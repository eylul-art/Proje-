import requests
from django.conf import settings
from movies.models import Movie, Genre
from django.db.models import Count
from django.shortcuts import render

def get_tmdb_data_and_store(endpoint, params=None, count=8):
    if params is None:
        params = {}

    params["api_key"] = settings.TMDB_API_KEY
    params["language"] = "tr-TR"
    try:
        response = requests.get(endpoint, params=params)
        if response.status_code == 200:
            data = response.json().get('results', [])[:count]
            movies = []
            for item in data:
                tmdb_id = item['id']
                movie, created = Movie.objects.get_or_create(
                    tmdb_id=tmdb_id,
                    defaults={
                        'title': item.get('title', 'Başlıksız'),
                        'overview': item.get('overview', ''),
                        'release_date': item.get('release_date') or '2000-01-01',
                        'poster_url': f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}" if item.get('poster_path') else '',
                        'popularity': item.get('popularity', 0)
                    }
                )
                movies.append(movie)
            return movies
    except Exception:
        pass
    return []


def home(request):
    # Günün filmi
    random_movie = Movie.objects.order_by('?').first()

    # En çok favorilenmiş filmler
    top_favorited = (
        Movie.objects.annotate(num_fav=Count('favorites'))
        .order_by('-num_fav')[:8]
    )

    # TMDB verileri: veritabanına kaydediyoruz
    all_time_popular = get_tmdb_data_and_store("https://api.themoviedb.org/3/discover/movie?sort_by=vote_average.desc&vote_count.gte=10000")
    trending = get_tmdb_data_and_store("https://api.themoviedb.org/3/trending/movie/week", count=4)
    new_releases = get_tmdb_data_and_store("https://api.themoviedb.org/3/movie/now_playing", count=4)

    context = {
        'random_movie': random_movie,
        'top_favorited': top_favorited,
        'all_time_popular': all_time_popular,
        'trending': trending,
        'new_releases': new_releases,
    }
    return render(request, 'home/home.html', context)
