from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("giris/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("cikis/", auth_views.LogoutView.as_view(), name="logout"),
    path("", include("apps.wells.urls")),
    path("", include("apps.reports.urls")),
    path("", include("apps.proposals.urls")),
    path("", include("apps.photos.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
