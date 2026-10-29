# Well Sketch Webapp

Günlük raporlardan kuyu şemasını (well sketch) güncel tutan Django uygulaması. Claude, rapordaki değişiklikleri araç çağrılarıyla
**öneri** olarak üretir; kullanıcı onaylayınca kuyu durumu güncellenir ve sketch yeniden çizilir.

Proje bağlamı (hedefler, kararlar, kurallar): [context/README.md](context/README.md).

## Kurulum

```bash
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
cd src
../.venv/Scripts/python.exe manage.py migrate
../.venv/Scripts/python.exe manage.py createsuperuser
../.venv/Scripts/python.exe manage.py runserver
```

Rapor analizi için ortam değişkenleri (şablon: `.env.example`): `ANTHROPIC_API_KEY`, isteğe bağlı `CLAUDE_MODEL`.
Anahtar tanımlı değilse analiz düğmesi net bir hata verir; diğer her şey çalışır.

## Testler

```bash
cd src
../.venv/Scripts/python.exe manage.py test apps
```

Testler gerçek Claude API'sine çağrı yapmaz (sahte istemci kullanır).

## Yapı

- `src/apps/wells`: kuyu, ad geçmişi, olaylar, durum motoru (olaylardan baştan hesaplama), doğrulama
- `src/apps/reports`: rapor yükleme, PDF/HTML metin çıkarma
- `src/apps/llm`: Claude araç şemaları ve analiz servisi
- `src/apps/proposals`: öneri, onay/red/düzeltme akışı
- `src/apps/sketch`: durum JSON → SVG çizim
- `src/apps/photos`: tarihli fotoğraf yükleme

Şirket DB izleyici ve Playwright kazıyıcı bu sürümde yoktur (Aşama 4).
