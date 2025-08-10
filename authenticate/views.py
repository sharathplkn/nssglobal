from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import UserRegistrationForm, LoginForm
from nss.models import College
from .forms import LoginForm

# Create your views here.

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if user.user_type == 'university':
                user.university = form.cleaned_data['university']
            elif user.user_type == 'college':
                user.college = form.cleaned_data['college']
            user.save()
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user_type = form.cleaned_data['user_type']
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None and user.user_type == user_type:
                login(request, user)
                if user_type == 'university':
                    return redirect('university_dashboard')
                else:
                    return redirect('college_dashboard')
            else:
                form.add_error(None, "Invalid credentials or user type mismatch")
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    return redirect('home')