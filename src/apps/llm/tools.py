"""LLM araç şemaları, OpenAI uyumlu `tools` biçiminde (taslak liste: context/llm-araclari.md).

Araçlar veri değiştirmez; her çağrı bir öneri kaydına dönüşür (K-05).
"""
from apps.wells.state import BILGI_ARACLARI


def _sayi(aciklama):
    return {"type": "number", "description": aciklama}


def _metin(aciklama, secenekler=None):
    sema = {"type": "string", "description": aciklama}
    if secenekler:
        sema["enum"] = secenekler
    return sema


def _dizi_metin(aciklama):
    return {"type": "array", "items": {"type": "string"}, "description": aciklama}


ORTAK = {
    "olay_tarihi": _metin("Operasyonun tarihi, YYYY-MM-DD (rapor tarihinden farklı olabilir)."),
    "dayanak_alinti": _metin("Değişikliği destekleyen cümle/satır; rapordan BİREBİR alıntı."),
    "guven": _metin("Çıkarımın güveni.", ["yuksek", "orta", "dusuk"]),
    "birim": _metin("Raporda kullanılan derinlik birimi.", ["m", "ft"]),
    "bilinmiyor": _dizi_metin("Raporda bulunmayan, boş bırakılan alanların adları."),
}
ORTAK_ZORUNLU = ["olay_tarihi", "dayanak_alinti", "guven", "birim"]

HEDEF_ID = {"type": "integer", "description": "Mevcut kuyu durumundaki öğenin `id` değeri."}
DER = "derinlik (raporun biriminde, sayı)"

