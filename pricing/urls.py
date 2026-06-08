from django.urls import path
from . import views

urlpatterns = [
    path('', views.pricing, name='pricing'),
    path('<int:pk>/', views.plan_detail, name='plan_detail'),
]
