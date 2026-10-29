# Kararlar

> Her karar: tarih, durum, gerekçe, kaynak. Durumlar: **Kabul** (kullanıcı söyledi),
> **Kural tabanından** (kuyu-tasarim-kurallari.md), **Karar bekliyor** (öneri var, karar kullanıcının).

## Kabul edilenler

### K-00 · Önce en basit sürüm
- Tarih: 2026-10-28 · Durum: **Kabul**
- Proje önce en basit şekilde kurulur: tek kuyu, SQLite, elle rapor yükleme, Claude ile öneri, kullanıcı onayı, sketch.
  Şirket DB izleyici, Playwright, kuyruk ve ölçek sonraki aşamalara kalır.
- Bu karar K-02, K-03, K-07, K-12 ve B-02'nin kapsamını belirler (aşağıda).

### K-01 · Web katmanı Django
- Tarih: 2026-10-27 · Durum: **Kabul**
- Kaynak: kullanıcı ("frontend için django").

### K-02 · Raporlar Playwright ile kazınacak — ERTELENDİ
- Tarih: 2026-10-27 · Durum: **Kabul**, uygulama sonraya (Aşama 4) ertelendi (2026-10-28, K-00).
- Raporlar şirket web sitesinde, web penceresinde PDF (veya HTML) olarak açılıyor.
- Başlangıçta kullanıcı raporu elle yükler. Kazıyıcı kodu proje iskeleti oturduktan sonra yazılacak.

### K-03 · Şirket veritabanı kontrol edilerek otomatik tetik — ERTELENDİ
- Tarih: 2026-10-27 · Durum: **Kabul**, uygulama sonraya (Aşama 4) ertelendi (2026-10-28, K-00).
- Süreç şirket veritabanını kontrol eder; bir kuyunun kaydında güncelleme olduğunda süreç kendiliğinden çalışır.
- Uygulama şirket veritabanına **yazmaz**, sadece okur.
- Mantık pseudo kod olarak duruyor: `sirket-db-izleme-pseudo.md`. Kod şimdi yazılmaz.
- Değişikliği algılama yöntemi şirket DB yapısına bağlı → açık soru.

