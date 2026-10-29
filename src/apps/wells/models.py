from django.conf import settings
from django.db import models
from django.utils import timezone


class Well(models.Model):
    REFERANS_TIPLERI = [("RKB", "RKB"), ("DF", "DF"), ("GL", "GL")]

    ad = models.CharField("Kuyu adı", max_length=200, unique=True)
    referans_tipi = models.CharField("Referans noktası", max_length=3, choices=REFERANS_TIPLERI)
    referans_yuksekligi = models.FloatField("Referans yüksekliği (m)")
    olusturma = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["ad"]

    def __str__(self):
        return self.ad

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Ad geçmişi (kararlar.md K-13): ad değişince eski ad kapatılır, yeni ad açılır.
        acik = self.names.filter(bitis__isnull=True).first()
        if acik is None:
            WellName.objects.create(well=self, ad=self.ad)
        elif acik.ad != self.ad:
            acik.bitis = timezone.now()
            acik.save(update_fields=["bitis"])
            WellName.objects.create(well=self, ad=self.ad)

    @classmethod
    def ada_gore_bul(cls, ad):
        """Güncel veya eski ada göre kuyu bulur; yoksa None."""
        isim = WellName.objects.filter(ad__iexact=ad.strip()).select_related("well").first()
        return isim.well if isim else None

    def tum_adlar(self):
        return list(self.names.values_list("ad", flat=True))


class WellName(models.Model):
    well = models.ForeignKey(Well, on_delete=models.CASCADE, related_name="names")
    ad = models.CharField(max_length=200, db_index=True)
    baslangic = models.DateTimeField(auto_now_add=True)
    bitis = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["baslangic", "id"]

    def __str__(self):
        return self.ad


class Event(models.Model):
    """Onaylanmış değişiklik. Silinmez/güncellenmez; kuyu durumu bunlardan türetilir (K-09)."""

    well = models.ForeignKey(Well, on_delete=models.PROTECT, related_name="events")
    tip = models.CharField(max_length=60)
    olay_tarihi = models.DateField(db_index=True)
    veri = models.JSONField()
    dayanak_alinti = models.TextField(blank=True)
    rapor = models.ForeignKey(
        "reports.Report", null=True, blank=True, on_delete=models.SET_NULL, related_name="events"
    )
    onaylayan = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    onay_zamani = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["olay_tarihi", "id"]
        indexes = [models.Index(fields=["well", "olay_tarihi"])]

    def __str__(self):
        return f"{self.well} · {self.tip} · {self.olay_tarihi}"
