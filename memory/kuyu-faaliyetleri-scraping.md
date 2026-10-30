---
name: kuyu-faaliyetleri-scraping
description: TPAO operasyon web sitesinden kuyu faaliyet raporlarını çekme yöntemi
metadata:
  type: project
---

# Kuyu Faaliyetleri Scraping

## Script: kuyu_faaliyetleri.py

TPAO operasyon web sitesinden (`https://operasyon.tpao.gov.tr`) herhangi bir kuyunun günlük faaliyet raporlarını çeken genel amaçlı script.

### Özellikler:
- Playwright ile TPAO sitesine bağlanır
- Kullanıcı adı/şifre ile giriş yapar (config.json)
- Kuyu adını Türkçe karakterlerden temizler:
  - ç → C
  - ı → I
  - ğ → G
  - ü → U
  - ş → S
  - ö → O
- Tüm raporları tek tek açar ve işler
- Saat bazlı faaliyetleri çıkarır

### Filtreleme Kuralları:
1. **00:00-08:00 faaliyetlerini atla** (son rapor hariç)
   - Sebep: 00:00-08:00 aralığı bir önceki güne ait faaliyet olur
   - İstisna: En son raporda başka faaliyet olmayacağı için 00:00-08:00 dahil edilir
2. **SN (Seramik Nozul) bölümünü atla** - kuyu donanım verileri faaliyet değil

### Output:
- `<kuyu_adi>_faaliyetler.json` - Tarih bazlı JSON
- `<kuyu_adi>_raporlar.png` - Screenshot

## Skill: kuyu-faaliyetleri

- **Trigger:** "kuyu adı verdiğinde", "faaliyetlerini çek", "faaliyet raporlarını al"
- **Komut:** `python kuyu_faaliyetleri.py <kuyu_adi>`
- **Dosya:** `.claude/skills/kuyu-faaliyetleri/SKILL.md`

## İlgili Dosyalar:
- `kuyu_faaliyetleri.py` - Ana script
- `.claude/skills/kuyu-faaliyetleri/SKILL.md` - Skill tanımı
- `config.json` - Giriş bilgileri (gizli, .gitignore'da olmalı)
