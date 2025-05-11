from django.core.management.base import BaseCommand
import requests
from django.conf import settings
from movies.models import Genre

class Command(BaseCommand):
    help = 'TMDB API\'den tür (genre) verilerini çekip veritabanına kaydeder.'

    def handle(self, *args, **kwargs):
        api_key = settings.TMDB_API_KEY
        url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={api_key}&language=tr-TR"

        response = requests.get(url)
        if response.status_code != 200:
            self.stdout.write(self.style.ERROR("TMDB'den veri alınamadı."))
            return

        data = response.json()
        genres = data.get('genres', [])

        for genre_data in genres:
            genre, created = Genre.objects.update_or_create(
                tmdb_id=genre_data["id"],
                defaults={"name": genre_data["name"]}
            )
            action = "Oluşturuldu" if created else "Güncellendi"
            self.stdout.write(f"{action}: {genre.name}")

        self.stdout.write(self.style.SUCCESS("✔ Tür listesi başarıyla güncellendi."))
