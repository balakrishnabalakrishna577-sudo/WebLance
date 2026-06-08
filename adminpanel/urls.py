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
    # Client Reviews
    path('reviews/', views.reviews_list, name='admin_reviews'),
    path('reviews/<int:pk>/toggle/', views.review_toggle_public, name='admin_review_toggle'),
    path('reviews/<int:pk>/delete/', views.review_delete, name='admin_review_delete'),

    # Bot (AI Widget) Conversations
    path('bot-chats/', views.bot_chats_list, name='admin_bot_chats'),
    path('bot-chats/mark-all-read/', views.bot_chat_mark_all_read, name='admin_bot_chats_mark_read'),
    path('bot-chats/<uuid:session_id>/', views.bot_chat_detail, name='admin_bot_chat_detail'),
    path('bot-chats/<uuid:session_id>/delete/', views.bot_chat_delete, name='admin_bot_chat_delete'),
]
