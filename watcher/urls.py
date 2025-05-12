"""
URL configuration for watcher project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from home.views import home
from account_app.views import CustomPasswordResetView, CustomPasswordResetDoneView, CustomPasswordResetConfirmView, CustomPasswordResetCompleteView, profile_view, edit_profile, delete_account, follow_user, unfollow_user, send_follow_request, accept_follow_request, reject_follow_request
from movies.views import search_movies
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),  # Include allauth URLs
    path('password/reset/', CustomPasswordResetView.as_view(), name='account_reset_password'),
    path('password/reset/done/', CustomPasswordResetDoneView.as_view(), name='account_reset_done'),
    path('password/reset/key/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='account_reset_confirm'),
    path('password/reset/key/done/', CustomPasswordResetCompleteView.as_view(), name='account_reset_complete'),
    path('', home, name='home'),
    path('movies/', include('movies.urls')),
    path('follow/<str:username>/', follow_user, name='follow_user'),
    path('unfollow/<str:username>/', unfollow_user, name='unfollow_user'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('users/<str:username>/', profile_view, name='profile_view'),
    path('profile/delete/', delete_account, name='delete_account'),
    path('search/', search_movies, name='search'),
    path('follow-request/send/<str:username>/', send_follow_request, name='send_follow_request'),
    path('follow-request/accept/<int:request_id>/', accept_follow_request, name='accept_follow_request'),
    path('follow-request/reject/<int:request_id>/', reject_follow_request, name='reject_follow_request'),


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)