"""Kuyu durumu (JSON) -> SVG sketch. LLM çizim yapmaz; çizim yalnızca bu koddadır (K-08)."""
from html import escape

from apps.wells.state import FT, metre

GENISLIK, YUKSEKLIK = 900, 720
ÜST, ALT = 40, 40
EKSEN_X = 60
MERKEZ_X = 520
FORMASYON_X, FORMASYON_GEN = 90, 230

RENKLER = {"acik": "#c0392b", "squeeze": "#7f8c8d", "tapa_altinda": "#e67e22"}
FORMASYON_RENKLERI = ["#f4ecd8", "#e8dcc0"]


def _tum_derinlikler(durum):
    degerler = []

    def dolas(obj):
        if isinstance(obj, dict):
            if set(obj) >= {"m", "ft"}:
                degerler.append(obj["m"])
            else:
                for v in obj.values():
                    dolas(v)
        elif isinstance(obj, list):
            for v in obj:
                dolas(v)

    dolas(durum)
    return [d for d in degerler if d is not None]


def _adim(maks_m, birim):
    maks = maks_m / FT if birim == "ft" else maks_m
    for adim in (10, 20, 50, 100, 200, 500, 1000, 2000, 5000):
        if maks / adim <= 12:
            return adim
    return 5000


def _cap_px(od):
    return 10 + float(od) * 5 if isinstance(od, (int, float)) else 30


