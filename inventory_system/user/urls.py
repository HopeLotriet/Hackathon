from django.urls import path
from .views import profile, RegisterView
from . import views
from user.views import CustomLoginView, ResetPasswordView, ChangePasswordView
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', login_required(views.home), name='home'),
    path('register/', RegisterView.as_view(), name='users-register'),
    path('profile/', profile, name='users-profile'),
]