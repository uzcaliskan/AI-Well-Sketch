# LLM Araç Listesi (TASLAK)

> Claude'un tool calling ile çağırabileceği araçların **önerilen** listesi. Kullanıcı onaylamadı; isimler ve alanlar değişebilir.
> Alan içerikleri [kuyu-tasarim-kurallari.md](kuyu-tasarim-kurallari.md) kural tabanından türetilmiştir.
> Kurallar: [kurallar-ve-sinirlar.md](kurallar-ve-sinirlar.md) §1–3. Karar: [kararlar.md](kararlar.md) K-04, K-05.

## Genel ilkeler

- **Araçlar veri değiştirmez.** Her çağrı bir *öneri* kaydı oluşturur (durum: ONAY_BEKLIYOR). Kuyu durumu yalnızca kullanıcı onayıyla değişir (K-05).
- **Ortak zorunlu alanlar** (her veri değiştiren araçta):
  - `olay_tarihi`: raporda geçen operasyon tarihi (rapor tarihinden farklı olabilir).
  - `dayanak_alinti`: değişikliği destekleyen rapor cümlesi/satırı. Dayanaksız öneri reddedilir.
  - `guven`: `yuksek` / `orta` / `dusuk`. Düşükse araç yerine `soru_sor` tercih edilir.
- **Bilinmeyen değer:** Raporda yoksa alan `null` bırakılır ve `bilinmiyor` listesine eklenir. Tipik değerle doldurulmaz.
- **Derinlik:** Rapordaki birimiyle ve birim bilgisiyle verilir (`m` veya `ft`); sistem ikisini de saklar (K-10). Referans noktası (RKB / DF / GL) biliniyorsa belirtilir.
- **Değişiklik yoksa** `degisiklik_yok` çağrılır; zaten uygulanmış olay tekrar önerilmez.

## Veri değiştiren araçlar (öneri üretir)

| Araç | Ne zaman | Ana alanlar (kural tabanı) |
|---|---|---|
| `casing_ekle` | Yeni conductor / yüzey / ara / üretim casing veya liner indi | tür, OD, ID, drift ID, grade, ağırlık (ppf), üst derinlik, pabuç derinliği, bağlantı (opsiyonel), float collar/shoe, liner için hanger ve top packer derinliği. Farklı grade/ağırlık varsa ayrı aralık. |
| `casing_guncelle` | Mevcut casing bilgisi değişti/düzeltildi (yama, kesme vb.) | casing kimliği, değişen alanlar |
| `cimento_isi_kaydet` | Çimentolama, TOC ölçümü veya squeeze | hedef casing, TOC ve kaynağı (CBL/CET, sıcaklık logu, hacim), kademe durumu (yapıldı / yapılamadı / kısmi), DV tool derinliği, sorunlar (kayıp sirkülasyon, yüzeye gelmedi, top job), bağ kalitesi aralıkları, squeeze mi |
| `perforasyon_ekle` | Yeni perforasyon atıldı | üst–alt derinlik, SPF, faz, tabanca tipi, tarih, zon/formasyon |
| `perforasyon_durumu_degistir` | Squeeze ile kapandı / tapa altında kaldı / tekrar açıldı | perforasyon kimliği, yeni durum (açık / squeeze / tapa altında) |
| `tapa_ekle` | CIBP, RBP, çimento tapa, retainer veya sand plug kondu | tür, derinlik (üst/alt), üzerindeki çimento kapağı boyu, tarih. PBTD güncellemesi önerilir. |
| `tapa_kaldir` | RBP çıkarıldı veya tapa delindi | tapa kimliği, tarih |
| `packer_ekle_veya_kaldir` | Packer set edildi / çekildi | tür, derinlik, tarih, işlem (ekle/kaldır) |
| `tamamlama_dizisi_guncelle` | Tubing veya ekipman değişti | tubing OD/ID/grade/ağırlık/derinlik, SSSV, nipple, sliding sleeve, yapay kaldırma (ESP, çubuklu pompa, gas lift mandrel) |
| `balik_ekle_veya_kaldir` | Kuyuda malzeme kaldı / çıkarıldı | tanım, tepe derinliği, uzunluk (biliniyorsa), işlem (ekle/çıkar) |
| `kuyu_tabani_guncelle` | PBTD / TD değişti (kum temizliği, tapa vb.) | yeni derinlik ve neden |
| `formasyon_ekle_veya_guncelle` | Rapor formasyon tepesi/tabanı veriyor | ad, tepe, taban derinliği |
| `workover_notu_ekle` | Geometri değiştirmeyen operasyon (asit, frac) | tür, aralık, ayrıntılar (asit tipi, hacim), tarih |
| `sidetrack_kaydet` | Whipstock/pencere ve yeni dal | whipstock ve pencere derinliği, tarih |

## Veri değiştirmeyen araçlar

| Araç | Amaç |
|---|---|
| `soru_sor` | Emin olunmayan veya belirsiz durumda kullanıcıya soru (ör. iki rapor çelişiyor). |
| `uyari_ver` | Rapor kural tabanıyla veya mevcut durumla çelişiyor; rapor esas alınır, uyarı gösterilir (kurallar-ve-sinirlar §1.3). |
| `degisiklik_yok` | Rapor kuyunun yapısını değiştirmiyor; kısa gerekçe verilir. |

## Aracın dışında kalanlar

- Sketch çizimi araç değildir; kodla JSON'dan çizilir (K-08).
- Serbest SQL, dosya, ağ erişimi yoktur.
- Doğrulama (geometri kontrolleri) araçların dışında, öneri kaydedilirken kodla yapılır (kurallar-ve-sinirlar §3).

## Açık noktalar

- Araç sayısı ve ayrıntı seviyesi: tek `casing_ekle` mi, casing ve liner ayrı mı? Deneme sonrası netleşir.
- Bir raporda birden fazla olay olursa araçların sırası/bağımlılığı (ör. tapa eklenince perforasyon durumu) nasıl ele alınacak?
- Önerilerin kısmi onayı (acik-sorular.md #14) araç çağrılarının bağımsız olmasını gerektirir.
- Gerçek rapor örnekleri gelince alanlar rapora göre düzeltilecek (acik-sorular.md #2).
