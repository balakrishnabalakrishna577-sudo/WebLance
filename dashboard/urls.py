from django.urls import path
from . import views

urlpatterns = [
    # Client
    path('',                                    views.client_dashboard,       name='client_dashboard'),
    path('project/<int:pk>/',                   views.project_detail,         name='project_detail'),
    path('project/<int:pk>/review/',            views.submit_review,          name='submit_review'),
    path('project/<int:pk>/review/delete/',     views.delete_review,          name='delete_review'),
    path('booking/<int:pk>/cancel/',            views.cancel_booking,         name='cancel_booking'),
    path('quote/<int:pk>/cancel/',              views.cancel_quote_request,   name='cancel_quote_request'),
    # Admin
    path('admin/projects/',                     views.admin_projects,         name='admin_projects'),
    path('admin/projects/new/',                 views.admin_project_create,   name='admin_project_create'),
    path('admin/projects/<int:pk>/',            views.admin_project_detail,   name='admin_project_detail'),
    path('admin/projects/<int:pk>/delete/',     views.admin_project_delete,   name='admin_project_delete'),
]
