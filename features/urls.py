from django.urls import path
from . import views

urlpatterns = [
    # ── Milestones ──
    path('milestones/<int:project_pk>/',        views.milestone_list,     name='milestone_list'),
    path('milestones/<int:project_pk>/add/',    views.milestone_add,      name='milestone_add'),
    path('milestones/update/<int:pk>/',         views.milestone_update,   name='milestone_update'),
    path('milestones/delete/<int:pk>/',         views.milestone_delete,   name='milestone_delete'),
    path('my-milestones/<int:project_pk>/',     views.client_milestones,  name='client_milestones'),

    # ── Invoices ──
    path('invoices/',                           views.invoice_list,           name='invoice_list'),
    path('invoices/new/',                       views.invoice_create,         name='invoice_create'),
    path('invoices/from-agreement/<int:agr_pk>/', views.invoice_from_agreement, name='invoice_from_agreement'),
    path('invoices/<int:pk>/',                  views.invoice_detail,         name='invoice_detail'),
    path('invoices/<int:pk>/status/',           views.invoice_status,         name='invoice_status'),
    path('invoices/<int:pk>/send/',             views.invoice_send,           name='invoice_send'),
    path('invoices/<int:pk>/delete/',           views.invoice_delete,         name='invoice_delete'),

    # ── Chat ──
    path('chat/',                               views.chat_list,        name='chat_list'),
    path('my-chats/',                           views.client_chat_list, name='client_chat_list'),
    path('chat/<int:project_pk>/',              views.chat_room,        name='chat_room'),
    path('chat/send/<int:room_pk>/',            views.chat_send,        name='chat_send'),
    path('chat/poll/<int:room_pk>/',            views.chat_poll,        name='chat_poll'),
    path('chat/ai-reply/<int:room_pk>/',        views.chat_ai_reply,    name='chat_ai_reply'),

    # ── Live progress poll ──
    path('progress-poll/<int:project_pk>/',     views.progress_poll,    name='progress_poll'),

    # ── Booking ──
    path('book/',                               views.booking_page,   name='booking_page'),
    path('bookings/admin/',                     views.booking_admin,  name='booking_admin'),
    path('bookings/slot/add/',                  views.slot_add,       name='slot_add'),
    path('bookings/slot/<int:pk>/delete/',      views.slot_delete,    name='slot_delete'),
    path('bookings/<int:pk>/status/',           views.booking_status, name='booking_status'),

    # ── Time Tracker ──
    path('timelog/<int:project_pk>/',           views.timelog_list,   name='timelog_list'),
    path('timelog/delete/<int:pk>/',            views.timelog_delete, name='timelog_delete'),
    path('my-timelog/<int:project_pk>/',        views.client_timelog, name='client_timelog'),
]