### K-04 · LLM: Claude API (tool calling)
- Tarih: 2026-10-28 (2026-10-27'deki vLLM/Qwen kararının yerine geçti) · Durum: **Kabul**
- Rapor analizi Claude API ile yapılır. Model adı ve API anahtarı yapılandırma / ortam değişkeninden verilir (kodda sabit değil).
- Hangi Claude modeli kullanılacağı henüz seçilmedi → açık soru. Kodda varsayılan `claude-sonnet-5-5`, `CLAUDE_MODEL` ile değişir.
- Kullanıcı (2026-10-28): "şimdilik Claude ile gidelim"; eski kuyu içe aktarmada yerel LLM konusu ertelendi (acik-sorular #7).

### K-05 · Önce kullanıcı onayı, sonra uygulama
- Tarih: 2026-10-27 · Durum: **Kabul**
- LLM'in tool call'ları doğrudan veriyi değiştirmez; "öneri" kaydı oluşturur. Kullanıcı onaylayınca uygulanır.

### K-06 · Tarihli fotoğraf yükleme
- Tarih: 2026-10-27 · Durum: **Kabul**
- Kullanıcı bir kuyuya farklı tarihlerde fotoğraf yükleyebilir.

### K-07 · Ölçek: başlangıç küçük, uzun vadeli hedef büyük
- Tarih: 2026-10-27, güncellendi 2026-10-28 · Durum: **Kabul**
- Başlangıç: tek kuyu. Uzun vadeli hedef: yüzbinlerce kuyu, onbinlerce kullanıcı.
- Başlangıç bu ölçek için altyapı kurmaz, ama veri modeli ölçeği engellemez.

### K-12 · Veritabanı: başlangıçta SQLite
- Tarih: 2026-10-28 · Durum: **Kabul** (K-00 kapsamında)
- Ölçek aşamasında PostgreSQL'e geçiş ayrıca değerlendirilir (JSONB kuyu durumuna uygun, eşzamanlı yazma).

### K-13 · Kuyu adı benzersizdir ve güncellenebilir
- Tarih: 2026-10-28 · Durum: **Kabul** (kaynak: kullanıcı)
- Kuyu adı benzersiz kimliktir; zamanla değişebilir (örn. `Arılı-1` → `Arılı-1/S`).
- Kuyu kaydı ad değişse de aynı kuyu olarak kalır (iç sabit kimlik), eski rapor ve olaylar bağlı kalır.
- Eski adlar saklanır (ad geçmişi). Raporda kuyu adı yazar; eşleştirme rapordaki ada göre yapılır ve eski ad da eşleşir (kullanıcı, 2026-10-28).

- Rapordaki ad hiçbir güncel veya eski adla eşleşmezse sistem **uyarı verir**, otomatik yeni kuyu açmaz (kullanıcı, 2026-10-28).

### K-14 · Raporu yazan ile öneriyi onaylayan aynı kişi
- Tarih: 2026-10-28 · Durum: **Kabul** (kaynak: kullanıcı)
- Onay verecek kişi raporu yazan kişidir; bu yüzden bir kuyuda onay beklerken yeni rapor gelmesi beklenmez.
- Bu nedenle "onay bekleyen öneri varken yeni rapor" için özel bir kuyruk/çakışma mantığı kurulmaz.

### K-15 · Veri değişince sketch ilgili tarihli olaydan itibaren yeniden hesaplanır
- Tarih: 2026-10-28 · Durum: **Kabul** (kaynak: kullanıcı)
- Veritabanında bir değişiklik olursa (geriye dönük tarihli olay veya rapor revizyonu) well sketch,
  değişen olayın tarihinden itibaren güncellenir; kuyu durumu olay geçmişinden türetildiği için (K-09) sonraki olaylar yeniden uygulanır.
- Eski tarihli bir kayıt güncellenirse sketch **en baştan** (ilk olaydan itibaren) yeniden hesaplanır; ara kayıt noktası (snapshot) kullanılmaz (kullanıcı, 2026-10-28).
- Varsayım (teyit edilmeli): düzeltilmiş rapordan çıkan değişiklikler de öneri olarak kullanıcı onayına düşer (K-05).

### K-16 · Başlangıç durumu: eski kuyular eski kayıtlarından, yeni kuyular boştan
- Tarih: 2026-10-28 · Durum: **Kabul** (kaynak: kullanıcı)
- Eski kuyuların verisi vardır: bu kuyuların well sketch'i **eski kayıtlarla** çizilir (kuyunun geçmişi olay geçmişi olarak kurulur).
- Yeni kuyularda hiçbir bilgi yoktur: sketch **boştan** başlar, ilk rapordan itibaren dolar.
- Eski kayıtlar **veritabanından** gelecek (kullanıcı, 2026-10-28). Kayıtların ayrıntısı (tablo, rapor mu yapılandırılmış veri mi) hâlâ açık.
- **Şimdiki kapsam:** yalnızca yeni bir kuyunun sketch'ini **boştan** çizmek. Eski kuyu içe aktarma şimdilik **ertelendi** (kullanıcı: "bu kısmı geçelim").
- İçe aktarma yapıldığında: tüm kayıtlar işlendikten sonra kuyu başına **tek bir toplu onay** sorulur (tek tek onay yok). Bu, K-05'in kullanıcı tarafından kabul edilmiş istisnasıdır; yalnızca eski kuyu içe aktarmasına uygulanır.

## Kural tabanından gelenler

### K-08 · Kuyu durumu yapılandırılmış veri (JSON); sketch bu veriden çizilir
- Kaynak: kuyu-tasarim-kurallari.md §13. LLM doğrudan çizim yapmaz.

### K-09 · Olay tabanlı tarihçe
- Kaynak: §1 ve §13. Her rapor bir olaydır; sketch olayların tarih sırasıyla uygulanmasının sonucudur.
  Her değişiklik kaynak rapora ve tarihe bağlanır.

### K-10 · Derinlik m ve ft; arayüzde m / ft combobox; sketch MD ile çizilir
- Kaynak: §12. Çap inç, ağırlık ppf. Referans noktası (RKB / DF / GL) her kuyuda kaydedilir.

### K-11 · Bilinmeyen değer uydurulmaz, "bilinmiyor" olarak işaretlenir; çelişki kullanıcıya sorulur
- Kaynak: §6 ve §13.

## Karar bekliyor

### B-02 · İş kuyruğu ve zamanlayıcı (Aşama 4–5)
- Başlangıçta gerekmez. Otomatik izleyici ve ölçek geldiğinde seçilecek (ör. Celery beat / RQ / cron + management komutu).
- Başlangıçta LLM çağrısının web isteğini bekletmesi sorun olursa basit bir arka plan çözümü değerlendirilir.

### B-03 · Fotoğraf ve ham rapor dosyalarının saklanacağı yer
- Başlangıç önerisi: yerel disk (`media/`). Ölçekte nesne depolama (S3 uyumlu) düşünülür.

### B-04 · Sketch çizim teknolojisi
- Seçenekler: sunucuda SVG üretimi, tarayıcıda SVG/Canvas (JS). Açık.

### B-05 · PDF'ten metin çıkarma yolu
- PDF metin tabanlıysa metin çıkarma kütüphanesi; taranmışsa OCR gerekir. PDF türü bilinmiyor (açık soru).

### B-06 · Kimlik doğrulama ve rol ayrımı
- Başlangıç tek kullanıcı olabilir. Kim öneri onaylayabilir, SSO/LDAP var mı? Açık.
