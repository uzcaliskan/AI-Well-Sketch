---
name: kuyu-faaliyetleri
description: Kullanıcı bir kuyu adı verdiğinde (örn. "ARILI-1", "Dodan-22", "Çamurlu-1"), TPAO operasyon web sitesinden o kuyunun tüm günlük faaliyet raporlarını çeker ve saat bazlı faaliyetleri JSON dosyasına kaydeder.
trigger: kuyu adı verdiğinde, faaliyetlerini çek, faaliyet raporlarını al, kuyu faaliyetleri
---

# Kuyu Faaliyetleri Çekme

**Script:** `kuyu_faaliyetleri.py`

**Komut:** `python kuyu_faaliyetleri.py <kuyu_adi>`

Bu beceri, verilen kuyu adının TPAO operasyon web sitesindeki (`https://operasyon.tpao.gov.tr`) tüm günlük faaliyet raporlarını çeker. Her rapordaki saat bazlı faaliyetleri (00:00-08:00 hariç, son rapor hariç) çıkarır ve JSON dosyasına kaydeder.

# Kuyu Faaliyetleri Çekme

Bu beceri, verilen kuyu adının TPAO operasyon web sitesindeki (`https://operasyon.tpao.gov.tr`) tüm günlük faaliyet raporlarını çeker. Her rapordaki saat bazlı faaliyetleri (00:00-08:00 hariç, son rapor hariç) çıkarır ve JSON dosyasına kaydeder.

## Kuyu Adı Hazırlama

Kullanıcı kuyu adını herhangi bir biçimde verebilir (örn. "arılı-1", "ARILI-1", "Arılı-1", "Çamurlu-1").

**Kural:** Kuyu adı büyük harflerle ve Türkçe karakter içermeyecek şekilde olmalıdır.

```python
def turkce_temizle(metin):
    """Türkçe karakterleri temizle ve büyük harfe çevir"""
    metin = metin.upper()
    turkce_karakterler = str.maketrans(
        "ıİğĞüÜşŞöÖçÇ",
        "IIGGUUS SOCC"
    )
    return metin.translate(turkce_karakterler)
```

**Örnekler:**
- "arılı-1" → "ARILI-1"
- "çamurlu-1" → "CAMURLU-1"
- "dodan-22" → "DODAN-22"
- "gökçe-1" → "GOKCE-1"

## Adımlar

1. **Kuyu adını hazırla.** Kullanıcının verdiği kuyu adını `turkce_temizle()` fonksiyonu ile temizle ve büyük harfe çevir.

2. **Scripti çalıştır.** `python kuyu_faaliyetleri.py <kuyu_adi_temiz>` komutunu çalıştır.
   - Script, TPAO operasyon web sitesine bağlanır
   - Kullanıcı adı ve şifre ile giriş yapar (`config.json`'dan okur)
   - Raporlar > Sondaj Raporları > Günlük Faaliyet Raporları sayfasına gider
   - Verilen kuyuyu seçer
   - Tüm raporları tek tek açar ve saat bazlı faaliyetleri çıkarır

3. **Faaliyet filtreleme kuralları:**
   - Sadece saat bazlı faaliyetleri al (00:00-08:00, 08:00-19:00, 19:00-00:00 gibi)
   - 00:00-08:00 faaliyetlerini **atla** (son rapor hariç)
   - SN (Seramik Nozul) bölümünü atla
   - Her rapor için faaliyetleri birleştirilmiş metin olarak da kaydet

4. **JSON dosyası oluştur.** `<kuyu_adi>_faaliyetler.json` dosyasını oluştur:

```json
{
  "kuyu_adi": "ARILI-1",
  "toplam_rapor": 63,
  "raporlar": {
    "31.08.2026": {
      "rapor_no": "63",
      "tarih": "31.08.2026",
      "toplam_faaliyet": 4,
      "faaliyetler": [...],
      "faaliyet_metni_birlesik": "..."
    }
  },
  "tum_faaliyetler_metni": "..."
}
```

5. **Screenshot al.** `<kuyu_adi>_raporlar.png` dosyasını kaydet.

6. **Raporla.**
   - Kaç rapor işlendi
   - Toplam kaç faaliyet bulundu
   - JSON ve PNG dosya adları

## Yapma

- Kuyu adını kullanıcıdan almadan scripti çalıştırma.
- Türkçe karakter temizlemesini atlama.
- 00:00-08:00 kuralını çiğneme (son rapor hariç).
- Kullanıcıya sormadan farklı kuyu adı kullanma.

## Örnek Kullanım

```
Kullanıcı: ARILI-1 kuyusunun faaliyetlerini çek
Claude: ARILI-1 kuyusu için tüm faaliyet raporları çekiliyor...
        [script çalışır]
        İşlem tamamlandı: arili-1_faaliyetler.json (63 rapor, 250 faaliyet)
```

```
Kullanıcı: çamurlu-1 kuyusunun faaliyetlerini al
Claude: Kuyu adı temizleniyor: ÇAMURLU-1 → CAMURLU-1
        CAMURLU-1 kuyusu için faaliyetler çekiliyor...
```
