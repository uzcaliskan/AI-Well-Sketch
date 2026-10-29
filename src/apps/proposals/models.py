import json

from django.conf import settings
from django.db import models

from apps.wells.state import BILGI_ARACLARI


class Proposal(models.Model):
    """LLM'in bir araç çağrısı. Onaylanana kadar kuyu durumunu değiştirmez (K-05)."""

    class Durum(models.TextChoices):
        ONAY_BEKLIYOR = "ONAY_BEKLIYOR", "Onay bekliyor"
        ONAYLANDI = "ONAYLANDI", "Onaylandı"
        DUZELTILDI = "DUZELTILDI", "Düzeltilerek onaylandı"
        REDDEDILDI = "REDDEDILDI", "Reddedildi"
        KAPATILDI = "KAPATILDI", "Okundu"

    rapor = models.ForeignKey("reports.Report", on_delete=models.CASCADE, related_name="oneriler")
    well = models.ForeignKey("wells.Well", on_delete=models.PROTECT, related_name="oneriler")
    arac_adi = models.CharField(max_length=60)
    parametreler = models.JSONField()
    olay_tarihi = models.DateField(null=True, blank=True)
    dayanak_alinti = models.TextField(blank=True)
    guven = models.CharField(max_length=10, blank=True)
    uyarilar = models.JSONField(default=list, blank=True)
    durum = models.CharField(max_length=20, choices=Durum.choices, default=Durum.ONAY_BEKLIYOR)
    karar_veren = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    karar_zamani = models.DateTimeField(null=True, blank=True)
    olay = models.OneToOneField("wells.Event", null=True, blank=True, on_delete=models.SET_NULL, related_name="oneri")
    olusturma = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.arac_adi} ({self.get_durum_display()})"

    @property
    def parametreler_json(self):
        return json.dumps(self.parametreler, ensure_ascii=False, indent=2)

    @property
    def bilgi_mi(self):
        return self.arac_adi in BILGI_ARACLARI
