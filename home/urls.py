from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('register/', views.register, name='register'),
    path('clear-cookie-flag/', views.clear_cookie_flag, name='clear_cookie_flag'),
    path('captcha/', views.captcha_image, name='captcha_image'),
    path('health/', views.health_check, name='health_check'),
    path('profile/', views.profile_edit, name='profile_edit'),
]
