# Context: Well Sketch Webapp

> Bu dosya projenin **neden** var olduğunu ve hangi ortamda çalışacağını anlatır.
> Kullanıcının verdiği bilgilere dayanır. Bilinmeyen her şey [acik-sorular.md](acik-sorular.md) dosyasındadır.

## 1. Problem

Sondajı yapılmış ve sonrasında workover operasyonları geçirmiş (veya geçirecek) kuyuların
kuyu şeması (well sketch) bugün raporlardan elle takip edilmek zorunda. Bir kuyunun hikâyesi
şöyledir:

sondaj → tamamlama → üretim veya terk → workover'lar → nihai terk (P&A)

Her günlük rapor kuyunun durumunu değiştirebilir: yeni casing inilir, çimento yapılır,
perforasyon açılır, tapa konur, packer set edilir, kuyuda balık kalır, tubing değişir vb.
Bu değişikliklerin sketch'e doğru ve zamanında yansıması gerekir.

## 2. Çözüm (başlangıç sürümü: en basit hâl)

Proje önce **en basit şekilde** kurulur; otomasyon sonraki aşamalara bırakılır. Başlangıç sürümü:

1. Kullanıcı bir kuyuya **günlük raporu elle yükler** (PDF veya HTML).
2. Rapordan metin çıkarılır.
3. **LLM (şirket içi vLLM, Qwen3.5 397B)** raporu okur, kuyunun mevcut durumuyla karşılaştırır, değişiklikleri algılar ve
   tanımlı **araçları (tool calling)** çağırarak değişiklik **önerileri** üretir.
4. Öneriler **kullanıcı onayına** düşer. Kullanıcı onaylamadan hiçbir değişiklik uygulanmaz.
5. Onaylanan değişiklikler kuyunun yapılandırılmış durumuna (JSON) işlenir ve sketch bu veriden yeniden çizilir.
6. Kullanıcı kuyuya **farklı tarihlerde fotoğraf** yükleyebilir.

### Sonraki aşama (ertelendi, plan olarak duruyor)

Raporlar şirket web sitesinde güncellenir ve şirket veritabanına aktarılır. Uygulama şirket DB'sini **salt okunur** izler,
bir kuyu güncellenince raporu **Playwright** ile alır ve süreci otomatik başlatır
(pseudo kod: [sirket-db-izleme-pseudo.md](sirket-db-izleme-pseudo.md)). Bu kısım için kod şimdi yazılmaz.

## 3. Sketch'te gösterilecek bilgiler

Kullanıcının saydıkları ve [kuyu-tasarim-kurallari.md](kuyu-tasarim-kurallari.md) kural tabanına göre:

