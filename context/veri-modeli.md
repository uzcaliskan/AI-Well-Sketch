# Kavramsal Veri Modeli (TASLAK)

> Tablo/sütun şeması değil, kavramsal modeldir. Kullanıcı onaylamadı; alanlar gerçek rapor örnekleri ve şirket verisi görülünce değişebilir.
> Dayanaklar: [kararlar.md](kararlar.md) K-05, K-08, K-09, K-10, K-11 · [kurallar-ve-sinirlar.md](kurallar-ve-sinirlar.md) §1, §4 ·
> [kuyu-tasarim-kurallari.md](kuyu-tasarim-kurallari.md) · araçlar: [llm-araclari.md](llm-araclari.md).

## Temel fikir

Kuyunun durumu **olayların tarih sırasıyla uygulanmasının sonucudur** (K-09). Kaynak doğruluk **olay geçmişidir**; kuyu durumu (JSON) bundan türetilir ve yeniden üretilebilir.

```
Rapor ──► (Claude) ──► Öneri ──onay──► Olay ──► Kuyu durumu (JSON) ──► Sketch
                         │ red/düzelt                   ▲
                         ▼                              │ herhangi bir tarihe kadar uygula
                       kayıt kalır                  geçmiş görünüm
```

## Varlıklar

### Kuyu
| Alan | Not |
|---|---|
| id (sabit iç kimlik) | Ad değişse de kuyu aynı kalır. |
| kuyu adı | **Benzersiz, güncellenebilir** (K-13), örn. `Arılı-1` → `Arılı-1/S`. Eski adlar **saklanır** (ad geçmişi: ad, geçerlilik tarihleri). |
| referans noktası tipi ve yüksekliği | RKB / DF / GL, **zorunlu** (kurallar §4). |
| birim tercihi | Arayüz m/ft; veri her zaman ikisini de tutar. |
| oluşturulma zamanı | |

### Rapor
| Alan | Not |
|---|---|
| kuyu, rapor tarihi | |
| ham dosya (PDF/HTML) | Olduğu gibi saklanır; yeniden işleme kaynağı. |
| çıkarılmış metin | PDF türü (metin/taranmış) açık soru. |
| işlenme durumu | örn. YUKLENDI → METIN_HAZIR → LLM_ISLENIYOR → ONAY_BEKLIYOR → TAMAMLANDI / HATA (taslak). |
| yükleyen, yüklenme zamanı | |
| (sonra) şirket rapor kimliği, kaynak adres | Aşama 4; şimdi yok. |

### Öneri
LLM'in bir araç çağrısının kaydı (K-05). Uygulanana kadar kuyu durumunu **değiştirmez**.
| Alan | Not |
|---|---|
| rapor, kuyu | Hangi rapordan geldiği. |
| araç adı, araç parametreleri (JSON) | llm-araclari.md ile birebir. |
| olay tarihi, dayanak alıntısı, güven | Ortak zorunlu alanlar. |
| doğrulama uyarıları | Geometri kontrolleri; engellemez (kurallar §3). |
| durum | ONAY_BEKLIYOR / ONAYLANDI / REDDEDILDI / DUZELTILDI. |
| karar veren, karar zamanı, düzeltilmiş parametreler | İzlenebilirlik (kurallar §1.5). |
| üretilen olay | Onaylanınca oluşan Olay'a bağ. |

### Olay (değiştirilmez)
Onaylanan değişiklik. **Silinmez veya güncellenmez**; düzeltme yeni olay olarak eklenir (kurallar §1.5).
| Alan | Not |
|---|---|
| kuyu, olay tipi | casing eklendi, tapa kondu, perforasyon kapandı… |
| olay tarihi | Operasyonun tarihi; sıralama bununla yapılır. |
| veri (JSON) | Olayın içeriği. |
| kaynak rapor, öneri | Her değişiklik rapora ve tarihe bağlı (K-09). |
| öneren (LLM/kullanıcı), onaylayan, onay zamanı | |
| düzeltiyor mu | Önceki bir olayı düzelten olay ise o olaya bağ. |

### Kuyu durumu (türetilmiş)
Olayların uygulanmasıyla oluşan JSON (K-08). İki kullanım: güncel görünüm ve **herhangi bir tarihteki görünüm** (kurallar §1.6).
- Başlangıçta: ihtiyaç olunca olaylardan hesaplanır.
- Güncel durum önbelleğe alınabilir; ancak geçmiş bir olay değişirse durum **en baştan** yeniden hesaplanır (K-15), ara snapshot kullanılmaz.

Taslak JSON bölümleri (kural tabanından): `referans`, `formasyonlar`, `casingler` (liner dahil), `cimento_isleri`, `perforasyonlar`, `tapalar`, `packerlar`, `tamamlama_dizisi`, `baliklar`, `kuyu_tabani` (TD/PBTD), `workover_notlari`, `sidetrack`.
Her derinlik: `{m, ft}`; bilinmeyen alan `null` + `bilinmiyor` işareti (K-11). MD ve TVD ayrı (K-10).

### Fotoğraf
| Alan | Not |
|---|---|
| kuyu, dosya | Saklama yeri açık (kararlar B-03). |
| çekim/yükleme tarihi | Farklı tarihler (K-06). |
| yükleyen | |
| not/derinlik/etiket | Gerekip gerekmediği açık soru (#19). |

### Kullanıcı
Başlangıçta basit (tek veya birkaç kullanıcı). Rol ayrımı, SSO/LDAP açık (B-06). Öneri kararı ve yüklemeler kullanıcıya bağlanır.

### (Sonra, Aşama 4) İzleyici imleci
Şirket DB'sinde en son işlenen nokta (sirket-db-izleme-pseudo.md). Başlangıçta yok.

## İlişkiler

```
Kuyu 1─* Rapor 1─* Öneri 0..1─1 Olay *─1 Kuyu
Kuyu 1─* Fotoğraf
Kullanıcı 1─* (Rapor yükler, Öneri karar verir, Fotoğraf yükler)
```

## Kurallar ve sınırlar

- Öneri onaylanmadan Olay oluşmaz; Olay olmadan kuyu durumu değişmez.
- Olay ve karar kayıtları silinmez.
- Kuyu içinde olaylar `olay tarihi` sırasıyla uygulanır. Geriye dönük tarihli olay veya rapor revizyonu gelirse durum, baştan (ilk olaydan itibaren) yeniden hesaplanır (K-15).
- Rapordaki kuyu adı hiçbir güncel veya eski adla eşleşmezse uyarı verilir; yeni kuyu otomatik açılmaz (K-13).
- Onay beklerken aynı kuyuya yeni rapor beklenmez (K-14); bunun için ayrı kuyruk mantığı yok.
- Kuyu listeleri sayfalı, sorgular `kuyu` ve `olay tarihi` üzerinden indeksli olmalı (uzun vadeli ölçek).

## Açık noktalar

- Revizyon: düzeltilmiş raporun yeni önerileri onaya mı düşer (K-15 varsayımı), eski olaylar nasıl düzeltilir?
- Kısmi onay (#14) için öneriler arası bağımlılık gerekir mi?
- Başlangıç durumu (K-16): eski kuyularda olay geçmişi eski kayıtlardan kurulur, yeni kuyular boş başlar.
  Eski kuyu içe aktarma ertelendi. Yapıldığında: kayıtlar veritabanından gelir, tüm süreç bitince kuyu başına tek toplu onay sorulur,
  hangi LLM'in kullanılacağı açık (#7). İçe aktarılan olayların kaynağı "geçmiş kayıt" olarak işaretlenmelidir.
