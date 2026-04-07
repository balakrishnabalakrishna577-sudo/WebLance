from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='admin_dashboard'),
    path('contacts/', views.contacts_list, name='admin_contacts'),
    path('contacts/edit/<int:pk>/', views.contact_edit, name='admin_contact_edit'),
    path('contacts/delete/<int:pk>/', views.contact_delete, name='admin_contact_delete'),
    path('requests/', views.requests_list, name='admin_requests'),
    path('requests/delete/<int:pk>/', views.request_delete, name='admin_request_delete'),
    path('requests/status/<int:pk>/', views.request_status, name='admin_request_status'),
    path('users/', views.users_list, name='admin_users'),
    path('users/edit/<int:pk>/', views.user_edit, name='admin_user_edit'),
    path('users/toggle-staff/<int:pk>/', views.user_toggle_staff, name='admin_user_toggle_staff'),
    path('users/delete/<int:pk>/', views.user_delete, name='admin_user_delete'),
    path('portfolio/', views.portfolio_list, name='admin_portfolio'),
    path('portfolio/add/', views.portfolio_add, name='admin_portfolio_add'),
    path('portfolio/edit/<int:pk>/', views.portfolio_edit, name='admin_portfolio_edit'),
    path('portfolio/delete/<int:pk>/', views.portfolio_delete, name='admin_portfolio_delete'),
    path('pricing/', views.pricing_list, name='admin_pricing'),
    path('pricing/add/', views.pricing_add, name='admin_pricing_add'),
    path('pricing/edit/<int:pk>/', views.pricing_edit, name='admin_pricing_edit'),
    path('pricing/delete/<int:pk>/', views.pricing_delete, name='admin_pricing_delete'),
    path('testimonials/', views.testimonials_list, name='admin_testimonials'),
    path('testimonials/add/', views.testimonial_add, name='admin_testimonial_add'),
    path('testimonials/edit/<int:pk>/', views.testimonial_edit, name='admin_testimonial_edit'),
    path('testimonials/delete/<int:pk>/', views.testimonial_delete, name='admin_testimonial_delete'),
]
