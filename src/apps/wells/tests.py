from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.sketch.render import render_svg

from .forms import WellForm
from .models import Event, Well
from .state import FT, kuyu_durumu
from .validation import dogrula


def kuyu(ad="Arılı-1"):
    return Well.objects.create(ad=ad, referans_tipi="RKB", referans_yuksekligi=5)


def olay(well, tip, tarih, **veri):
    return Event.objects.create(well=well, tip=tip, olay_tarihi=tarih, veri=veri)


class DurumTests(TestCase):
    def test_yeni_kuyu_bos(self):
        durum = kuyu_durumu(kuyu())
        self.assertEqual(durum["casingler"], [])
        self.assertIn("Henüz onaylanmış veri yok", render_svg(durum))

    def test_ft_ve_m_birlikte_saklanir(self):
        w = kuyu()
        olay(w, "casing_ekle", date(2026, 1, 1), tur="yuzey", od_inc=13.375, pabuc_derinlik=1000, birim="ft")
        c = kuyu_durumu(w)["casingler"][0]
        self.assertAlmostEqual(c["pabuc_derinlik"]["m"], 1000 * FT, places=2)
        self.assertEqual(c["pabuc_derinlik"]["ft"], 1000)

    def test_geriye_donuk_olay_sonrasini_yeniden_hesaplar(self):
        w = kuyu()
        olay(w, "kuyu_tabani_guncelle", date(2026, 3, 1), td_derinlik=2000, birim="m")
        olay(w, "kuyu_tabani_guncelle", date(2026, 5, 1), pbtd_derinlik=1800, birim="m")
        self.assertEqual(kuyu_durumu(w)["kuyu_tabani"]["td"]["m"], 2000)
        # Daha eski tarihli bir olay sonradan eklenir: TD sonra gelen olayla ezilmemeli, sıra tarihe göredir.
        olay(w, "kuyu_tabani_guncelle", date(2026, 4, 1), td_derinlik=2100, birim="m")
        durum = kuyu_durumu(w)
        self.assertEqual(durum["kuyu_tabani"]["td"]["m"], 2100)
        self.assertEqual(durum["kuyu_tabani"]["pbtd"]["m"], 1800)

    def test_tarihe_gore_gecmis_gorunum(self):
        w = kuyu()
        olay(w, "kuyu_tabani_guncelle", date(2026, 3, 1), td_derinlik=2000, birim="m")
        olay(w, "kuyu_tabani_guncelle", date(2026, 5, 1), td_derinlik=2200, birim="m")
        self.assertEqual(kuyu_durumu(w, tarih=date(2026, 4, 1))["kuyu_tabani"]["td"]["m"], 2000)

    def test_tapa_ekle_ve_kaldir(self):
        w = kuyu()
        tapa = olay(w, "tapa_ekle", date(2026, 1, 1), tur="rbp", ust_derinlik=500, birim="m")
        self.assertEqual(len(kuyu_durumu(w)["tapalar"]), 1)
        olay(w, "tapa_kaldir", date(2026, 2, 1), hedef_id=tapa.id)
        self.assertEqual(kuyu_durumu(w)["tapalar"], [])


class AdGecmisiTests(TestCase):
    def test_yeniden_adlandirma_eski_adi_saklar(self):
        w = kuyu("Arılı-1")
        w.ad = "Arılı-1/S"
        w.save()
        self.assertEqual(Well.ada_gore_bul("arılı-1"), w)
        self.assertEqual(Well.ada_gore_bul("Arılı-1/S"), w)
        self.assertEqual(w.names.filter(bitis__isnull=True).count(), 1)

    def test_eski_ad_baska_kuyuya_verilemez(self):
        w = kuyu("Arılı-1")
        w.ad = "Arılı-1/S"
        w.save()
        form = WellForm({"ad": "Arılı-1", "referans_tipi": "RKB", "referans_yuksekligi": 3})
        self.assertFalse(form.is_valid())
        self.assertIn("ad", form.errors)


class DogrulamaTests(TestCase):
    def test_od_drift_ihlali_uyari_verir(self):
        w = kuyu()
        olay(w, "casing_ekle", date(2026, 1, 1), tur="yuzey", od_inc=13.375, drift_id_inc=12.0,
             pabuc_derinlik=500, ust_derinlik=0, birim="m")
        veri = dict(tur="uretim", od_inc=12.5, pabuc_derinlik=2000, ust_derinlik=0, birim="m")
        uyarilar = dogrula(w, "casing_ekle", veri, date(2026, 2, 1))
        self.assertTrue(any("drift ID" in u for u in uyarilar))

    def test_eksik_alan_ve_birim_uyarisi(self):
        w = kuyu()
        uyarilar = dogrula(w, "casing_ekle", dict(tur="uretim", pabuc_derinlik=2000), date(2026, 1, 1))
        self.assertTrue(any("bilinmeyen zorunlu alanlar" in u for u in uyarilar))
        self.assertTrue(any("birim" in u for u in uyarilar))


class SketchTests(TestCase):
    def test_dolu_sketch_ogeleri_icerir(self):
        w = kuyu()
        olay(w, "formasyon_ekle_veya_guncelle", date(2026, 1, 1), ad="Karababa", tepe_derinlik=0, taban_derinlik=900, birim="m")
        olay(w, "casing_ekle", date(2026, 1, 2), tur="uretim", od_inc=7, ust_derinlik=0, pabuc_derinlik=1500, birim="m")
        olay(w, "perforasyon_ekle", date(2026, 1, 3), ust_derinlik=1200, alt_derinlik=1210, birim="m")
        olay(w, "tapa_ekle", date(2026, 1, 4), tur="cibp", ust_derinlik=1100, birim="m")
        olay(w, "kuyu_tabani_guncelle", date(2026, 1, 5), td_derinlik=1550, birim="m")
        svg = render_svg(kuyu_durumu(w), "ft")
        for parca in ("Karababa", "uretim", "cibp", "TD", "ft"):
            self.assertIn(parca, svg)
        # Tapa altındaki açık perforasyon turuncu (izole) çizilmeli.
        self.assertIn("#e67e22", svg)

    def test_svg_metni_kacislanir(self):
        w = kuyu()
        olay(w, "formasyon_ekle_veya_guncelle", date(2026, 1, 1), ad="<script>x</script>", tepe_derinlik=10, birim="m")
        self.assertNotIn("<script>", render_svg(kuyu_durumu(w)))


class GorunumTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("u", password="p")

    def test_giris_gerekli(self):
        self.assertEqual(self.client.get("/").status_code, 302)

    def test_liste_ve_detay(self):
        w = kuyu()
        self.client.force_login(self.user)
        self.assertContains(self.client.get("/"), "Arılı-1")
        cevap = self.client.get(f"/kuyular/{w.pk}/?birim=ft&tarih=2026-01-01")
        self.assertEqual(cevap.status_code, 200)
        self.assertContains(cevap, "<svg")
