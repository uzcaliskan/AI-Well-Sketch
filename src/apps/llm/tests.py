from datetime import date
from types import SimpleNamespace

from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings

from apps.proposals.models import Proposal
from apps.reports.models import Report
from apps.wells.models import Well

from .service import analiz_et
from .tools import arac_tanimlari


def blok(ad, **girdi):
    return SimpleNamespace(type="tool_use", name=ad, input=girdi)


class SahteIstemci:
    def __init__(self, bloklar):
        self.cagrilar = []
        self.messages = SimpleNamespace(create=self._create)
        self._bloklar = bloklar

    def _create(self, **kwargs):
        self.cagrilar.append(kwargs)
        return SimpleNamespace(content=self._bloklar)


class AracTanimTests(TestCase):
    def test_semalar_gecerli(self):
        araclar = arac_tanimlari()
        adlar = [a["name"] for a in araclar]
        self.assertEqual(len(adlar), len(set(adlar)))
        for a in araclar:
            self.assertEqual(a["input_schema"]["type"], "object")
            for z in a["input_schema"]["required"]:
                self.assertIn(z, a["input_schema"]["properties"])
        self.assertIn("degisiklik_yok", adlar)


class AnalizTests(TestCase):
    def setUp(self):
        self.well = Well.objects.create(ad="Arılı-1", referans_tipi="RKB", referans_yuksekligi=5)
        self.rapor = Report.objects.create(
            well=self.well, rapor_tarihi=date(2026, 2, 1), dosya="x.html",
            metin="Arılı-1  günlük rapor.\nCIBP 1100 m derinliğe set edildi.", durum=Report.Durum.METIN_HAZIR,
        )

    def test_arac_cagrilari_oneri_olur_kuyu_degismez(self):
        istemci = SahteIstemci([
            blok("tapa_ekle", olay_tarihi="2026-02-01", dayanak_alinti="CIBP 1100 m derinliğe set edildi.",
                 guven="yuksek", birim="m", tur="cibp", ust_derinlik=1100),
            blok("soru_sor", soru="Casing çapı nedir?"),
        ])
        oneriler = analiz_et(self.rapor, istemci=istemci)
        self.assertEqual(len(oneriler), 2)
        self.assertEqual(self.well.events.count(), 0)  # onay olmadan hiçbir şey değişmez
        self.assertTrue(all(o.durum == Proposal.Durum.ONAY_BEKLIYOR for o in oneriler))
        self.assertEqual(oneriler[0].uyarilar, [])
        self.rapor.refresh_from_db()
        self.assertEqual(self.rapor.durum, Report.Durum.ANALIZ_EDILDI)
        # Rapor metni veri olarak etiketlenir, tool_choice zorunlu.
        cagri = istemci.cagrilar[0]
        self.assertIn("<rapor>", cagri["messages"][0]["content"])
        self.assertEqual(cagri["tool_choice"], {"type": "any"})

    def test_dayanaksiz_oneri_dusurulur_uydurma_alinti_uyarilir(self):
        istemci = SahteIstemci([
            blok("tapa_ekle", olay_tarihi="2026-02-01", dayanak_alinti="", guven="yuksek", birim="m", tur="cibp"),
            blok("tapa_ekle", olay_tarihi="2026-02-01", dayanak_alinti="rapor bunu hiç söylemedi",
                 guven="orta", birim="m", tur="rbp", ust_derinlik=900),
        ])
        oneriler = analiz_et(self.rapor, istemci=istemci)
        self.assertEqual(len(oneriler), 1)
        self.assertTrue(any("birebir bulunamadı" in u for u in oneriler[0].uyarilar))

    def test_bekleyen_oneri_varken_tekrar_analiz_yok(self):
        istemci = SahteIstemci([blok("degisiklik_yok", gerekce="yok")])
        analiz_et(self.rapor, istemci=istemci)
        with self.assertRaises(ValueError):
            analiz_et(self.rapor, istemci=istemci)

    @override_settings(ANTHROPIC_API_KEY=None)
    def test_anahtar_yoksa_net_hata(self):
        with self.assertRaises(ImproperlyConfigured):
            analiz_et(self.rapor)
