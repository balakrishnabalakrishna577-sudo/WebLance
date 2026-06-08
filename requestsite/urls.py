from django.urls import path
from . import views

urlpatterns = [
    path('', views.request_website, name='request_website'),
    path('service-quote/', views.service_quote, name='service_quote'),
    path('<int:pk>/proposal/', views.website_proposal, name='website_proposal'),
    path('<int:pk>/select-template/', views.select_template, name='select_template'),
]
