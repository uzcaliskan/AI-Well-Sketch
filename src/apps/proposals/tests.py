import json
from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.reports.models import Report
from apps.wells.models import Well
from apps.wells.state import kuyu_durumu

from .models import Proposal


class OnayAkisiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("u", password="p")
        self.client.force_login(self.user)
        self.well = Well.objects.create(ad="Arılı-1", referans_tipi="RKB", referans_yuksekligi=5)
        self.rapor = Report.objects.create(well=self.well, rapor_tarihi=date(2026, 2, 1), dosya="x.html", metin="m")

    def oneri(self, **parametreler):
        varsayilan = dict(olay_tarihi="2026-02-01", dayanak_alinti="CIBP kondu", guven="yuksek",
                          birim="m", tur="cibp", ust_derinlik=1100)
        varsayilan.update(parametreler)
        return Proposal.objects.create(rapor=self.rapor, well=self.well, arac_adi="tapa_ekle",
                                       parametreler=varsayilan, olay_tarihi=date(2026, 2, 1))

    def onayla(self, oneri, parametreler=None):
        return self.client.post(
            f"/oneriler/{oneri.pk}/onayla/",
            {"parametreler": json.dumps(parametreler if parametreler is not None else oneri.parametreler)},
        )

    def test_onay_olay_uretir_ve_sketch_degisir(self):
        o = self.oneri()
        self.onayla(o)
        o.refresh_from_db()
        self.assertEqual(o.durum, Proposal.Durum.ONAYLANDI)
        self.assertEqual(o.karar_veren, self.user)
        olay = self.well.events.get()
        self.assertEqual(olay.onaylayan, self.user)
        self.assertEqual(olay.rapor, self.rapor)
        self.assertNotIn("dayanak_alinti", olay.veri)
        self.assertEqual(len(kuyu_durumu(self.well)["tapalar"]), 1)

    def test_duzeltilerek_onay_orijinali_korur(self):
        o = self.oneri()
        degisen = {**o.parametreler, "ust_derinlik": 1150}
        self.onayla(o, degisen)
        o.refresh_from_db()
        self.assertEqual(o.durum, Proposal.Durum.DUZELTILDI)
        self.assertEqual(o.parametreler["ust_derinlik"], 1100)
        self.assertEqual(self.well.events.get().veri["ust_derinlik"], 1150)

    def test_birimsiz_derinlik_onaylanamaz(self):
        o = self.oneri()
        parametreler = {k: v for k, v in o.parametreler.items() if k != "birim"}
        self.onayla(o, parametreler)
        self.assertEqual(self.well.events.count(), 0)
        o.refresh_from_db()
        self.assertEqual(o.durum, Proposal.Durum.ONAY_BEKLIYOR)

    def test_gecersiz_tarih_ve_json(self):
        o = self.oneri()
        self.onayla(o, {**o.parametreler, "olay_tarihi": "yarın"})
        self.client.post(f"/oneriler/{o.pk}/onayla/", {"parametreler": "{bozuk"})
        self.assertEqual(self.well.events.count(), 0)

    def test_red_olay_uretmez_ve_iki_kez_karar_verilemez(self):
        o = self.oneri()
        self.client.post(f"/oneriler/{o.pk}/reddet/")
        self.onayla(o)
        o.refresh_from_db()
        self.assertEqual(o.durum, Proposal.Durum.REDDEDILDI)
        self.assertEqual(self.well.events.count(), 0)

    def test_bilgi_araci_olay_uretmez(self):
        o = Proposal.objects.create(rapor=self.rapor, well=self.well, arac_adi="soru_sor", parametreler={"soru": "?"})
        self.onayla(o, {})
        o.refresh_from_db()
        self.assertEqual(o.durum, Proposal.Durum.KAPATILDI)
        self.assertEqual(self.well.events.count(), 0)

    def test_acik_yonlendirme_engellenir(self):
        o = self.oneri()
        cevap = self.client.post(
            f"/oneriler/{o.pk}/reddet/", {"next": "//evil.example/"}
        )
        self.assertNotIn("evil.example", cevap["Location"])
