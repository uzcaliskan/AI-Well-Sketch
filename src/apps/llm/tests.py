import json
import threading
from datetime import date
from http.server import BaseHTTPRequestHandler, HTTPServer

from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase, TestCase, override_settings

from apps.proposals.models import Proposal
from apps.reports.models import Report
from apps.wells.models import Well

from .client import LlmHatasi, VllmIstemcisi, adres_icerde_mi, vllm_istemcisi
from .service import analiz_et
from .tools import arac_tanimlari


def cagri(ad, **girdi):
    return {"function": {"name": ad, "arguments": json.dumps(girdi)}}


def yanit(cagrilar):
    return {"choices": [{"message": {"role": "assistant", "content": None, "tool_calls": cagrilar}}]}


class SahteIstemci:
    """vLLM istemcisini taklit eder; ağa çıkmaz."""

    def __init__(self, cagrilar):
        self.kayit = []
        self._yanit = yanit(cagrilar)

    def sohbet(self, mesajlar, araclar):
        self.kayit.append({"mesajlar": mesajlar, "araclar": araclar})
        return self._yanit


class SahteSunucu:
    """Yerel (127.0.0.1) sahte vLLM: gelen isteği saklar, verilen yanıtı döndürür."""

    def __init__(self, durum=200, govde=None, baslik=None):
        sunucu = self
        sunucu.istekler = []

        class Isleyici(BaseHTTPRequestHandler):
            def do_POST(self):
                uzunluk = int(self.headers["Content-Length"])
                sunucu.istekler.append(
                    {"yol": self.path, "govde": json.loads(self.rfile.read(uzunluk)), "yetki": self.headers.get("Authorization")}
                )
                veri = json.dumps(govde if govde is not None else {}).encode()
                self.send_response(durum)
                for k, v in (baslik or {}).items():
                    self.send_header(k, v)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(veri)))
                self.end_headers()
                self.wfile.write(veri)

            def log_message(self, *args):
                pass

        self.http = HTTPServer(("127.0.0.1", 0), Isleyici)
        self.adres = f"http://127.0.0.1:{self.http.server_address[1]}/v1"
        threading.Thread(target=self.http.serve_forever, daemon=True).start()

    def kapat(self):
        self.http.shutdown()
        self.http.server_close()


class AracTanimTests(SimpleTestCase):
    def test_semalar_gecerli(self):
        araclar = arac_tanimlari()
        adlar = [a["function"]["name"] for a in araclar]
        self.assertEqual(len(adlar), len(set(adlar)))
        for a in araclar:
            self.assertEqual(a["type"], "function")
            parametreler = a["function"]["parameters"]
            self.assertEqual(parametreler["type"], "object")
            for z in parametreler["required"]:
                self.assertIn(z, parametreler["properties"])
        self.assertIn("degisiklik_yok", adlar)


class IstemciKorumaTests(SimpleTestCase):
    def test_adres_kontrolu(self):
        for ic in ("localhost", "127.0.0.1", "10.1.2.3", "192.168.0.7", "172.16.5.5"):
            self.assertTrue(adres_icerde_mi(ic), ic)
        for dis in ("api.openai.com", "8.8.8.8", "example.com"):
            self.assertFalse(adres_icerde_mi(dis), dis)

    @override_settings(VLLM_BASE_URL="https://api.example.com/v1", VLLM_MODEL="m", VLLM_IZINLI_HOSTLAR=[])
    def test_dis_adres_reddedilir(self):
        with self.assertRaises(ImproperlyConfigured) as ctx:
            vllm_istemcisi()
        self.assertIn("dışarı çıkmaması", str(ctx.exception))

    @override_settings(VLLM_BASE_URL="http://vllm.sirket.local:8000/v1", VLLM_MODEL="m",
                       VLLM_IZINLI_HOSTLAR=["vllm.sirket.local"])
    def test_izinli_alan_adi_kabul_edilir(self):
        self.assertIsInstance(vllm_istemcisi(), VllmIstemcisi)

    @override_settings(VLLM_BASE_URL="http://10.0.0.5:8000/v1", VLLM_MODEL="m")
    def test_ozel_ip_kabul_edilir(self):
        self.assertIsInstance(vllm_istemcisi(), VllmIstemcisi)

    @override_settings(VLLM_BASE_URL="", VLLM_MODEL="")
    def test_ayar_yoksa_net_hata(self):
        with self.assertRaises(ImproperlyConfigured):
            vllm_istemcisi()


