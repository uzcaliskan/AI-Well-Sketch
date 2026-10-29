"""Geometri ve tutarlılık kontrolleri (kurallar-ve-sinirlar.md §3).

İhlal engellemez; kullanıcıya uyarı olarak gösterilir. Kural kaynağı:
context/kuyu-tasarim-kurallari.md §3, §4, §9.
"""
from .state import BILGI_ARACLARI, derinlik_var_mi, kuyu_durumu, metre

ZORUNLU_CASING_ALANLARI = ["od_inc", "id_inc", "grade", "agirlik_ppf", "pabuc_derinlik"]


def dogrula(well, tip, veri, olay_tarihi):
    """Önerilen olay uygulandıktan sonraki durumu kontrol eder, uyarı listesi döndürür."""
    uyarilar = []
    if tip in BILGI_ARACLARI:
        return uyarilar

    if derinlik_var_mi(veri) and veri.get("birim") not in ("m", "ft"):
        uyarilar.append("Derinlik birimi (m/ft) belirtilmemiş; onaylamadan önce birim seçilmeli.")

    if tip == "casing_ekle":
        eksik = [a for a in ZORUNLU_CASING_ALANLARI if veri.get(a) in (None, "")]
        if veri.get("tur") != "liner" and veri.get("ust_derinlik") in (None, ""):
            eksik.append("ust_derinlik")
        if eksik:
            uyarilar.append("Casing için bilinmeyen zorunlu alanlar: " + ", ".join(eksik) + ".")
        if veri.get("tur") in ("yuzey", "ara", "uretim") and veri.get("ust_derinlik") not in (None, 0, 0.0):
            uyarilar.append("Yüzey/ara/üretim casing kuyu başından (0) başlamalı.")

    durum = kuyu_durumu(well, ek_olaylar=[(tip, veri, olay_tarihi)])
    uyarilar.extend(_casing_geometrisi(durum["casingler"]))
    return uyarilar


def _casing_geometrisi(casingler):
    uyarilar = []
    sirali = sorted(
        (c for c in casingler if metre(c.get("pabuc_derinlik")) is not None),
        key=lambda c: metre(c["pabuc_derinlik"]),
    )
    for dis, ic in zip(sirali, sirali[1:]):
        drift = dis.get("drift_id_inc")
        od = ic.get("od_inc")
        if isinstance(drift, (int, float)) and isinstance(od, (int, float)) and od >= drift:
            uyarilar.append(
                f"Casing OD ({od}\") bir önceki casing'in drift ID'sinden ({drift}\") küçük olmalı."
            )
    return uyarilar
