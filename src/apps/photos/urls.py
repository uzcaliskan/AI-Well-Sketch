from django.urls import path

from . import views

urlpatterns = [
    path("kuyular/<int:well_id>/foto/yeni/", views.photo_create, name="photo_create"),
]