class IstemciAgTests(SimpleTestCase):
    """Gerçek `requests` istemcisi, yalnızca 127.0.0.1 üzerindeki sahte sunucuya karşı."""

    def test_istek_govdesi_ve_yanit(self):
        sunucu = SahteSunucu(govde=yanit([cagri("degisiklik_yok", gerekce="x")]))
        self.addCleanup(sunucu.kapat)
        istemci = VllmIstemcisi(sunucu.adres, "sahte-model", api_key="gizli", max_tokens=77)
        sonuc = istemci.sohbet([{"role": "user", "content": "merhaba"}], arac_tanimlari())
        istek = sunucu.istekler[0]
        self.assertEqual(istek["yol"], "/v1/chat/completions")
        self.assertEqual(istek["yetki"], "Bearer gizli")
        self.assertEqual(istek["govde"]["model"], "sahte-model")
        self.assertEqual(istek["govde"]["tool_choice"], "required")
        self.assertEqual(istek["govde"]["max_tokens"], 77)
        self.assertEqual(len(istek["govde"]["tools"]), len(arac_tanimlari()))
        self.assertEqual(sonuc["choices"][0]["message"]["tool_calls"][0]["function"]["name"], "degisiklik_yok")

    def test_anahtar_yoksa_yetki_basligi_gonderilmez(self):
        sunucu = SahteSunucu(govde=yanit([]))
        self.addCleanup(sunucu.kapat)
        VllmIstemcisi(sunucu.adres, "m").sohbet([], [])
        self.assertIsNone(sunucu.istekler[0]["yetki"])

    def test_http_hatasi_net_mesaj_verir(self):
        sunucu = SahteSunucu(durum=500, govde={"hata": "model yüklenmedi"})
        self.addCleanup(sunucu.kapat)
        with self.assertRaises(LlmHatasi) as ctx:
            VllmIstemcisi(sunucu.adres, "m").sohbet([], [])
        self.assertIn("500", str(ctx.exception))

    def test_yonlendirme_izlenmez(self):
        sunucu = SahteSunucu(durum=302, baslik={"Location": "http://example.com/dis"})
        self.addCleanup(sunucu.kapat)
        with self.assertRaises(LlmHatasi) as ctx:
            VllmIstemcisi(sunucu.adres, "m").sohbet([], [])
        self.assertIn("302", str(ctx.exception))
        self.assertEqual(len(sunucu.istekler), 1)

    def test_ulasilamayan_sunucu(self):
        sunucu = SahteSunucu()
        adres = sunucu.adres
        sunucu.kapat()
        with self.assertRaises(LlmHatasi):
            VllmIstemcisi(adres, "m", timeout=2).sohbet([], [])


class AnalizTests(TestCase):
    def setUp(self):
        self.well = Well.objects.create(ad="Arılı-1", referans_tipi="RKB", referans_yuksekligi=5)
        self.rapor = Report.objects.create(
            well=self.well, rapor_tarihi=date(2026, 2, 1), dosya="x.html",
            metin="Arılı-1  günlük rapor.\nCIBP 1100 m derinliğe set edildi.", durum=Report.Durum.METIN_HAZIR,
        )

    def test_arac_cagrilari_oneri_olur_kuyu_degismez(self):
        istemci = SahteIstemci([
            cagri("tapa_ekle", olay_tarihi="2026-02-01", dayanak_alinti="CIBP 1100 m derinliğe set edildi.",
                  guven="yuksek", birim="m", tur="cibp", ust_derinlik=1100),
            cagri("soru_sor", soru="Casing çapı nedir?"),
        ])
        oneriler = analiz_et(self.rapor, istemci=istemci)
        self.assertEqual(len(oneriler), 2)
        self.assertEqual(self.well.events.count(), 0)  # onay olmadan hiçbir şey değişmez
        self.assertTrue(all(o.durum == Proposal.Durum.ONAY_BEKLIYOR for o in oneriler))
        self.assertEqual(oneriler[0].uyarilar, [])
        self.rapor.refresh_from_db()
        self.assertEqual(self.rapor.durum, Report.Durum.ANALIZ_EDILDI)
        # Rapor metni veri olarak etiketlenir.
        mesajlar = istemci.kayit[0]["mesajlar"]
        self.assertEqual(mesajlar[0]["role"], "system")
        self.assertIn("<rapor>", mesajlar[1]["content"])

    def test_dayanaksiz_oneri_dusurulur_uydurma_alinti_uyarilir(self):
        istemci = SahteIstemci([
            cagri("tapa_ekle", olay_tarihi="2026-02-01", dayanak_alinti="", guven="yuksek", birim="m", tur="cibp"),
            cagri("tapa_ekle", olay_tarihi="2026-02-01", dayanak_alinti="rapor bunu hiç söylemedi",
                  guven="orta", birim="m", tur="rbp", ust_derinlik=900),
        ])
        oneriler = analiz_et(self.rapor, istemci=istemci)
        self.assertEqual(len(oneriler), 1)
        self.assertTrue(any("birebir bulunamadı" in u for u in oneriler[0].uyarilar))

    def test_bozuk_ve_bilinmeyen_cagrilar_atlanir(self):
        bozuk = {"function": {"name": "tapa_ekle", "arguments": "{bozuk"}}
        istemci = SahteIstemci([bozuk, cagri("sistemi_sil", x=1), cagri("degisiklik_yok", gerekce="yok")])
        oneriler = analiz_et(self.rapor, istemci=istemci)
        self.assertEqual([o.arac_adi for o in oneriler], ["degisiklik_yok"])
        self.rapor.refresh_from_db()
        self.assertIn("2 geçersiz", self.rapor.hata)

    def test_gecerli_cagri_yoksa_hata_ve_durum_degismez(self):
        with self.assertRaises(ValueError):
            analiz_et(self.rapor, istemci=SahteIstemci([]))
        self.rapor.refresh_from_db()
        self.assertEqual(self.rapor.durum, Report.Durum.METIN_HAZIR)
        self.assertEqual(self.rapor.oneriler.count(), 0)

    def test_beklenmeyen_yanit_bicimi_hata_verir(self):
        class Bozuk:
            def sohbet(self, mesajlar, araclar):
                return {"beklenmeyen": True}

        with self.assertRaises(ValueError):
            analiz_et(self.rapor, istemci=Bozuk())

    def test_bekleyen_oneri_varken_tekrar_analiz_yok(self):
        istemci = SahteIstemci([cagri("degisiklik_yok", gerekce="yok")])
        analiz_et(self.rapor, istemci=istemci)
        with self.assertRaises(ValueError):
            analiz_et(self.rapor, istemci=istemci)

    @override_settings(VLLM_BASE_URL="", VLLM_MODEL="")
    def test_ayar_yoksa_net_hata(self):
        with self.assertRaises(ImproperlyConfigured):
            analiz_et(self.rapor)
