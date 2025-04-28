from django.core.management.base import BaseCommand
from django.conf import settings
from movies.models import Movie, Genre
import requests

class Command(BaseCommand):
    help = 'TMDB API üzerinden popüler filmleri çekip veritabanına kaydeder ve genre ilişkilerini kurar.'

    def handle(self, *args, **kwargs):
        api_key = settings.TMDB_API_KEY
        url = f"https://api.themoviedb.org/3/movie/popular?api_key={api_key}&language=tr-TR&page=1"

        response = requests.get(url)
        if response.status_code != 200:
            self.stdout.write(self.style.ERROR(f"❌ API isteği başarısız oldu. Status code: {response.status_code}"))
            return

        data = response.json()
        movies = data.get('results', [])

        added_count = 0
        updated_count = 0

        for movie_data in movies:
            movie, created = Movie.objects.update_or_create(
                tmdb_id=movie_data['id'],
                defaults={
                    'title': movie_data.get('title'),
                    'overview': movie_data.get('overview', ''),
                    'release_date': movie_data.get('release_date') or None,
                    'poster_url': f"https://image.tmdb.org/t/p/w500{movie_data.get('poster_path')}" if movie_data.get('poster_path') else None,
                    'popularity': movie_data.get('popularity', 0),
                }
            )

            if created:
                added_count += 1
            else:
                updated_count += 1

            # 🎯 Genre ilişkilendirme
            genre_ids = movie_data.get('genre_ids', [])
            movie.genres.clear()  # varsa eski ilişkiyi temizle

            for genre_id in genre_ids:
                genre = Genre.objects.filter(tmdb_id=genre_id).first()
                if genre:
                    movie.genres.add(genre)

            # İstersen movie.save() yapmana gerek yok, ManyToMany değişimlerinde otomatik olur.

        self.stdout.write(self.style.SUCCESS(f"✅ Popüler filmler başarıyla güncellendi."))
        self.stdout.write(self.style.SUCCESS(f"➕ Eklenen film sayısı: {added_count}"))
        self.stdout.write(self.style.SUCCESS(f"📝 Güncellenen film sayısı: {updated_count}"))