def render_svg(durum, birim="m"):
    derinlikler = _tum_derinlikler(durum)
    maks_m = max(derinlikler) * 1.05 if derinlikler else 1000.0
    h = YUKSEKLIK - ÜST - ALT

    def y(m):
        return ÜST + (m / maks_m) * h

    def etiket_derinlik(d):
        m = metre(d)
        if m is None:
            return "?"
        return f"{m / FT:,.0f} ft" if birim == "ft" else f"{m:,.0f} m"

    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {GENISLIK} {YUKSEKLIK}" '
        f'class="sketch" role="img" aria-label="Kuyu şeması">',
        '<defs><pattern id="cimento" width="6" height="6" patternUnits="userSpaceOnUse">'
        '<path d="M0,6 L6,0" stroke="#7f8c8d" stroke-width="1"/></pattern></defs>',
    ]

    # Derinlik ekseni
    adim = _adim(maks_m, birim)
    deger = 0
    while True:
        m = deger * FT if birim == "ft" else deger
        if m > maks_m:
            break
        p.append(f'<line x1="{EKSEN_X}" x2="{EKSEN_X + 6}" y1="{y(m):.1f}" y2="{y(m):.1f}" stroke="#555"/>')
        p.append(f'<text x="{EKSEN_X - 4}" y="{y(m) + 4:.1f}" text-anchor="end" font-size="11">{deger:,}</text>')
        deger += adim
    p.append(f'<line x1="{EKSEN_X + 6}" x2="{EKSEN_X + 6}" y1="{ÜST}" y2="{ÜST + h}" stroke="#555"/>')
    p.append(f'<text x="{EKSEN_X}" y="{ÜST - 14}" font-size="11" text-anchor="middle">MD ({birim})</text>')

    # Formasyonlar
    for i, f in enumerate(durum["formasyonlar"]):
        tepe, taban = metre(f.get("tepe_derinlik")), metre(f.get("taban_derinlik"))
        if tepe is None:
            continue
        if taban is None:
            sonraki = [metre(g.get("tepe_derinlik")) for g in durum["formasyonlar"]]
            sonraki = sorted(s for s in sonraki if s is not None and s > tepe)
            taban = sonraki[0] if sonraki else maks_m
        renk = FORMASYON_RENKLERI[i % 2]
        p.append(
            f'<rect x="{FORMASYON_X}" y="{y(tepe):.1f}" width="{FORMASYON_GEN}" '
            f'height="{max(y(taban) - y(tepe), 2):.1f}" fill="{renk}" stroke="#bbb"/>'
        )
        p.append(
            f'<text x="{FORMASYON_X + 6}" y="{y(tepe) + 14:.1f}" font-size="11">'
            f"{escape(str(f.get('ad', '?')))} ({etiket_derinlik(f.get('tepe_derinlik'))})</text>"
        )

    # Casingler: dıştan içe (OD büyükten küçüğe)
    casingler = sorted(durum["casingler"], key=lambda c: -(c.get("od_inc") or 0))
    en_ic_yari = 20
    for c in casingler:
        pabuc = metre(c.get("pabuc_derinlik"))
        if pabuc is None:
            continue
        ust = metre(c.get("ust_derinlik"))
        if ust is None:
            ust = 0 if c.get("tur") != "liner" else pabuc
        yari = _cap_px(c.get("od_inc")) / 2
        en_ic_yari = min(en_ic_yari, yari) if en_ic_yari != 20 else yari
        sol, sag = MERKEZ_X - yari, MERKEZ_X + yari
        p.append(f'<line x1="{sol}" x2="{sol}" y1="{y(ust):.1f}" y2="{y(pabuc):.1f}" stroke="#222" stroke-width="2"/>')
        p.append(f'<line x1="{sag}" x2="{sag}" y1="{y(ust):.1f}" y2="{y(pabuc):.1f}" stroke="#222" stroke-width="2"/>')
        p.append(f'<polygon points="{sol},{y(pabuc):.1f} {sol - 7},{y(pabuc):.1f} {sol},{y(pabuc) - 7:.1f}" fill="#222"/>')
        p.append(f'<polygon points="{sag},{y(pabuc):.1f} {sag + 7},{y(pabuc):.1f} {sag},{y(pabuc) - 7:.1f}" fill="#222"/>')
        od = c.get("od_inc")
        p.append(
            f'<text x="{sag + 12}" y="{y(pabuc) - 2:.1f}" font-size="11">'
            f"{escape(str(c.get('tur', '')))} {escape(str(od)) if od else '?'}\" "
            f"@ {etiket_derinlik(c.get('pabuc_derinlik'))}</text>"
        )

    # Çimento (annulus, TOC -> pabuç)
    for cim in durum["cimento_isleri"]:
        toc = metre(cim.get("toc_derinlik"))
        hedef = next((c for c in durum["casingler"] if c.get("id") == cim.get("hedef_casing_id")), None)
        if toc is None or hedef is None or metre(hedef.get("pabuc_derinlik")) is None:
            continue
        yari = _cap_px(hedef.get("od_inc")) / 2
        pabuc = metre(hedef["pabuc_derinlik"])
        for x in (MERKEZ_X - yari - 8, MERKEZ_X + yari):
            p.append(
                f'<rect x="{x}" y="{y(toc):.1f}" width="8" height="{max(y(pabuc) - y(toc), 1):.1f}" '
                f'fill="url(#cimento)" stroke="#7f8c8d"/>'
            )

    # Tapalar
    ust_tapalar = []
    for t in durum["tapalar"]:
        ust, alt = metre(t.get("ust_derinlik")), metre(t.get("alt_derinlik"))
        if ust is None:
            continue
        ust_tapalar.append(ust)
        alt = alt if alt is not None else ust
        p.append(
            f'<rect x="{MERKEZ_X - en_ic_yari}" y="{y(ust):.1f}" width="{2 * en_ic_yari}" '
            f'height="{max(y(alt) - y(ust), 4):.1f}" fill="#34495e"/>'
        )
        p.append(
            f'<text x="{MERKEZ_X + en_ic_yari + 14}" y="{y(ust) + 10:.1f}" font-size="11">'
            f"{escape(str(t.get('tur', 'tapa')))} {etiket_derinlik(t.get('ust_derinlik'))}</text>"
        )

    # Perforasyonlar (tapa altında kalan açık perforasyon izole sayılır, kural tabanı §9)
    for pf in durum["perforasyonlar"]:
        ust, alt = metre(pf.get("ust_derinlik")), metre(pf.get("alt_derinlik"))
        if ust is None:
            continue
        alt = alt if alt is not None else ust
        durum_adi = pf.get("durum") or "acik"
        if durum_adi == "acik" and any(u <= alt for u in ust_tapalar):
            durum_adi = "tapa_altinda"
        renk = RENKLER.get(durum_adi, RENKLER["acik"])
        p.append(
            f'<rect x="{MERKEZ_X - en_ic_yari - 14}" y="{y(ust):.1f}" width="{2 * en_ic_yari + 28}" '
            f'height="{max(y(alt) - y(ust), 3):.1f}" fill="{renk}" fill-opacity="0.35" '
            f'stroke="{renk}" stroke-dasharray="3 2"/>'
        )

    # Tamamlama dizisi (tubing)
    tubing_ayak = metre(durum["tamamlama_dizisi"].get("tubing_ayak_derinlik"))
    if tubing_ayak is not None:
        yari = _cap_px(durum["tamamlama_dizisi"].get("tubing_od_inc")) / 2
        for x in (MERKEZ_X - yari, MERKEZ_X + yari):
            p.append(f'<line x1="{x}" x2="{x}" y1="{y(0)}" y2="{y(tubing_ayak):.1f}" stroke="#2980b9" stroke-width="2"/>')

    # Packerlar
    for pk in durum["packerlar"]:
        d = metre(pk.get("derinlik"))
        if d is None:
            continue
        p.append(
            f'<rect x="{MERKEZ_X - en_ic_yari - 4}" y="{y(d) - 4:.1f}" width="{2 * en_ic_yari + 8}" '
            f'height="8" fill="#2980b9"/>'
        )
        p.append(
            f'<text x="{MERKEZ_X - en_ic_yari - 10}" y="{y(d) + 4:.1f}" font-size="11" text-anchor="end">'
            f"packer {escape(str(pk.get('tur', '')))} {etiket_derinlik(pk.get('derinlik'))}</text>"
        )

    # Kuyuda kalan malzeme (balık)
    for b in durum["baliklar"]:
        tepe = metre(b.get("tepe_derinlik"))
        if tepe is None:
            continue
        uzunluk = b.get("uzunluk")
        alt = tepe + (uzunluk if isinstance(uzunluk, (int, float)) else 3)
        p.append(f'<rect x="{MERKEZ_X - 8}" y="{y(tepe):.1f}" width="16" height="{max(y(alt) - y(tepe), 5):.1f}" fill="#8e44ad"/>')
        p.append(
            f'<text x="{MERKEZ_X + 14}" y="{y(tepe) + 4:.1f}" font-size="11" fill="#8e44ad">'
            f"balık: {escape(str(b.get('tanim', '?')))} {etiket_derinlik(b.get('tepe_derinlik'))}</text>"
        )

    # TD / PBTD
    for ad, anahtar in (("TD", "td"), ("PBTD", "pbtd")):
        d = metre(durum["kuyu_tabani"].get(anahtar))
        if d is None:
            continue
        p.append(f'<line x1="{EKSEN_X + 6}" x2="{GENISLIK - 20}" y1="{y(d):.1f}" y2="{y(d):.1f}" stroke="#16a085" stroke-dasharray="6 3"/>')
        p.append(
            f'<text x="{GENISLIK - 24}" y="{y(d) - 3:.1f}" font-size="11" text-anchor="end" fill="#16a085">'
            f"{ad} {etiket_derinlik(durum['kuyu_tabani'][anahtar])}</text>"
        )

    if not derinlikler:
        p.append(
            f'<text x="{GENISLIK / 2}" y="{YUKSEKLIK / 2}" text-anchor="middle" font-size="14" fill="#888">'
            "Henüz onaylanmış veri yok (boş sketch)</text>"
        )
    p.append("</svg>")
    return "".join(p)
