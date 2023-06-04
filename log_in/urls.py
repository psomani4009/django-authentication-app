from django.urls import path
from . import views

urlpatterns = [
    path('', views.base, name='Log In Page'),
    path('login', views.logIn, name='LogIn POST'),
    path('signup', views.signUp, name='LogIn POST'),
    path('verify/<str:mail>', views.otpVerification, name='LogIn POST'),
]