app_name= 'accounts'

from django.urls import path
from .views import register, user_login
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
]
