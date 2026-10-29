"""Kuyu durumu motoru.

Durum, onaylanmış olayların olay tarihi sırasıyla uygulanmasıyla **her seferinde baştan**
hesaplanır (kararlar.md K-09, K-15). Ara kayıt noktası (snapshot) kullanılmaz.
"""
import copy

FT = 0.3048

# Her araç çağrısında ortak olan alanlar; olay verisine girmez.
ORTAK_ALANLAR = {"olay_tarihi", "dayanak_alinti", "guven"}

# Veri değiştirmeyen araçlar: öneri olur ama olay üretmez.
BILGI_ARACLARI = {"soru_sor", "uyari_ver", "degisiklik_yok"}

EKLE = {
    "casing_ekle": "casingler",
    "cimento_isi_kaydet": "cimento_isleri",
    "perforasyon_ekle": "perforasyonlar",
    "tapa_ekle": "tapalar",
    "workover_notu_ekle": "workover_notlari",
    "sidetrack_kaydet": "sidetrackler",
}
EKLE_VEYA_KALDIR = {"packer_ekle_veya_kaldir": "packerlar", "balik_ekle_veya_kaldir": "baliklar"}


def bos_durum():
    return {
        "formasyonlar": [],
        "casingler": [],
        "cimento_isleri": [],
        "perforasyonlar": [],
        "tapalar": [],
        "packerlar": [],
        "tamamlama_dizisi": {},
        "baliklar": [],
        "kuyu_tabani": {},
        "workover_notlari": [],
        "sidetrackler": [],
    }


def cift_birim(deger, birim):
    m = deger * FT if birim == "ft" else float(deger)
    return {"m": round(m, 3), "ft": round(m / FT, 3)}


def derinlik_var_mi(veri):
    if isinstance(veri, dict):
        return any(
            (k.endswith("derinlik") and isinstance(v, (int, float)) and not isinstance(v, bool))
            or derinlik_var_mi(v)
            for k, v in veri.items()
        )
    if isinstance(veri, list):
        return any(derinlik_var_mi(v) for v in veri)
    return False


def normalize(obj, birim):
    """`*derinlik` anahtarlı sayıları {"m", "ft"} çiftine çevirir."""
    if isinstance(obj, dict):
        cikti = {}
        for k, v in obj.items():
            sayi = isinstance(v, (int, float)) and not isinstance(v, bool)
            if k.endswith("derinlik") and sayi and birim in ("m", "ft"):
                cikti[k] = cift_birim(v, birim)
            else:
                cikti[k] = normalize(v, birim)
        return cikti
    if isinstance(obj, list):
        return [normalize(v, birim) for v in obj]
    return obj


def _bul(liste, hedef_id):
    for oge in liste:
        if oge.get("id") == hedef_id:
            return oge
    return None


def uygula(durum, tip, veri, olay_id, olay_tarihi):
    """Tek bir olayı duruma uygular (durumu yerinde değiştirir)."""
    birim = veri.get("birim")
    v = normalize({k: x for k, x in veri.items() if k not in ORTAK_ALANLAR}, birim)
    v.pop("birim", None)
    meta = {"id": olay_id, "olay_tarihi": str(olay_tarihi)}

    if tip in EKLE:
        durum[EKLE[tip]].append({**v, **meta})
    elif tip == "casing_guncelle":
        oge = _bul(durum["casingler"], v.get("hedef_id"))
        if oge is not None:
            oge.update(v.get("degisen_alanlar") or {})
    elif tip == "perforasyon_durumu_degistir":
        oge = _bul(durum["perforasyonlar"], v.get("hedef_id"))
        if oge is not None:
            oge["durum"] = v.get("yeni_durum")
    elif tip == "tapa_kaldir":
        durum["tapalar"] = [t for t in durum["tapalar"] if t.get("id") != v.get("hedef_id")]
    elif tip in EKLE_VEYA_KALDIR:
        anahtar = EKLE_VEYA_KALDIR[tip]
        if v.get("islem") == "kaldir":
            durum[anahtar] = [o for o in durum[anahtar] if o.get("id") != v.get("hedef_id")]
        else:
            durum[anahtar].append({**v, **meta})
    elif tip == "tamamlama_dizisi_guncelle":
        durum["tamamlama_dizisi"].update(v)
    elif tip == "kuyu_tabani_guncelle":
        if "td_derinlik" in v:
            durum["kuyu_tabani"]["td"] = v["td_derinlik"]
        if "pbtd_derinlik" in v:
            durum["kuyu_tabani"]["pbtd"] = v["pbtd_derinlik"]
    elif tip == "formasyon_ekle_veya_guncelle":
        mevcut = next((f for f in durum["formasyonlar"] if f.get("ad") == v.get("ad")), None)
        if mevcut is None:
            durum["formasyonlar"].append({**v, **meta})
        else:
            mevcut.update(v)
    return durum


def kuyu_durumu(well, tarih=None, ek_olaylar=()):
    """Kuyunun durumunu baştan hesaplar. `tarih` verilirse o tarihe kadarki görünüm.

    `ek_olaylar`: (tip, veri, olay_tarihi) üçlüleri; doğrulama için varsayımsal uygulama.
    """
    durum = bos_durum()
    olaylar = well.events.all()
    if tarih is not None:
        olaylar = olaylar.filter(olay_tarihi__lte=tarih)
    for olay in olaylar:
        uygula(durum, olay.tip, olay.veri, olay.id, olay.olay_tarihi)
    for i, (tip, veri, olay_tarihi) in enumerate(ek_olaylar):
        uygula(durum, tip, veri, f"onerilen-{i}", olay_tarihi)
    return durum


def kopya(durum):
    return copy.deepcopy(durum)


def metre(deger):
    """Durumdaki derinlik değerini metreye çevirir; bilinmiyorsa None."""
    if isinstance(deger, dict):
        return deger.get("m")
    return None
