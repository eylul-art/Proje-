from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView

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
            return redirect('home')  # Redirect to a home page or dashboard
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
