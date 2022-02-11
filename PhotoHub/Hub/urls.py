from django.urls import path
from Hub import views

urlpatterns = [
    path('', views.index, name='home'),
]    