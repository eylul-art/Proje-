import requests
from django.conf import settings
from django.conf import settings

def get_popular_movies():
    """
    TMDB API'den popüler filmleri çeker.
    """
    tmdb_api_key = settings.TMDB_API_KEY
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={tmdb_api_key}&language=tr-TR"
    
    print(f"API'ye istek atılıyor: {url}")  # API çağrısını logla

    try:
        response = requests.get(url)
        print(f"API Response Status Code: {response.status_code}")  # HTTP durum kodunu kontrol et
        response.raise_for_status()  # Hata kontrolü yap
        data = response.json()
        print(f"API Yanıtı: {data}")  # API cevabını kontrol et
        return data.get("results", [])[:6]  # İlk 6 filmi al
    except requests.exceptions.RequestException as e:
        print(f"TMDB API Hatası: {e}")
        return []