- Formasyonlar (tepe/taban derinlikleri, adları)
- Casing ve liner'lar (OD, ID, drift ID, grade, ağırlık, üst/pabuç derinliği; float collar/shoe, hanger)
- Çimento işleri (TOC ve kaynağı, kademeli çimentolama, DV tool, sorunlar, squeeze'ler, bağ kalitesi)
- Tapalar ve çimento tapaları (CIBP, RBP, çimento tapa, retainer, sand plug) ve PBTD
- Packer'lar ve tamamlama ekipmanları (tubing, SSSV, nipple, sliding sleeve, yapay kaldırma)
- Perforasyonlar (aralık, SPF, faz, durum: açık / squeeze'li / tapa altında)
- Kuyuda kalan malzeme (balık) ve tepe derinliği
- Workover notları (asit, frac, patch, kum temizliği, sidetrack)

## 4. Ana akış (başlangıç sürümü)

```
Kullanıcı: rapor yükler (PDF / HTML)
        │
        ▼
Metin çıkarma  →  uygulama DB: rapor kaydı (ham dosya + metin)
        │
        ▼
LLM (şirket içi vLLM)
  girdi: rapor metni + kuyunun mevcut JSON durumu + kural tabanı
  çıktı: tool call'lar  →  "değişiklik önerisi"
        │
        ▼
Doğrulama (geometri ve tutarlılık kuralları; uyarı verir, engellemez)
        │
        ▼
Kullanıcı onay ekranı  ── reddet / düzelt / onayla
        │ onay
        ▼
Kuyu durumu (JSON, olay geçmişiyle) güncellenir  →  Sketch yeniden çizilir
```

## 5. Aktörler

| Aktör | Rolü |
|---|---|
| Kullanıcı | Rapor yükler, önerileri onaylar/düzeltir, sketch'i görüntüler, fotoğraf yükler. Rol ayrımı henüz belirlenmedi. |
| LLM (şirket içi vLLM) | Raporu yorumlar, değişiklikleri tool call olarak önerir. Doğrudan veri değiştirmez, çizim yapmaz. Veri şirket ağından çıkmaz (K-17). |
| Şirket web sitesi / şirket DB / izleyici / Playwright | **Sonraki aşama.** Otomatik rapor alımı ve tetik. Başlangıçta yok. |

## 6. Ölçek

- **Başlangıç:** tek kuyu, tek (veya birkaç) kullanıcı.
- **Uzun vadeli hedef:** yüzbinlerce kuyu, önümüzdeki yıllarda onbinlerce kullanıcı. Başlangıç sürümü bunu karşılamak zorunda değil,
  ama veri modeli bunu engellemeyecek şekilde kurulur (kuyu başına olay geçmişi, sayfalı listeler).

## 7. Teknoloji

| Katman | Seçim | Durum |
|---|---|---|
| Web / arayüz | Django | Kararlaştırıldı |
| Veritabanı | SQLite (başlangıç) | Kararlaştırıldı; ölçekte PostgreSQL'e geçiş sonra değerlendirilir |
| LLM | vLLM üzerinde Qwen3.5 397B (OpenAI uyumlu API, tool calling, `requests` ile) | Kararlaştırıldı; adres ve model adı yapılandırmadan verilir |
| Rapor formatı | PDF (HTML olabilir) | Bilgi; PDF'in metin mi taranmış mı olduğu açık soru |
| Kazıma | Playwright | Ertelendi (sonraki aşama) |

## 8. Çalışma ortamı: iki bilgisayar

Kullanıcı projeyi iki farklı bilgisayarda yürütür (kullanıcı, 2026-10-29):

| Bilgisayar | Rolü | Erişimler |
|---|---|---|
| Kişisel | Proje ana hatları: tasarım, bağlam dosyaları, kod iskeleti, sahte veriyle testler | Şirket ağına ve vLLM'e erişim yok; gerçek şirket verisi yok |
| Şirket | Uygulama ve gerçek ortam: şirket içi vLLM ile uçtan uca deneme, gerçek raporlar | Şirket ağı, vLLM, şirket verisi |

- İki bilgisayar arasındaki **tek taşıma yolu git deposudur**. Göndermek için `git-push` becerisi kullanılır
  (veri sızıntısı ve test kontrolünden sonra commit + push); diğer bilgisayardaki değişiklikleri almak için `git-pull` becerisi kullanılır
  (yalnızca fast-forward; yerel çalışmayı ezmez). Her iki bilgisayarda da ilk açılışta `context/README.md` okunur.
- **Şirket bilgisayarında çalışma şartları, en az kişisel bilgisayardaki kadar sıkı olmalıdır:** aynı `CLAUDE.md` ve `context/` kuralları geçerlidir,
  testler aynı komutlarla çalıştırılır, push'tan önce aynı kontrol yapılır. Şirket bilgisayarında hiçbir kural gevşetilmez.
- **KIRMIZI ÇİZGİ: şirket verisi hiçbir şekilde dışarı sızmaz** (K-17). Şirket bilgisayarındaki gerçek rapor, kuyu verisi, veritabanı, fotoğraf,
  sunucu adresi/anahtar ve `.env` içeriği git'e, yani kişisel bilgisayara veya herhangi bir dış servise de gitmez. Şüphe varsa push edilmez, kullanıcıya sorulur.
- Ortama özgü ayarlar (`VLLM_BASE_URL`, `VLLM_MODEL`, `VLLM_IZINLI_HOSTLAR`, anahtarlar) her bilgisayarda yerel `.env` içinde tutulur; repoya girmez.
- Kişisel bilgisayarda gerçek vLLM denenemez; testler sahte sunucu/istemci kullanır. Gerçek uçtan uca doğrulama yalnızca şirket bilgisayarında yapılır.

## 9. Kaynak dosyalar

- Kural tabanı: [kuyu-tasarim-kurallari.md](kuyu-tasarim-kurallari.md)
- Hedefler: [hedefler.md](hedefler.md)
- Kararlar: [kararlar.md](kararlar.md)
- Kurallar ve sınırlar: [kurallar-ve-sinirlar.md](kurallar-ve-sinirlar.md)
- Açık sorular: [acik-sorular.md](acik-sorular.md)
