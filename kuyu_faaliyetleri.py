from playwright.sync_api import sync_playwright
import json
import time
import re
import sys

def turkce_temizle(metin):
    """Türkçe karakterleri temizle ve büyük harfe çevir"""
    metin = metin.upper()
    # Türkçe karakterleri İngilizce eşdeğerlerine çevir
    esleme = {
        'İ': 'I', 'ı': 'I',
        'Ğ': 'G', 'ğ': 'G',
        'Ü': 'U', 'ü': 'U',
        'Ş': 'S', 'ş': 'S',
        'Ö': 'O', 'ö': 'O',
        'Ç': 'C', 'ç': 'C'
    }
    for tr, en in esleme.items():
        metin = metin.replace(tr, en)
    return metin

def kuyu_faaliyetlerini_getir(kuyu_adi):
    """Kuyu adı verildiğinde tüm faaliyetleri JSON olarak döndür"""

    # Kuyu adını temizle
    kuyu_adi_temiz = turkce_temizle(kuyu_adi.strip())

    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=False)
        page = browser.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})

        # Giriş
        print(f"1. Giriş yapılıyor...")
        page.goto("https://operasyon.tpao.gov.tr/")
        page.wait_for_load_state("networkidle")
        page.get_by_placeholder("Kullanıcı Adı").fill(config["username"])
        page.get_by_placeholder("Şifre").fill(config["password"])
        page.locator("button").first.click()
        page.wait_for_timeout(8000)

        # Raporlar sayfasına git
        print("2. Raporlar > Sondaj Raporları > Günlük Faaliyet Raporları...")
        page.get_by_text("Raporlar").first.click()
        page.wait_for_timeout(1000)
        page.get_by_text("Sondaj Raporları").first.click()
        page.wait_for_timeout(1000)
        page.get_by_text("Günlük Faaliyet Raporları").first.click()
        page.wait_for_timeout(8000)

        # Kuyu seç
        print(f"3. {kuyu_adi_temiz} kuyusu seçiliyor...")
        page.get_by_text("Wellbore Seçiniz").first.click()
        page.wait_for_timeout(2000)
        page.keyboard.type(kuyu_adi_temiz)
        page.wait_for_timeout(2000)
        page.get_by_text(kuyu_adi_temiz, exact=False).first.click()
        page.wait_for_timeout(5000)

        print(f"4. {kuyu_adi_temiz} kuyusu sayfasına bağlanıldı!")

        # Rapor tablosunu bekle
        print("5. Raporlar yükleniyor...")
        page.wait_for_timeout(3000)

        # Tüm raporları al
        print("6. Tüm raporlar işleniyor...")
        rows = page.locator("tbody tr").all()
        print(f"  Toplam rapor sayısı: {len(rows)}")

        saat_pattern = re.compile(r'^\d{2}:\d{2}$')
        tum_raporlar = {}
        tum_faaliyetler_metni = []

        # Her raporu işle (TÜM RAPORLAR)
        for row_idx in range(len(rows)):
            row = rows[row_idx]
            cells = row.locator("td").all()

            if len(cells) < 2:
                continue

            rapor_no = cells[0].inner_text().strip()
            tarih = cells[1].inner_text().strip()

            print(f"\n  Rapor {rapor_no} ({tarih}) işleniyor...")

            # Raporu yeni sekmede aç
            with page.expect_popup() as popup_info:
                cells[0].click()

            popup = popup_info.value
            popup.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(3000)

            # Tablo satırlarını al
            table_rows = popup.locator("table tr").all()

            # Saat bazlı faaliyetleri çıkar
            rapor_faaliyetler = []
            sn_modu = False

            for i, tr in enumerate(table_rows[1:], 1):
                try:
                    tds = tr.locator("td").all()
                    if len(tds) >= 5:
                        baslama = tds[0].inner_text().strip()
                        bitis = tds[1].inner_text().strip()
                        faaliyet = tds[4].inner_text().strip()

                        # SN bölümünü atla
                        if baslama == "SN":
                            sn_modu = True
                            continue
                        if sn_modu and len(tds) >= 2:
                            ilk = tds[0].inner_text().strip()
                            if ilk.isdigit():
                                continue
                            sn_modu = False

                        # Sadece saat bazlı faaliyetleri al
                        if saat_pattern.match(baslama) and saat_pattern.match(bitis):
                            # 00:00-08:00 faaliyetlerini atla (son rapor hariç)
                            if baslama == "00:00" and bitis == "08:00" and row_idx > 0:
                                continue
                            rapor_faaliyetler.append(faaliyet)
                            tum_faaliyetler_metni.append(f"[{rapor_no} - {tarih}] {faaliyet}")
                except Exception as e:
                    print(f"    Satır {i} hatası: {e}")

            # Raporu JSON'a ekle
            tum_raporlar[tarih] = {
                "rapor_no": rapor_no,
                "tarih": tarih,
                "toplam_faaliyet": len(rapor_faaliyetler),
                "faaliyetler": rapor_faaliyetler,
                "faaliyet_metni_birlesik": " | ".join(rapor_faaliyetler)
            }

            print(f"    {len(rapor_faaliyetler)} faaliyet bulundu")

            # Popup'ı kapat ve ana sayfaya dön
            popup.close()
            page.wait_for_timeout(1000)

        # Ana JSON
        sonuc = {
            "kuyu_adi": kuyu_adi_temiz,
            "toplam_rapor": len(tum_raporlar),
            "raporlar": tum_raporlar,
            "tum_faaliyetler_metni": "\n".join(tum_faaliyetler_metni)
        }

        # Dosya adını kuyu adına göre oluştur
        dosya_adi = f"{kuyu_adi_temiz.lower()}_faaliyetler.json"
        with open(dosya_adi, "w", encoding="utf-8") as f:
            json.dump(sonuc, f, ensure_ascii=False, indent=2)

        print(f"\n7. JSON kaydedildi: {dosya_adi}")
        print(f"   Toplam rapor: {len(tum_raporlar)}")
        print(f"   Toplam faaliyet: {len(tum_faaliyetler_metni)}")

        # Screenshot
        ekran_gorseli = f"{kuyu_adi_temiz.lower()}_raporlar.png"
        page.screenshot(path=ekran_gorseli)
        print(f"8. Screenshot: {ekran_gorseli}")

        print("\nİşlem tamamlandı!")
        time.sleep(3)
        browser.close()

        return dosya_adi

if __name__ == "__main__":
    if len(sys.argv) > 1:
        kuyu_adi = sys.argv[1]
    else:
        kuyu_adi = input("Kuyu adı girin: ")

    kuyu_faaliyetlerini_getir(kuyu_adi)
