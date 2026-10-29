from django.urls import path

from . import views

urlpatterns = [
    path("oneriler/<int:pk>/onayla/", views.approve, name="proposal_approve"),
    path("oneriler/<int:pk>/reddet/", views.reject, name="proposal_reject"),
]
