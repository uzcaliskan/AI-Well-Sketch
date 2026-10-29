# Şirket Veritabanı İzleme — Pseudo Kod

> **Sonraki aşama (Aşama 4).** Başlangıç sürümünde rapor elle yüklenir (kararlar.md K-00). LLM artık Claude API'dir (K-04);
> aşağıda geçen "llm" adımı buna karşılık gelir.

> Gerçek kod DEĞİLDİR. Şirket DB yapısı bilinmediği için tablo/sütun adları **yer tutucudur**
> (`<KUYU_TABLOSU>`, `<RAPOR_TABLOSU>`, `<GUNCELLEME_SUTUNU>` vb.). Cevap bekleyen sorular: acik-sorular.md #3.
> İlgili karar: kararlar.md K-03. Kurallar: kurallar-ve-sinirlar.md §5.

## Varsayımlar (teyit edilmeli)

- Şirket DB'sinde her raporun kuyuya bağlı bir kaydı var.
- Kayıtta güncellemeyi gösteren bir alan var (son güncelleme zamanı **veya** artan ID/sürüm).
- Kayıttan raporun web adresi veya kimliği bulunabiliyor; Playwright bununla raporu açacak.

## 1. Periyodik kontrol (zamanlayıcı her N dakikada çalıştırır)

```
FONKSİYON sirket_db_kontrol_et():
    kilit = al_kilit("sirket_db_izleyici")          # aynı anda iki izleyici çalışmasın
    EĞER kilit alınamadıysa: ÇIK

    imlec = uygulama_db.oku("izleyici_imleci")        # en son işlenen nokta (zaman damgası ve/veya ID)

    # Sadece okuma bağlantısı; sayfalı ve indeksli sorgu
    TEKRARLA:
        kayitlar = sirket_db.sorgula(
            SELECT rapor_id, kuyu_kodu, rapor_tarihi, rapor_adresi, <GUNCELLEME_SUTUNU>
            FROM <RAPOR_TABLOSU>
            WHERE (<GUNCELLEME_SUTUNU>, rapor_id) > (imlec.zaman, imlec.id)
            ORDER BY <GUNCELLEME_SUTUNU>, rapor_id
            LIMIT SAYFA_BOYUTU
        )
        EĞER kayitlar boşsa: DÖNGÜDEN ÇIK

        HER kayit İÇİN kayitlar:
            degisiklik_isle(kayit)
            imlec = (kayit.<GUNCELLEME_SUTUNU>, kayit.rapor_id)

        uygulama_db.yaz("izleyici_imleci", imlec)      # her sayfadan sonra kaydet; çökme olursa kaldığı yerden devam
    
    kilidi_birak(kilit)
```

## 2. Tek bir değişikliği işleme

```
FONKSİYON degisiklik_isle(kayit):
    kuyu = uygulama_db.kuyu_bul(kayit.kuyu_kodu)
    EĞER kuyu yoksa:
        kuyu = uygulama_db.kuyu_olustur(kayit.kuyu_kodu)   # veya kullanıcıya "eşleşmeyen kuyu" uyarısı (açık soru)

    # Aynı güncelleme iki kez işlenmesin (idempotent)
    anahtar = (kayit.rapor_id, kayit.<GUNCELLEME_SUTUNU>)
    EĞER uygulama_db.rapor_surumu_var_mi(anahtar): DÖN

    rapor = uygulama_db.rapor_kaydi_olustur(
        kuyu, sirket_rapor_id = kayit.rapor_id, rapor_tarihi = kayit.rapor_tarihi,
        kaynak_adres = kayit.rapor_adresi, durum = "KAZIMA_BEKLIYOR"
    )

    kuyruga_ekle(rapor_kazi, rapor.id)               # uzun işler arka planda
```

## 3. Sonraki adımlar (arka plan işleri, zincir)

```
İŞ rapor_kazi(rapor_id):                           # Playwright — kod sonra yazılacak
    dosya = playwright_ile_raporu_ac_ve_indir(rapor.kaynak_adres)   # PDF veya HTML
    rapor.ham_dosya = sakla(dosya); rapor.durum = "METIN_BEKLIYOR"
    kuyruga_ekle(metin_cikar, rapor_id)

İŞ metin_cikar(rapor_id):
    rapor.metin = pdf_veya_html_metin(rapor.ham_dosya)   # taranmış PDF ise OCR (açık soru)
    rapor.durum = "LLM_BEKLIYOR"
    kuyruga_ekle(llm_analiz, rapor_id)

İŞ llm_analiz(rapor_id):
    # Aynı kuyunun raporları tarih sırasıyla işlenir (kuyu başına sıralı kuyruk)
    durum = kuyu_guncel_durumu(rapor.kuyu)
    cagrilar = llm.tool_calling(rapor.metin, durum, kural_tabani, araclar)
    HER cagri İÇİN cagrilar:
        uyarilar = dogrula(cagri, durum)              # kurallar-ve-sinirlar.md §3
        oneri_olustur(rapor, cagri, uyarilar, durum = "ONAY_BEKLIYOR")
    rapor.durum = "ONAY_BEKLIYOR"
    kullaniciya_bildir(rapor.kuyu)                    # bildirim yöntemi açık soru
```

## 4. Hata durumları

```
- Şirket DB'ye bağlanılamazsa: imleç ilerletilmez, sonraki turda tekrar denenir, hata loglanır.
- Playwright raporu açamazsa: rapor.durum = "KAZIMA_HATASI", artan aralıklarla N kez tekrar, sonra kullanıcıya göster.
- LLM hatası / zaman aşımı: rapor.durum = "LLM_HATASI", tekrar dene; öneri üretilmez, kuyu durumu değişmez.
- Bir rapor hata verirse aynı kuyunun sonraki raporları beklemeye alınır (olay sırası bozulmasın).
```
