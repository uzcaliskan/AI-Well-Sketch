from django.urls import path

from . import views

urlpatterns = [
    path("", views.well_list, name="well_list"),
    path("kuyular/yeni/", views.well_create, name="well_create"),
    path("kuyular/<int:pk>/", views.well_detail, name="well_detail"),
    path("kuyular/<int:pk>/duzenle/", views.well_rename, name="well_rename"),
]
