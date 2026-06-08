from django.urls import path
from . import views

urlpatterns = [
    # Admin panel routes (under /panel/agreements/)
    path('',                          views.agreement_list,       name='agreement_list'),
    path('new/',                      views.agreement_create,     name='agreement_create'),
    path('<int:pk>/',                 views.agreement_detail,     name='agreement_detail'),
    path('<int:pk>/edit/',            views.agreement_edit,       name='agreement_edit'),
    path('<int:pk>/delete/',          views.agreement_delete,     name='agreement_delete'),
    path('<int:pk>/status/',          views.agreement_status,     name='agreement_status'),
    path('<int:pk>/pdf/',             views.agreement_pdf,        name='agreement_pdf'),
    path('<int:pk>/send-email/',      views.agreement_send_email, name='agreement_send_email'),
    # Public routes (under /agreement/)
    path('verify/<uuid:ref_id>/',     views.agreement_verify,     name='agreement_verify'),
    path('sign/<uuid:ref_id>/',       views.agreement_sign,       name='agreement_sign'),
]
