from django.conf import settings
from django.db import models


class Report(models.Model):
    class Durum(models.TextChoices):
        YUKLENDI = "YUKLENDI", "Yüklendi"
        METIN_HAZIR = "METIN_HAZIR", "Metin hazır"
        ANALIZ_EDILDI = "ANALIZ_EDILDI", "Analiz edildi"
        HATA = "HATA", "Hata"

    well = models.ForeignKey("wells.Well", on_delete=models.PROTECT, related_name="reports")
    rapor_tarihi = models.DateField(db_index=True)
    dosya = models.FileField(upload_to="raporlar/%Y/%m/")
    metin = models.TextField(blank=True)
    durum = models.CharField(max_length=20, choices=Durum.choices, default=Durum.YUKLENDI)
    uyarilar = models.JSONField(default=list, blank=True)
    hata = models.TextField(blank=True)
    yukleyen = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    yuklenme = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-rapor_tarihi", "-id"]

    def __str__(self):
        return f"{self.well} · {self.rapor_tarihi}"
