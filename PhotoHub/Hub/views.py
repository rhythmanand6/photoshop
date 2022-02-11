from django.http import HttpResponse
from django.shortcuts import render, redirect

#Importing User model for creating a User instance or authenticating and login , logout
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

#For message displaying
from django.contrib import messages


# Create your views here.
def index(request):
    return render(request, 'index.html')


def loginUser(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(username=username, password=password)
        if user is not None:
           # A backend authenticated the credentials
           login(request, user)
           messages.success(request, 'Successfully logged in as ' + str(request.user) + ' !')
           return redirect('/')
        else:
           # No backend authenticated the credentials
           messages.warning(request, 'Invalid credentials! Please try again.')
           return redirect('/')

    return HttpResponse('<h1>Error 404</h1><br> <h3>Page not found!</h3>')


def logoutUser(request):
    logout(request)
    messages.success(request, 'Your have logged out successfully !')
    return redirect('/')


def profile(request):
    return render(request, 'profile.html')
