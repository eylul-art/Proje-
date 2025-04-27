from django.core.management.base import BaseCommand
from movies.models import Movie
import requests
from django.conf import settings

class Command(BaseCommand):
    help = 'Popüler filmleri TMDB API’den çekip veritabanına kaydeder.'

    def handle(self, *args, **kwargs):
        api_key = settings.TMDB_API_KEY
        url = f"https://api.themoviedb.org/3/movie/popular?api_key={api_key}&language=tr-TR"

        response = requests.get(url)
        if response.status_code != 200:
            self.stdout.write(self.style.ERROR("❌ API isteği başarısız oldu"))
            return

        movies = response.json().get('results', [])
        for data in movies:
            movie, created = Movie.objects.update_or_create(
                tmdb_id=data['id'],
                defaults={
                    'title': data.get('title'),
                    'overview': data.get('overview'),
                    'release_date': data.get('release_date') or None,
                    'poster_url': f"https://image.tmdb.org/t/p/w500{data.get('poster_path')}" if data.get('poster_path') else None,
                    'popularity': data.get('popularity', 0),
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ Eklendi: {movie.title}"))
            else:
                self.stdout.write(self.style.WARNING(f"📝 Güncellendi: {movie.title}"))
