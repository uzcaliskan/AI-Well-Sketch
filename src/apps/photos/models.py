from django.conf import settings
from django.db import models


class Photo(models.Model):
    well = models.ForeignKey("wells.Well", on_delete=models.PROTECT, related_name="photos")
    dosya = models.ImageField(upload_to="fotograflar/%Y/%m/")
    tarih = models.DateField("Fotoğraf tarihi", db_index=True)
    not_metni = models.CharField("Not", max_length=300, blank=True)
    yukleyen = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    yuklenme = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-tarih", "-id"]

    def __str__(self):
        return f"{self.well} · {self.tarih}"
