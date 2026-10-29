from django.urls import path

from . import views

urlpatterns = [
    path("kuyular/<int:well_id>/rapor/yeni/", views.report_create, name="report_create"),
    path("raporlar/<int:pk>/", views.report_detail, name="report_detail"),
    path("raporlar/<int:pk>/analiz/", views.report_analyze, name="report_analyze"),
]
