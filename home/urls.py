from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('clear-cookie-flag/', views.clear_cookie_flag, name='clear_cookie_flag'),
]
