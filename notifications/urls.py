from django.urls import path
from . import views

urlpatterns = [
    path('',                            views.notification_list,    name='notification_list'),
    path('<int:pk>/read/',              views.mark_read,            name='notif_mark_read'),
    path('mark-all-read/',              views.mark_all_read,        name='notif_mark_all_read'),
    path('<int:pk>/delete/',            views.delete_notification,  name='notif_delete'),
    path('clear-all/',                  views.clear_all,            name='notif_clear_all'),
    path('api/unread/',                 views.api_unread_count,     name='notif_api_unread'),
]
