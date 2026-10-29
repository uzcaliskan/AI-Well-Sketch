# Hedefler

> Sayısal başarı ölçütleri (doğruluk oranı, gecikme, maliyet) kullanıcı tarafından henüz verilmedi.
> Bunlar uydurulmadı, [acik-sorular.md](acik-sorular.md) dosyasında soruldu.

## Ana hedef

Önce **en basit çalışan sürüm**: elle yüklenen günlük raporlardan, **vLLM modeli + kullanıcı onayı** ile bir kuyunun
well sketch'ini izlenebilir şekilde güncel tutmak. Otomasyon ve ölçek sonra gelir.

## Başlangıç sürümünün hedefleri

1. **Rapor yükleme:** Kullanıcı bir kuyuya PDF / HTML rapor yükler; metin çıkarılır.
2. **Değişiklik algılama:** LLM raporu kuyunun mevcut durumuyla karşılaştırıp yalnızca *yeni* olayları bulur.
3. **Tool calling ile öneri:** LLM değişiklikleri serbest metin değil, tanımlı araç çağrıları olarak üretir
   (taslak araç listesi: [llm-araclari.md](llm-araclari.md)).
4. **İnsan onayı:** Her öneri kullanıcıya gösterilir; onay / red / düzeltme sonrası uygulanır.
5. **Sketch çizimi:** Kuyunun yapılandırılmış (JSON) durumundan sketch çizilir; formasyon, casing, liner,
   çimento, tapa, packer, perforasyon, tubing ve kuyuda kalan malzeme gösterilir.
6. **Tarihçe:** Her değişiklik kaynak rapora ve tarihe bağlanır; kuyunun herhangi bir tarihteki görünümü yeniden üretilebilir.
7. **Fotoğraflar:** Kullanıcı kuyuya farklı tarihlerde fotoğraf yükler ve tarihe göre görür.
8. **Birimler:** Derinlikler m ve ft olarak tutulur; arayüzde combobox ile m / ft geçişi.

## Fonksiyonel olmayan hedefler

- **Doğruluk önce:** Raporda olmayan değer uydurulmaz; emin olunmayan durum kullanıcıya sorulur.
- **İzlenebilirlik:** Her öneri ve onay kim / ne zaman / hangi rapor bilgisiyle kaydedilir.
- **Model yapılandırılabilirliği:** vLLM adresi ve model adı yapılandırmadan verilir, kodda sabit değildir.
- **Veri dışarı çıkmaz:** LLM yalnızca şirket içi vLLM'dir (K-17).
- **Ölçeğe açık veri modeli (uzun vade):** yüzbinlerce kuyu, onbinlerce kullanıcı; başlangıçta bunun için altyapı kurulmaz.

## Aşamalar (öneri, kullanıcı onayı bekliyor)

| Aşama | İçerik |
|---|---|
| 0 | Proje bağlam dosyaları (tamam) |
| 1 | Veri modeli: kuyu, rapor, olay, öneri, fotoğraf (kodlandı) |
| 2 | Sketch çizimi (JSON → görsel) ve elle veri girişiyle test (kodlandı, örnek veriyle gözle kontrol edildi) |
| 3 | Rapor yükleme + LLM araç şemaları + öneri/onay akışı (kodlandı; gerçek vLLM sunucusu ve gerçek rapor ile denenmedi) |
| 4 | Şirket DB izleyicisi ve Playwright kazıyıcı (otomatik tetik) |
| 5 | Ölçek (PostgreSQL, iş kuyruğu), yetki, izleme |

## Kapsam dışı (şimdilik)

- Eski kuyuların geçmiş verisini veritabanından içe aktarma (K-16; yapıldığında tek toplu onay). Şimdiki hedef: yeni kuyunun sketch'ini boştan çizmek.
- Playwright kazıyıcı ve şirket DB izleyici kodu (Aşama 4).
- Kuyruk/zamanlayıcı, PostgreSQL geçişi, çok kullanıcılı yetki (Aşama 5).
- LLM'in onaysız değişiklik uygulaması.
- LLM'in doğrudan çizim üretmesi.
