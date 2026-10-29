# Well Sketch Webapp

Günlük raporlardan kuyu şemasını (well sketch) güncel tutan Django uygulaması. Şirket içi vLLM modeli, rapordaki değişiklikleri araç çağrılarıyla
**öneri** olarak üretir; kullanıcı onaylayınca kuyu durumu güncellenir ve sketch yeniden çizilir. **Hiçbir veri şirket ağının dışına çıkmaz.**

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

Rapor analizi için ortam değişkenleri (şablon: `.env.example`): `VLLM_BASE_URL` (örn. `http://10.0.0.5:8000/v1`) ve `VLLM_MODEL`
(sunucuda servis edilen model adı). Sunucu alan adıyla veriliyorsa `VLLM_IZINLI_HOSTLAR`'a eklenmelidir; özel ağ dışındaki adresler reddedilir.
Bunlar tanımlı değilse analiz düğmesi net bir hata verir; diğer her şey çalışır. vLLM'in tool calling ile başlatılmış olması gerekir
(`--enable-auto-tool-choice`, modele uygun `--tool-call-parser`).

## Testler

```bash
cd src
../.venv/Scripts/python.exe manage.py test apps
```

Testler dış ağa çıkmaz (sahte istemci ve yalnızca 127.0.0.1'deki sahte sunucu).

## Yapı

- `src/apps/wells`: kuyu, ad geçmişi, olaylar, durum motoru (olaylardan baştan hesaplama), doğrulama
- `src/apps/reports`: rapor yükleme, PDF/HTML metin çıkarma
- `src/apps/llm`: araç şemaları, vLLM istemcisi (`requests`), analiz servisi
- `src/apps/proposals`: öneri, onay/red/düzeltme akışı
- `src/apps/sketch`: durum JSON → SVG çizim
- `src/apps/photos`: tarihli fotoğraf yükleme

Şirket DB izleyici ve Playwright kazıyıcı bu sürümde yoktur (Aşama 4).
