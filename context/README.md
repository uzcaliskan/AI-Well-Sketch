# Well Sketch Webapp — Bağlam Haritası

Günlük sondaj, tamamlama ve workover raporlarından kuyu şemasını (well sketch) güncel tutan web uygulaması.
**Başlangıç sürümü (en basit hâl):** kullanıcı raporu yükler, Claude API değişiklikleri tool calling ile **öneri** olarak üretir,
kullanıcı onaylayınca kuyu durumu güncellenir ve sketch yeniden çizilir. Şirket DB izleme ve Playwright sonraki aşamada.

> **Durum:** Başlangıç sürümü kodlandı (`src/`): kuyu, rapor yükleme, Claude önerisi, onay akışı, olay geçmişi, SVG sketch, fotoğraf.
> Kurulum ve çalıştırma: [../README.md](../README.md). Şirket DB izleyici ve Playwright yok (Aşama 4). Gerçek Claude API ile uçtan uca deneme henüz yapılmadı.

## Her görevde oku

| Dosya | İçerik |
|---|---|
| [context.md](context.md) | Problem, çözüm, ana akış, aktörler, ölçek, teknoloji |
| [kurallar-ve-sinirlar.md](kurallar-ve-sinirlar.md) | Onay, uydurmama, LLM sınırları, doğrulama, veri kuralları |
| [kararlar.md](kararlar.md) | Kabul edilen ve karar bekleyen kararlar |

## Göreve göre oku

| Dosya | Ne zaman |
|---|---|
| [hedefler.md](hedefler.md) | Kapsam, aşama veya öncelik konuşulurken |
| [acik-sorular.md](acik-sorular.md) | Belirsiz bir noktaya rastlanınca; cevap gelince buraya işlenir |
| [llm-araclari.md](llm-araclari.md) | Claude araç listesi (taslak); prompt, öneri/onay akışı veya araç şeması işi yapılırken |
| [veri-modeli.md](veri-modeli.md) | Kavramsal veri modeli (taslak); tablo/model, olay geçmişi veya durum JSON'u işi yapılırken |
| [uygulama-mantigi.md](uygulama-mantigi.md) | `src/` kodunu değiştirirken veya hata ayıklarken: tasarım kararları, durum motoru, onay akışı |
| [kuyu-tasarim-kurallari.md](kuyu-tasarim-kurallari.md) | Sketch, geometri, doğrulama, LLM prompt/araç tasarımı (mühendislik kural tabanı, esas) |
| [sirket-db-izleme-pseudo.md](sirket-db-izleme-pseudo.md) | Yalnızca Aşama 4 (şirket DB izleyici, otomatik tetik) konuşulurken |

## Akış (başlangıç sürümü)

```
Rapor yükle (PDF/HTML) → metin çıkar → Claude API (tool call) → doğrulama → kullanıcı onayı → kuyu olayı → durum (JSON) → sketch
```

## Kod yapısı

`src/apps/`: wells (kuyu, ad geçmişi, olay, durum motoru, doğrulama), reports (yükleme, `extraction.py` metin çıkarma),
llm (`tools.py` araç şemaları, `service.py` analiz), proposals (öneri ve onay), sketch (SVG çizim), photos.
Henüz yok (Aşama 4): watcher (şirket DB izleyici), scraper (Playwright). Araç şemalarının kaynağı artık `llm/tools.py`;
`llm-araclari.md` onun taslak tasarım notudur.

## Teknoloji

Django · SQLite (başlangıç) · Claude API · (sonra: PostgreSQL, Playwright, iş kuyruğu).

## Temel kurallar

1. LLM öneri üretir, kullanıcı onaylamadan hiçbir şey değişmez.
2. Raporda olmayan değer uydurulmaz, "bilinmiyor" yazılır.
3. Sketch yapılandırılmış veriden çizilir; LLM çizim yapmaz.
4. Her değişiklik kaynak rapora ve tarihe bağlıdır.
5. Basit tut: istenmeyen altyapı eklenmez.

## Eksikler

- `context/kaynaklar/` ve `kaynak-indeksi.md` yok (henüz kaynak eklenmedi; gerekmedikçe oluşturulmadı).
- LLM araç listesi ve kavramsal veri modeli taslak olarak kodlandı; kullanıcı onayı ve gerçek rapor örnekleriyle doğrulama bekliyor.
