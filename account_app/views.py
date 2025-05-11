from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.shortcuts import render, get_object_or_404
from .models import UserProfile, User, FollowRequest
from movies.models import Favorite
from .forms import ProfileUpdateForm
from django.contrib import messages

@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile = get_object_or_404(UserProfile, user=profile_user)
    favorite_movies = Favorite.objects.filter(user=profile_user).select_related('movie')
    is_own_profile = request.user == profile_user
    is_following = False
    is_follower = False
    if request.user.is_authenticated and request.user != profile_user:
        is_follower = profile.followers.filter(id=request.user.id).exists()
        
    if request.user != profile_user:
        viewer_profile = get_object_or_404(UserProfile, user=request.user)
        is_following = viewer_profile.following.filter(pk=profile.pk).exists()
    
    favorite_movies = []
    if profile_user == request.user or is_follower:
        favorite_movies = Favorite.objects.filter(user=profile_user).select_related('movie')
        
    has_pending_request = False
    if not is_own_profile:
        has_pending_request = FollowRequest.objects.filter(from_user=request.user, to_user=profile_user).exists()
        
    incoming_requests = []
    if is_own_profile:
        incoming_requests = FollowRequest.objects.filter(to_user=request.user)



    context = {
        'profile': profile,
        'favorite_movies': [fav.movie for fav in favorite_movies],
        'is_own_profile': is_own_profile,
        'is_follower': is_follower,
        'is_following': is_following,
        'follower_count': profile.followers.count(),
        'following_count': profile.following.count(),
        'followers': profile.followers.all(),
        'following': profile.following.all(),
        'has_pending_request': has_pending_request,
        'incoming_requests': incoming_requests,
    }
    return render(request, 'account/profile.html', context)

@login_required
def follow_user(request, username):
    target_user = get_object_or_404(User, username=username)
    target_profile = get_object_or_404(UserProfile, user=target_user)
    request.user.userprofile.following.add(target_profile)
    return redirect('profile_view', username=username)

@login_required
def unfollow_user(request, username):
    target_user = get_object_or_404(User, username=username)
    target_profile = get_object_or_404(UserProfile, user=target_user)
    request.user.userprofile.following.remove(target_profile)
    return redirect('profile_view', username=username)

@login_required
def delete_account(request):
    if request.method == 'POST':
        request.user.delete()
        logout(request)
        return redirect('home')

@login_required
def edit_profile(request):
    profile = request.user.userprofile

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated!")
            return redirect('profile_view', username=request.user.username)
    else:
        form = ProfileUpdateForm(instance=profile)

    return render(request, 'account/edit_profile.html', {'form': form})

class CustomPasswordResetView(PasswordResetView):
    template_name = 'account/password_reset_form.html'
    email_template_name = 'account/password_reset_email.html'
    success_url = reverse_lazy('account_reset_done')

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'account/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'account/password_reset_confirm.html'
    success_url = reverse_lazy('account_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'account/password_reset_done.html'

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('edit_profile')  # Redirect to a home page or dashboard
    else:
        form = UserCreationForm()
    return render(request, 'account_app/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to a home page or dashboard
        else:
            return render(request, 'account_app/login.html', {'error': 'Invalid username or password'})
    return render(request, 'account_app/login.html')

@login_required
def send_follow_request(request, username):
    to_user = get_object_or_404(User, username=username)
    if to_user != request.user:
        FollowRequest.objects.get_or_create(from_user=request.user, to_user=to_user)
    return redirect('profile_view', username=username)

@login_required
def accept_follow_request(request, request_id):
    follow_request = get_object_or_404(FollowRequest, id=request_id, to_user=request.user)
    follower_profile = get_object_or_404(UserProfile, user=follow_request.from_user)
    following_profile = get_object_or_404(UserProfile, user=request.user)
    
    follower_profile.following.add(following_profile)
    follow_request.delete()
    return redirect('profile_view', username=request.user.username)
