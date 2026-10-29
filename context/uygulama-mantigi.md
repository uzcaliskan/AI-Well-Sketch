# Uygulama Mantığı (başlangıç sürümü kodu)

> `src/` altındaki kodun **neden böyle çalıştığı**. Kod yapısını okumakla anlaşılmayan tasarım kararlarını içerir.
> Kavramsal model: [veri-modeli.md](veri-modeli.md) · Karar kayıtları: [kararlar.md](kararlar.md) · Araç tasarım notu: [llm-araclari.md](llm-araclari.md).
> Son güncelleme: 2026-10-29. Çalıştırma komutları: [../README.md](../README.md).

## Akış (koddaki karşılığı)

1. `reports/views.py` rapor yükler → `reports/extraction.py` metin çıkarır (PDF: pypdf, HTML: BeautifulSoup; OCR yok). Raporda kuyunun güncel/eski adlarından biri geçmiyorsa uyarı üretir (K-13).
2. `llm/service.py: analiz_et` raporu, rapor tarihindeki kuyu durumuyla birlikte Claude'a gönderir (`tool_choice: any`, her yanıt en az bir araç çağrısı). Rapor metni `<rapor>` etiketinde **veri** olarak verilir.
3. Her araç çağrısı bir `Proposal` kaydı olur. Kuyu verisi değişmez.
4. `proposals/views.py` onay/red/düzeltme akışı. Onay `Event` üretir.
5. `wells/state.py: kuyu_durumu` olaylardan durumu **her seferinde baştan** hesaplar → `sketch/render.py` SVG çizer.

## Temel tasarım kararları

- **Kaynak doğruluk olaylardır** (`Event`: değiştirilmez). Durum önbelleğe/snapshot'a alınmaz; geçmiş bir olay eklenirse sketch kendiliğinden doğru çıkar (K-15). Olaylar `olay_tarihi`, sonra `id` sırasıyla uygulanır.
- **Derinlik normalizasyonu:** Olay verisinde adı `derinlik` ile biten sayısal alanlar (ör. `ust_derinlik`, `pabuc_derinlik`) `birim` alanına göre durumda `{"m", "ft"}` çiftine çevrilir (iç içe listelerde de). Yeni bir derinlik alanı eklenirken adı `...derinlik` ile bitmelidir.
- **Birim zorunlu:** Derinlik içeren olayda `birim` yoksa uyarı verilir ve onay engellenir (birim tahmin edilmez).
- **Araç → olay eşlemesi** `state.py: uygula` içindedir: `*_ekle` araçları listeye öğe ekler (öğenin `id`'si olay id'sidir); `*_guncelle`, `*_durumu_degistir`, `*_kaldir` öğeye `hedef_id` ile başvurur. Claude durumdaki `id`'leri görür. `soru_sor`, `uyari_ver`, `degisiklik_yok` olay üretmez (`BILGI_ARACLARI`).
- **Orijinal öneri korunur:** Kullanıcı JSON'u düzeltip onaylarsa düzeltilmiş hâl `Event.veri`'de, LLM'in orijinal çıktısı `Proposal.parametreler`'de kalır (durum DUZELTILDI).
- **Dayanak:** Dayanak alıntısı boş olan öneri kaydedilmez; alıntı rapor metninde birebir (boşluk/büyük-küçük harf normalize) bulunamazsa uyarı eklenir.
- **Doğrulama engellemez:** `wells/validation.py` yalnızca uyarı üretir. Şu an kontrol edilenler: casing OD < önceki casing drift ID, eksik zorunlu casing alanları, yüzey/ara/üretim casing üstü 0, birim eksikliği. Kural tabanındaki diğer kontroller yazılmadı. Varsayımsal olay duruma sona eklenerek denenir (olay tarihine göre araya sokulmaz).
- **Sketch:** Tapa altındaki `acik` perforasyon çizimde "izole" (turuncu) gösterilir; bu durum olaya yazılmaz, çizimde türetilir (kural tabanı §9).
- **Ad geçmişi:** `Well.save()` ad değişince eski `WellName` kaydını kapatır, yenisini açar. `Well.ada_gore_bul` güncel ve eski adlarla eşleşir.
- **Erişim:** Tüm görünümler `login_required`. Onaylayan ve yükleyen kullanıcı kaydedilir. Rol ayrımı yok (B-06 açık).
- **Yapılandırma:** `ANTHROPIC_API_KEY`, `CLAUDE_MODEL` (varsayılan `claude-sonnet-5-5`, kullanıcı seçmedi), `DJANGO_DB_PATH` ortam değişkenleridir. Anahtar yoksa analiz düğmesi net hata verir, uygulamanın geri kalanı çalışır.
- **Senkron analiz:** Claude çağrısı web isteği içinde yapılır (kuyruk yok, B-02 ertelendi).

## Testler

`cd src` → `manage.py test apps`. Claude çağrısı sahte istemciyle test edilir; gerçek API'ye çağrı yapılmaz.

## Doğrulanmayanlar

- Gerçek Claude API ve gerçek rapor ile uçtan uca deneme yapılmadı; araç şemaları gerçek raporlara göre ayarlanmadı.
- Rapor metni Claude API'ye gider; şirket verisi için izin durumu açık (acik-sorular #13).
- Taranmış PDF'ler (OCR yok) desteklenmez.
