from django.urls import path
from Hub import views

urlpatterns = [
    path('', views.index, name='home'),
    path('register1', views.register_step1, name='register1'),
    path('register2', views.register_step2, name='register2'),
    path('login', views.loginUser, name='login'),
    path('glogin', views.googleLogin, name='glogin'),
    path('role', views.role, name='role'),
    path('profile', views.profile, name='profile'),
    path('logout', views.logoutUser, name='logout'),
    path('checkout', views.checkout, name="checkout"),
    path('allfromCat/<str:cat>', views.allfromCat, name="allfromCat"),
]