# ad -> (açıklama, özel alanlar, ek zorunlu alanlar)
DEGISTIREN = {
    "casing_ekle": (
        "Yeni conductor/yüzey/ara/üretim casing veya liner indi.",
        {
            "tur": _metin("Boru türü.", ["conductor", "yuzey", "ara", "uretim", "liner"]),
            "od_inc": _sayi("OD (inç)"), "id_inc": _sayi("ID (inç)"), "drift_id_inc": _sayi("Drift ID (inç)"),
            "grade": _metin("API grade, örn. J-55, N-80"), "agirlik_ppf": _sayi("Ağırlık (ppf)"),
            "ust_derinlik": _sayi("Üst " + DER), "pabuc_derinlik": _sayi("Pabuç " + DER),
            "baglanti": _metin("Bağlantı tipi (opsiyonel)"),
            "float_collar_derinlik": _sayi("Float collar " + DER), "float_shoe_derinlik": _sayi("Float shoe " + DER),
            "hanger_derinlik": _sayi("Liner hanger " + DER), "liner_top_packer_derinlik": _sayi("Liner top packer " + DER),
        },
        ["tur"],
    ),
    "casing_guncelle": (
        "Mevcut casing bilgisi değişti veya düzeltildi.",
        {"hedef_id": HEDEF_ID, "degisen_alanlar": {"type": "object", "description": "Değişen alanlar ve yeni değerleri."}},
        ["hedef_id", "degisen_alanlar"],
    ),
    "cimento_isi_kaydet": (
        "Çimentolama, TOC ölçümü veya squeeze işi.",
        {
            "hedef_casing_id": {"type": "integer", "description": "Çimentolanan casing'in `id` değeri."},
            "toc_derinlik": _sayi("Çimento tepesi " + DER), "toc_kaynagi": _metin("CBL/CET, sıcaklık logu, hacim vb."),
            "kademe_durumu": _metin("Kademe durumu.", ["yapildi", "yapilamadi", "kismi"]),
            "dv_tool_derinlik": _sayi("DV tool " + DER),
            "sorunlar": _dizi_metin("Kayıp sirkülasyon, çimento yüzeye gelmedi, top job vb."),
            "bag_kalitesi": {"type": "array", "items": {"type": "object"}, "description": "ust_derinlik, alt_derinlik, kalite (iyi/zayif/yok)."},
            "squeeze": {"type": "boolean"}, "aciklama": _metin("Serbest açıklama"),
        },
        [],
    ),
    "perforasyon_ekle": (
        "Yeni perforasyon atıldı.",
        {
            "ust_derinlik": _sayi("Üst " + DER), "alt_derinlik": _sayi("Alt " + DER), "spf": _sayi("Atış yoğunluğu"),
            "faz_derece": _sayi("Faz açısı"), "tabanca_tipi": _metin("Tabanca tipi"), "zon": _metin("Zon/formasyon adı"),
        },
        ["ust_derinlik", "alt_derinlik"],
    ),
    "perforasyon_durumu_degistir": (
        "Perforasyon squeeze ile kapandı, tapa altında kaldı veya tekrar açıldı.",
        {"hedef_id": HEDEF_ID, "yeni_durum": _metin("Yeni durum.", ["acik", "squeeze", "tapa_altinda"])},
        ["hedef_id", "yeni_durum"],
    ),
    "tapa_ekle": (
        "CIBP, RBP, çimento tapa, retainer veya sand plug kondu.",
        {
            "tur": _metin("Tapa türü.", ["cibp", "rbp", "cimento_tapa", "retainer", "sand_plug"]),
            "ust_derinlik": _sayi("Üst " + DER), "alt_derinlik": _sayi("Alt " + DER),
            "cimento_kapagi_boyu": _sayi("Üzerindeki çimento kapağı boyu"),
            "pbtd_derinlik": _sayi("Rapor yeni PBTD veriyorsa " + DER),
        },
        ["tur", "ust_derinlik"],
    ),
    "tapa_kaldir": ("RBP çıkarıldı veya tapa delindi.", {"hedef_id": HEDEF_ID}, ["hedef_id"]),
    "packer_ekle_veya_kaldir": (
        "Packer set edildi veya çekildi.",
        {
            "islem": _metin("İşlem.", ["ekle", "kaldir"]), "tur": _metin("Packer türü"),
            "derinlik": _sayi("Packer " + DER), "hedef_id": HEDEF_ID,
        },
        ["islem"],
    ),
    "tamamlama_dizisi_guncelle": (
        "Tubing veya tamamlama ekipmanı değişti.",
        {
            "tubing_od_inc": _sayi("Tubing OD (inç)"), "tubing_id_inc": _sayi("Tubing ID (inç)"),
            "tubing_grade": _metin("Tubing grade"), "tubing_agirlik_ppf": _sayi("Tubing ağırlığı (ppf)"),
            "tubing_ayak_derinlik": _sayi("Tubing ayağı " + DER),
            "ekipman": {"type": "array", "items": {"type": "object"}, "description": "SSSV, nipple, sliding sleeve vb.: ad, derinlik."},
            "yapay_kaldirma": _metin("ESP, çubuklu pompa, gas lift"),
        },
        [],
    ),
    "balik_ekle_veya_kaldir": (
        "Kuyuda malzeme (balık) kaldı veya çıkarıldı.",
        {
            "islem": _metin("İşlem.", ["ekle", "kaldir"]), "tanim": _metin("Balığın tanımı"),
            "tepe_derinlik": _sayi("Balık tepesi " + DER), "uzunluk": _sayi("Uzunluk (aynı birim)"), "hedef_id": HEDEF_ID,
        },
        ["islem"],
    ),
    "kuyu_tabani_guncelle": (
        "PBTD veya TD değişti (kum temizliği, tapa vb.).",
        {"td_derinlik": _sayi("TD " + DER), "pbtd_derinlik": _sayi("PBTD " + DER), "neden": _metin("Neden")},
        [],
    ),
    "formasyon_ekle_veya_guncelle": (
        "Rapor formasyon tepesi/tabanı veriyor.",
        {"ad": _metin("Formasyon adı"), "tepe_derinlik": _sayi("Tepe " + DER), "taban_derinlik": _sayi("Taban " + DER)},
        ["ad"],
    ),
    "workover_notu_ekle": (
        "Geometriyi değiştirmeyen operasyon (asit, frac vb.).",
        {
            "tur": _metin("Operasyon türü"), "ust_derinlik": _sayi("Üst " + DER), "alt_derinlik": _sayi("Alt " + DER),
            "ayrinti": _metin("Asit tipi, hacim vb."),
        },
        ["tur"],
    ),
    "sidetrack_kaydet": (
        "Sidetrack: whipstock ve pencere.",
        {
            "whipstock_derinlik": _sayi("Whipstock " + DER), "pencere_derinlik": _sayi("Pencere " + DER),
            "aciklama": _metin("Açıklama"),
        },
        [],
    ),
}

BILGI = {
    "soru_sor": ("Emin olunmayan veya çelişkili durumda kullanıcıya soru sor.", {"soru": _metin("Soru")}, ["soru"]),
    "uyari_ver": ("Rapor kural tabanı veya mevcut durumla çelişiyor.", {"uyari": _metin("Uyarı")}, ["uyari"]),
    "degisiklik_yok": ("Rapor kuyunun yapısını değiştirmiyor.", {"gerekce": _metin("Kısa gerekçe")}, ["gerekce"]),
}
assert set(BILGI) == BILGI_ARACLARI


def arac_tanimlari():
    def arac(ad, aciklama, alanlar, zorunlu):
        return {
            "type": "function",
            "function": {
                "name": ad,
                "description": aciklama,
                "parameters": {"type": "object", "properties": alanlar, "required": zorunlu},
            },
        }

    araclar = []
    for ad, (aciklama, alanlar, zorunlu) in DEGISTIREN.items():
        araclar.append(arac(ad, aciklama, {**ORTAK, **alanlar}, ORTAK_ZORUNLU + zorunlu))
    for ad, (aciklama, alanlar, zorunlu) in BILGI.items():
        araclar.append(arac(ad, aciklama, alanlar, zorunlu))
    return araclar
