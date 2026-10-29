# Kuyu Tasarımı ve Well Sketch Kural Tabanı

Bu dosya, sondaj ve workover raporlarından otomatik well sketch çizecek LLM sisteminin kural tabanıdır.
Kaynak: standart sondaj mühendisliği pratiği (API/IADC gelenekleri, NORSOK D-010 tarzı terk kuralları) ve kullanıcı düzeltmeleri.
Rakamlar **tipik değerlerdir**; her zaman rapordaki değer esastır.

---

## 1. Kuyunun yaşam döngüsü (olay sırası)

- Sondaj → (log/test) → tamamlama → üretim veya terk → workover'lar → nihai terk (P&A).
- Her rapor bir **olaydır** ve kuyunun mevcut durumunu günceller.
- Sketch, olayların tarih sırasıyla uygulanmasının sonucudur.

## 2. Casing hiyerarşisi (dıştan içe, sığdan derine)

| Sıra | Boru | Görev |
|---|---|---|
| 1 | Conductor (çakma/kılavuz boru) | İlk, en büyük çaplı, en sığ boru; gevşek yüzey formasyonunu tutar. |
| 2 | Yüzey (surface) casing | Tatlı su akiferlerini korur; BOP ve kuyu başı bunun üzerine oturur. |
| 3 | Ara (intermediate) casing | Problemli zonları (kayıp, aşırı basınç, tuz, şişen şeyl) izole eder. Sıfır, bir veya birden fazla olabilir. |
| 4 | Üretim (production) casing | Rezervuarın üstüne veya içinden geçer; tamamlama bunun içinde yapılır. |
| 5 | Liner | Yüzeye kadar çıkmayan, önceki casing'in içine asılan boru (sondaj veya üretim liner'ı). Sonradan tie-back ile yüzeye bağlanabilir. |

## 3. Geometri kuralları (sketch doğrulaması için kritik)

- Her casing bir öncekinin içinden geçer: `OD(n) < drift ID(n-1)`.
- Her bölümün kuyu çapı, o bölüme inen casing'in OD'sinden büyüktür (tipik 1–4 inç boşluk).
- Sonraki bölümün matkabı önceki casing'in drift ID'sinden geçmelidir.
- Pabuç (shoe) derinlikleri içe doğru artar: conductor < yüzey < ara < üretim.
- Yüzey, ara ve üretim casing'leri kuyu başından (0) başlar; liner'lar başlamaz.
- Liner tepesi önceki casing'in içindedir; üst üste binme (overlap) tipik 50–150 m (150–500 ft).
- **Liner 6" veya 7" olarak açık kuyuya indirilir** (7" liner tipik olarak 8½" kuyuya).

Tipik çap eşleşmeleri:

| Kuyu çapı | Casing OD | Tipik kullanım |
|---|---|---|
| 36" | 30" | Conductor |
| 26" | 20" | Yüzey |
| 17½" | 13⅜" | Yüzey veya ara |
| 12¼" | 9⅝" | Ara veya üretim |
| 8½" | 7" | Üretim veya liner |
| açık kuyu | 6" | Liner |

Karada sık görülen sığ dizilim: 17½/13⅜ → 12¼/9⅝ → 8½/7.

## 4. Casing veri alanları (zorunlu)

Her casing ve liner için aşağıdakiler **elzemdir**:

- **OD** (inç)
- **ID** (inç) ve drift ID
- **API grade** (J-55, K-55, N-80, L-80, C-95, P-110 vb.)
- **Ağırlık** (ppf / #)
- Üst ve alt (pabuç) derinliği

Ek kurallar:

- Bir dizide farklı grade veya ağırlık kullanıldıysa her biri **ayrı derinlik aralığı** olarak kaydedilir.
- Bağlantı tipi (BTC, LTC, STC, premium) opsiyonel alan olarak tutulur.
- Float collar ve float shoe derinlikleri kaydedilir; liner için hanger ve liner top packer derinliği de tutulur.

## 5. Set derinliği mantığı

- Conductor: genelde 20–100 m.
- Yüzey casing: tatlı su akiferlerinin altına ve sağlam formasyona; mevzuatla zorunlu.
- Ara casing: gözenek basıncı ile çatlatma basıncı arasındaki pencere daraldığında set edilir.
- Casing pabucu tercihen sağlam, geçirimsiz bir formasyona (şeyl) oturtulur.
- Üretim casing'i rezervuarın tabanının altına (rathole/cep bırakarak) veya rezervuar tepesine (açık kuyu tamamlama) set edilir.

## 6. Çimento kuralları

Çimentolama kuralları değişkendir; aşağıdakiler **tipik değerdir, rapor esastır**.

Tipik değerler:

- Conductor ve yüzey casing'i genelde yüzeye kadar çimentolanır.
- Ara casing'te çimento tepesi (TOC) tipik olarak önceki pabucun 100–300 m üstündedir.
- Üretim casing'inde TOC en üst rezervuarın/perforasyonun en az 150–300 m üstündedir.
- Liner genelde tüm boyunca, liner tepesine kadar çimentolanır.
- Float collar pabucun 1–3 boru (~10–40 m) üstündedir; aradaki "shoe track" çimentoyla doludur.
- Sketch'te annulus çimentosu TOC ile pabuç arasında gösterilir. TOC bilinmiyorsa tahmin edilmez, "bilinmiyor" olarak işaretlenir.

Sketch, çimentolama sırasında yaşanan **sorunları da göstermelidir**:

- **Kademeli çimentolama:** DV tool (stage collar) derinliği ve her kademenin durumu (yapıldı / yapılamadı / kısmi).
- DV açılmadı, DV açıldı ama kapanmadı, 2. kademe yapılmadı gibi olaylar.
- Kayıp sirkülasyon, çimento yüzeye gelmedi, top job yapıldı.
- Ölçülen TOC ve kaynağı (CBL/CET, sıcaklık logu, hacim hesabı).
- Çimento bağ kalitesi (iyi / zayıf / bağ yok aralıkları).
- Sonradan yapılan remedial squeeze işleri.

## 7. Tamamlama

- Açık kuyu (open hole), casing'li-perforeli (cased hole) veya liner'lı tamamlama.
- Tubing her zaman üretim casing'inin/liner'ının içindedir; OD, ID, grade ve ağırlığı tutulur.
- Packer tipik olarak en üst perforasyonun 10–30 m üstüne set edilir.
- Ekipmanlar: kuyu başı ve X-mas tree, SSSV, nipple'lar, sliding sleeve, gravel pack/elek.
- Yapay kaldırma: ESP, çubuklu pompa (rod pump), gas lift mandrelleri.

## 8. Perforasyon

- Sadece casing/liner'ın çimentolu bölümünde yapılır.
- Kaydedilecekler: üst–alt derinlik, atış yoğunluğu (SPF), faz açısı, tabanca tipi, tarih, zon/formasyon adı.
- Durum: **açık**, **squeeze ile kapatılmış** veya **tapa altında kalmış**.

## 9. Tapalar ve izolasyon

- Türler: köprü tapa (CIBP / RBP), çimento tapa, çimento tutucu (retainer), sand plug.
- Tapanın altındaki perforasyonlar izole kabul edilir.
- CIBP üzerine tipik 5–15 m çimento kapağı konur.
- Her tapa PBTD'yi (plugged back total depth) günceller.
- Geri alınabilir tapa (RBP) sonradan çıkarılabilir; sketch'ten de kaldırılır.

## 10. Workover operasyonları ve sketch'e etkisi

| Operasyon | Sketch'e etkisi |
|---|---|
| Asitleme | Geometri değişmez; aralığa not düşülür (asit tipi, hacim, tarih). |
| Fracturing | Geometri değişmez; aralığa not düşülür. |
| Squeeze çimento | İlgili perforasyon "kapalı" olur. |
| Yeniden perforasyon | Yeni perforasyon aralığı eklenir. |
| Tubing / pompa değişimi | Tamamlama dizisi güncellenir. |
| Casing yaması (patch) | Belirli derinliğe işaretlenir. |
| Kum temizliği | Kuyu tabanı / PBTD güncellenir. |
| Balık (fishing) | Kuyu içindeki balık ve tepe derinliği gösterilir; çıkarılırsa kaldırılır. |
| Rekompletasyon | Alt zon kapatılır, üst zon açılır. |
| Sidetrack | Whipstock ve pencere derinliğinden yeni kuyu dalı açılır. |

## 11. Terk (P&A)

- Rezervuar üstüne, casing pabuçlarına, liner tepelerine ve yüzeye çimento tapalar konur.
- Tipik tapa boyu en az 30–50 m (100 ft).
- Casing yüzeyin birkaç metre altından kesilir.

## 12. Derinlik ve birim kuralları

- Derinlikler hem **metre** hem **ft** olarak tutulur.
- Arayüzde bir **combobox** ile kullanıcı m / ft arasında geçiş yapar (1 ft = 0,3048 m).
- Çaplar inç, ağırlık ppf olarak kalır.
- MD ile TVD ayrı tutulur; sketch MD ile çizilir.
- Referans noktası (RKB / DF / GL) ve yüksekliği her kuyuda kaydedilir.

## 13. LLM ve sketch için doğrulama kuralları

- Raporda olmayan değer uydurulmaz, "bilinmiyor" olarak işaretlenir.
- Her yeni olay bu dosyadaki geometri kurallarına göre kontrol edilir; çelişki varsa kullanıcıya sorulur.
- Kuyu durumu yapılandırılmış veri (JSON) olarak tutulur ve sketch bu veriden çizilir; LLM doğrudan çizim yapmaz.
- Her değişiklik kaynak rapora ve tarihe bağlanır, böylece kuyunun herhangi bir tarihteki görünümü yeniden üretilebilir.
