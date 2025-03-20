from django.shortcuts import render
import requests
from .utils import get_popular_movies

def home(request):
    movies = get_popular_movies()  # Filmleri çek
    return render(request, "home/home.html", {"movies": movies})
