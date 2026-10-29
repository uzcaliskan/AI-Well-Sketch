# Açık Sorular

> Cevaplanmamış her şey burada. Cevap gelince ilgili dosyaya işlenir ve buradan "Cevaplandı" bölümüne taşınır.

## Rapor ve veri kaynağı
1. **PDF türü:** Raporlar metin tabanlı PDF mi, taranmış görüntü mü? (Taranmışsa OCR gerekir.)
2. **Örnek rapor:** Kişisel/gizli bilgileri çıkarılmış 2–3 örnek rapor (sondaj, tamamlama, workover) paylaşılabilir mi?
3. **Şirket veritabanı:**
   - Hangi veritabanı (Oracle, MS SQL, PostgreSQL…)? Uygulamaya salt okuma erişimi verilebilir mi?
   - Kuyu ve rapor kayıtları hangi tablolarda? Bir güncellemeyi neyden anlarız (son güncelleme zamanı sütunu, sürüm numarası, artan ID, değişiklik tablosu)?
   - Kayıtta rapor içeriği mi var, yoksa sadece raporun web adresi/kimliği mi? (Playwright'ın neyi açacağını belirler.)
   - Ne sıklıkla kontrol edilmeli (ör. 5 dk, saatlik)? Şirket DB'si üzerindeki sorgu yükü için sınır var mı?
   - Aynı rapor sonradan düzeltilirse (revizyon) yeni kayıt mı açılıyor, mevcut kayıt mı değişiyor?
4. **Rapor-kuyu eşleşmesi:** Kuyu adı benzersiz ve güncellenebilir (cevaplandı). Raporda kuyu adı yazıyor ve eski adlar saklanacak (cevaplandı). Eşleşmeyen ad için uyarı verilir (cevaplandı).
5. **Rapor sıklığı:** Kuyu başına günde kaç rapor gelir? Toplam günlük rapor hacmi tahmini?
6. **Geçmiş kayıtlar:** Eski kuyuların sketch'i eski kayıtlarla çizilecek (K-16, cevaplandı). Eski kayıtlar veritabanından gelecek (cevaplandı). Kalan: hangi veritabanı/tablolar, kayıtlar rapor metni mi yapılandırılmış veri mi? Geriye dönük işlemenin yükü/maliyeti (yüzbinlerce kuyuda büyük) nasıl yönetilecek? **Ertelendi.**
7. **İçe aktarmada hangi LLM:** Kullanıcı eski kuyu işlemede Claude değil **yerel LLM** çalışacağını söyledi (ertelendi). Bu, K-04 (Claude API) ile nasıl birleşecek? Yerel LLM hangisi, nerede çalışacak? Henüz karar yok; K-04 değişmedi.
8. **Formasyon bilgisi:** Formasyon tepeleri raporlardan mı gelecek, başka bir kaynaktan mı (jeoloji veritabanı)?

## Kullanıcılar ve yetki
9. **Rol ayrımı:** Kim öneri onaylayabilir, kim sadece görüntüler? Kuyu/saha bazında yetki gerekir mi?
10. **Giriş:** Şirket içi kimlik sistemi (SSO / LDAP / Active Directory) kullanılacak mı?
11. **Erişim:** Uygulama sadece şirket ağında mı çalışacak, dışarıdan erişim olacak mı?

## LLM
12. **Claude modeli ve hesap:** Hangi Claude modeli kullanılacak? API anahtarı/hesap hazır mı? Maliyet için bir bütçe sınırı var mı?
13. **Veri gizliliği:** Rapor içerikleri Claude API'ye gönderilebilir mi (şirket politikası, gizlilik)? Gerçek raporlar test için kullanılabilir mi, yoksa anonimleştirme gerekir mi?

## Onay akışı
14. **Kısmi onay:** Kullanıcı bir rapordaki önerilerin bir kısmını onaylayıp diğerlerini reddedebilsin mi? (Öneri: evet.)
16. **Bildirim:** Onay bekleyen öneri olduğunda kullanıcıya bildirim (e-posta vb.) gidecek mi?

## Sketch ve arayüz
17. **Görünüm:** Beğendiğiniz örnek bir well sketch görseli var mı (stil, renkler, sembolleri belirlemek için)?
18. **Dışa aktarma:** Sketch PDF/PNG olarak indirilebilsin mi?
19. **Fotoğraflar:** Fotoğrafa tarih dışında not/derinlik/etiket eklenecek mi? Dosya boyutu/sayı sınırı var mı?

## Altyapı ve kararlar
20. **Dosya saklama:** Fotoğraf ve ham raporlar nerede saklanacak? Başlangıç önerisi yerel disk (B-03).
22. **Sunucu ortamı:** Uygulama nerede çalışacak (şirket sunucusu, bulut, Docker/Kubernetes)?
23. **Kod dili:** Kod içi tanımlayıcılar İngilizce, arayüz Türkçe olsun mu?

## Başarı ölçütleri
24. Kabul edilebilir doğruluk, rapor başına işlem süresi ve maliyet hedefleri neler?

## Cevaplandı
- Kuyu adı benzersiz ve güncellenebilir (Arılı-1 → Arılı-1/S). — 2026-10-28
- Başlangıç durumu: eski kuyular eski kayıtlarıyla çizilir, yeni kuyular boştan başlar. — 2026-10-28
- Rapordaki kuyu adı hiçbir güncel/eski adla eşleşmezse uyarı verilir, yeni kuyu otomatik açılmaz. — 2026-10-28
- Eski adlar saklanır; raporda kuyu adı yazar; eski tarihli kayıt güncellenirse sketch en baştan yeniden hesaplanır. — 2026-10-28
- Raporu yazan ve onaylayan aynı kişi; onay beklerken yeni rapor gelmeyecek. — 2026-10-28
- Veri değişirse (geriye dönük olay / revizyon) sketch ilgili olay tarihinden itibaren güncellenir. — 2026-10-28
- Proje önce en basit sürümle başlar; LLM = Claude API; başlangıç tek kuyu, SQLite, elle rapor yükleme. Şirket DB izleyici ve Playwright sonraya. — 2026-10-28
- (Geçersiz) Önceki vLLM/Qwen3.5 397B kararı Claude API ile değiştirildi; vLLM soruları kaldırıldı. — 2026-10-28
- Akış: süreç şirket veritabanını kontrol eder; kuyu kaydı güncellenince tetiklenir. Kod şimdilik yok, pseudo kod var. — 2026-10-27
- Rapor formatı: web penceresinde PDF, HTML olabilir. — 2026-10-27
- Değişiklikler önce kullanıcı onayına düşer. — 2026-10-27
- Ölçek: yüzbinlerce kuyu, onbinlerce kullanıcı. — 2026-10-27
