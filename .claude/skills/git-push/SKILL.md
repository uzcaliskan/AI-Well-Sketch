---
name: git-push
description: Kullanıcı “push et”, “git’e gönder”, “değişiklikleri depoya gönder” veya aynı anlama gelen bir ifade kullandığında değişiklikleri veri sızıntısı ve test kontrolünden geçirip commit etmek ve uzak depoya push etmek için kullan.
---

# Git Push

Bu beceri, projedeki değişiklikleri güvenli biçimde commit edip uzak depoya gönderir. Push dış dünyada etkisi olan bir işlemdir:
yalnızca kullanıcı açıkça push istediğinde çalıştır. Proje kuralı: **şirket verisi dışarı çıkmaz** (`context/kararlar.md` K-17).

## Adımlar

1. **Durumu incele.** `git status --short`, `git branch --show-current`, `git remote -v` çalıştır.
   - Uzak adres yoksa veya yer tutucu içeriyorsa (`KULLANICI` gibi) dur ve kullanıcıdan gerçek adresi iste.
   - Uzak adresi ve dal adını kullanıcıya göster; beklenenden farklıysa onay al.
   - Gönderilecek değişiklik yoksa bunu bildir ve dur.

2. **Veri sızıntısı kontrolü.** İzlenmeyen klasörlerde kendi `.git` klasörü olan iç içe depo (örn. yanlışlıkla yapılmış bir `git clone`) varsa `git add -A` kullanma; onu ekleme, kullanıcıya bildir ve yalnızca gerekli yolları (`git add -u` ve yeni dosyaları adıyla) ekle. Ardından `git diff --cached --name-only` ile eklenecek dosyaları listele ve şunlardan biri varsa **dur**, eklemeyi geri al (`git restore --staged`) ve kullanıcıya bildir:
   - `.env` (`.env.example` hariç), `*.sqlite3`, `media/` altı, `.venv/`, `*.pdf`, `raporlar/` altı, gerçek rapor/fotoğraf/veritabanı dosyaları
   - İçeriğinde parola, API anahtarı, token veya özel anahtar olan dosyalar (`git diff --cached` çıktısında `password`, `api_key`, `secret`, `token`, `BEGIN PRIVATE KEY` ara; yer tutucu/şablon değerleri sorun değildir)
   - Bu bilgisayar şirket bilgisayarıysa ve şirketten GitHub’a gönderme izni teyit edilmediyse (`context/acik-sorular.md` #13) önce kullanıcıya sor.

3. **Testleri çalıştır** (kod değiştiyse): `cd src` → `../.venv/Scripts/python.exe manage.py test apps`. Başarısızsa push etme; çıktıyı bildir. Sadece belge değiştiyse testi atla ve bunu belirt.

4. **Commit et.** Kısa, açıklayıcı, Türkçe bir mesaj yaz (ne değişti, neden). Oturumda attribution satırı veriliyorsa mesajın sonuna ekle. `--no-verify` kullanma, mevcut commit’i `--amend` ile değiştirme.

5. **Push et.** `git push -u origin <dal>`.
   - `--force` / `--force-with-lease` kullanma.
   - Reddedilirse (uzak dalda yeni commit var) dur, nedeni bildir ve kullanıcıya sor; kendiliğinden `pull`/`rebase` yapma.
   - Kimlik doğrulama hatasında kullanıcıdan oturum açmasını iste; parola veya token’ı sen girme.

6. **Raporla.** Commit özeti (hash, dosya sayısı), push sonucu, atlanan veya başarısız kontroller. Yapılamayanı yapılmış gibi gösterme.

## Yapma

- Kullanıcı istemeden push etme; başka bir dala veya adrese gönderme.
- Depo yapılandırmasını (`git config`) veya uzak adresi kullanıcıya sormadan değiştirme.
- `.gitignore` ile dışarıda bırakılan dosyaları zorla (`git add -f`) ekleme.
