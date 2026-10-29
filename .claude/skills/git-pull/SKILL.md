---
name: git-pull
description: Kullanıcı “pull et”, “git’ten çek”, “son değişiklikleri al”, “diğer bilgisayardaki değişiklikleri getir” veya aynı anlama gelen bir ifade kullandığında uzak depodaki değişiklikleri yerel çalışmayı bozmadan güvenli biçimde almak için kullan.
---

# Git Pull

Bu beceri, diğer bilgisayardan push edilen değişiklikleri bu bilgisayara güvenli biçimde alır (iki bilgisayarlı çalışma: `context/context.md` §8).
Yerel çalışmayı ezmemek için yalnızca hızlı ileri sarma (fast-forward) ile çeker. Proje kuralı: **şirket verisi dışarı çıkmaz** (`context/kararlar.md` K-17, K-18).

## Adımlar

1. **Durumu incele.** `git status --short`, `git branch --show-current`, `git remote -v` çalıştır.
   - Uzak adres yoksa veya yer tutucu içeriyorsa dur ve kullanıcıdan gerçek adresi iste.
   - Uzak adresi ve dal adını kullanıcıya göster; beklenenden farklıysa onay al.
   - Commit edilmemiş yerel değişiklik varsa çekmeden önce kullanıcıya bildir ve ne yapılacağını sor (önce commit/`git-push`, saklamak vb.); kendiliğinden `stash`, `reset` veya `checkout --` yapma.

2. **Uzak durumu getir.** `git fetch origin` çalıştır. Ardından `git log --oneline HEAD..origin/<dal>` ve `git diff --stat HEAD...origin/<dal>` ile gelecek commit ve dosyaları kullanıcıya özetle.
   - Gelecek bir şey yoksa bunu bildir ve dur.
   - Gelen dosyalar arasında `.env`, `*.sqlite3`, `media/`, `*.pdf`, `raporlar/` veya gerçek veri gibi görünen dosya varsa **dur** ve kullanıcıya bildir (veri sızıntısı işareti olabilir, K-17).

3. **Çek.** `git pull --ff-only origin <dal>`.
   - Hızlı ileri sarma mümkün değilse (iki tarafta da yeni commit var) dur, durumu açıkla ve kullanıcıya sor; kendiliğinden merge, rebase, `--force` veya `reset --hard` yapma.
   - Kimlik doğrulama hatasında kullanıcıdan oturum açmasını iste; parola veya token’ı sen girme.

4. **Sonrasını kontrol et.**
   - `context/` altında dosya eklendi, taşındı, silindi veya yeniden adlandırıldıysa `context/README.md` haritasını okuyarak güncel olup olmadığına bak; tutarsızlık varsa kullanıcıya bildir.
   - Bağımlılıklar (`requirements.txt`) veya veritabanı modelleri (`migrations/`) değiştiyse kullanıcıya bildir; kurulum/migrate komutlarını kendiliğinden çalıştırma, öner.
   - Kod değiştiyse isteğe bağlı olarak testleri çalıştır: `cd src` → `../.venv/Scripts/python.exe manage.py test apps`. Sadece belge değiştiyse atla ve belirt.

5. **Raporla.** Alınan commit’ler (kısa liste), değişen dosya sayısı, gerekli sonraki adımlar (migrate, bağımlılık, `.env` farkı). Yapılamayanı yapılmış gibi gösterme.

## Yapma

- Kullanıcı istemeden pull etme.
- `--force`, `reset --hard`, `clean`, otomatik merge/rebase kullanma; yerel çalışmayı silme.
- Depo yapılandırmasını (`git config`) veya uzak adresi kullanıcıya sormadan değiştirme.
- Diğer bilgisayara özgü ayarları (`.env`) bu bilgisayara taşımaya çalışma; ortam ayarları her bilgisayarda yerel kalır.
