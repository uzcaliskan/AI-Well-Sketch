import tempfile
from datetime import date

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from apps.wells.models import Well

from .extraction import MetinCikarmaHatasi, metin_cikar
from .models import Report
from .views import isim_uyarisi


class ExtractionTests(TestCase):
    def test_html_metni_script_olmadan_cikar(self):
        dosya = SimpleUploadedFile("r.html", b"<html><script>x=1</script><body><p>Arili-1 tapa kondu</p></body></html>")
        metin, uyarilar = metin_cikar(dosya)
        self.assertIn("tapa kondu", metin)
        self.assertNotIn("x=1", metin)
        self.assertEqual(uyarilar, [])

    def test_desteklenmeyen_bicim(self):
        with self.assertRaises(MetinCikarmaHatasi):
            metin_cikar(SimpleUploadedFile("r.docx", b"x"))

    def test_bozuk_pdf(self):
        with self.assertRaises(MetinCikarmaHatasi):
            metin_cikar(SimpleUploadedFile("r.pdf", b"not a pdf"))


class IsimUyarisiTests(TestCase):
    def test_eski_ad_eslesir_hicbiri_yoksa_uyarir(self):
        w = Well.objects.create(ad="Arılı-1", referans_tipi="RKB", referans_yuksekligi=5)
        w.ad = "Arılı-1/S"
        w.save()
        self.assertEqual(isim_uyarisi(w, "Rapor: Arılı-1 kuyusu"), [])
        self.assertTrue(isim_uyarisi(w, "Rapor: Başka-9 kuyusu"))


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class YuklemeTests(TestCase):
    def test_html_rapor_yukle(self):
        user = get_user_model().objects.create_user("u", password="p")
        w = Well.objects.create(ad="Arılı-1", referans_tipi="RKB", referans_yuksekligi=5)
        self.client.force_login(user)
        dosya = SimpleUploadedFile("r.html", "<p>Arılı-1: CIBP 1100 m'ye kondu</p>".encode("utf-8"))
        cevap = self.client.post(f"/kuyular/{w.pk}/rapor/yeni/", {"rapor_tarihi": "2026-02-01", "dosya": dosya})
        self.assertEqual(cevap.status_code, 302)
        rapor = Report.objects.get()
        self.assertEqual(rapor.durum, Report.Durum.METIN_HAZIR)
        self.assertEqual(rapor.rapor_tarihi, date(2026, 2, 1))
        self.assertEqual(rapor.uyarilar, [])
