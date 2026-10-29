"""Rapor dosyasından (PDF/HTML) metin çıkarma. OCR yoktur; taranmış PDF için uyarı verilir (B-05)."""
from pathlib import Path

from bs4 import BeautifulSoup
from pypdf import PdfReader


class MetinCikarmaHatasi(Exception):
    pass


def metin_cikar(dosya):
    """`dosya`: açık dosya nesnesi veya yol. (metin, uyarilar) döndürür."""
    ad = str(getattr(dosya, "name", dosya)).lower()
    uzanti = Path(ad).suffix
    if uzanti == ".pdf":
        return _pdf(dosya)
    if uzanti in (".html", ".htm"):
        return _html(dosya)
    raise MetinCikarmaHatasi("Desteklenen biçimler: PDF, HTML.")


def _pdf(dosya):
    try:
        okuyucu = PdfReader(dosya)
        metin = "\n".join((s.extract_text() or "") for s in okuyucu.pages).strip()
    except Exception as exc:
        raise MetinCikarmaHatasi(f"PDF okunamadı: {exc}") from exc
    uyarilar = []
    if not metin:
        uyarilar.append("PDF'ten metin çıkarılamadı; taranmış (görüntü) olabilir. OCR henüz yok.")
    return metin, uyarilar


def _html(dosya):
    icerik = dosya.read() if hasattr(dosya, "read") else Path(dosya).read_bytes()
    if isinstance(icerik, bytes):
        icerik = icerik.decode("utf-8", errors="replace")
    soup = BeautifulSoup(icerik, "html.parser")
    for etiket in soup(["script", "style"]):
        etiket.decompose()
    metin = soup.get_text("\n").strip()
    uyarilar = [] if metin else ["HTML dosyasında metin bulunamadı."]
    return metin, uyarilar
