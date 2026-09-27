"""Libreria di arredi in pianta, stessa scala del template della pianta.

Scala: 80 px = 1 m (SVG), come pianta_abitazione_template.svg.
       PNG esportati a 3x -> 240 px = 1 m, come pianta_abitazione_template.png.

Convenzione: nella rotazione r0 il lato di utilizzo (dove ci si siede,
si aprono ante/cassetti, si entra nel letto) e' in BASSO; lo schienale
o il lato da addossare al muro e' in ALTO.
Ogni pezzo e' esportato in 4 rotazioni (r0, r90, r180, r270) perche'
Milanote non permette di ruotare le immagini.
"""
import os
import cairosvg

ROT = 0              # rotazione corrente (usata da T)
PX_CM = 0.8          # px per cm (80 px/m)
PNG_SCALE = 3        # 240 px/m
ST = "#5a5a5a"       # tratto
SW = 1.6             # spessore tratto (cm)

COL = {
    "soggiorno": "#f5ecdc",
    "camera": "#eee8f7",
    "cucina": "#e6f2e6",
    "bagno": "#e3eff9",
    "ingresso": "#f2eee5",
    "complementi": "#eef3ea",
}


# ------------------------------------------------------------------ primitive (cm)
def R(x, y, w, h, fill="#fff", rx=2, sw=SW, dash=None, stroke=ST):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"{d}/>')


def L(x1, y1, x2, y2, sw=SW * 0.6, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{ST}" stroke-width="{sw}"{d}/>'


def C(cx, cy, r, fill="#fff", sw=SW):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{ST}" stroke-width="{sw}"/>'


def E(cx, cy, rx, ry, fill="#fff", sw=SW):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{ST}" stroke-width="{sw}"/>'


def T(x, y, s, fs=11, bold=False):
    b = ' font-weight="700"' if bold else ""
    # in r180 il testo viene ribaltato sul posto per restare leggibile
    flip = f' transform="rotate(180 {x} {y})"' if ROT == 180 else ""
    base = f'<text x="{x}" y="{y}" font-size="{fs}" text-anchor="middle" dominant-baseline="middle"{b}{flip}'
    # alone bianco separato (cairosvg non supporta paint-order)
    return (base + f' fill="#fff" stroke="#fff" stroke-width="3" stroke-linejoin="round">{s}</text>'
            + base + f' fill="#333">{s}</text>')


def etichetta(w, d, nome, cy=None):
    """Nome + misure al centro, solo se entrano nel pezzo."""
    fs = 11
    dims = f"{w}×{d}"
    need_w = max(len(nome), len(dims)) * fs * 0.56 + 6
    if w < need_w or d < 2.6 * fs:
        if w >= len(dims) * fs * 0.56 + 4 and d >= 1.4 * fs:
            return T(w / 2, cy or d / 2, dims, fs)
        return ""
    cy = cy or d / 2
    k = -1 if ROT == 180 else 1   # in r180 le righe si invertono: le rimetto in ordine
    return T(w / 2, cy - k * fs * 0.6, nome, fs, True) + T(w / 2, cy + k * fs * 0.65, dims, fs)


def K():
    return -1 if ROT == 180 else 1


# ------------------------------------------------------------------ disegni
def box(w, d, fill, nome):
    return R(0, 0, w, d, fill) + etichetta(w, d, nome)


def divano(w, d, fill, nome, posti):
    s = R(0, 0, w, d, fill)
    s += R(0, 0, w, 22, "#e6d8bf")                 # schienale (in alto)
    s += R(0, 0, 20, d, "#e6d8bf") + R(w - 20, 0, 20, d, "#e6d8bf")  # braccioli
    seat = (w - 40) / posti
    for i in range(1, posti):
        s += L(20 + i * seat, 22, 20 + i * seat, d - 4)
    return s + etichetta(w, d, nome, cy=(22 + d) / 2)


def divano_angolare(w, d, fill, nome):
    pen = 90   # profondità seduta
    chaise = 90
    s = (f'<path d="M 0 0 H {w} V {d} H {w-chaise} V {pen} H 0 Z" fill="{fill}" '
         f'stroke="{ST}" stroke-width="{SW}" stroke-linejoin="round"/>')
    s += R(0, 0, w, 22, "#e6d8bf") + R(w - 20, 0, 20, d, "#e6d8bf") + R(0, 0, 20, pen, "#e6d8bf")
    s += L(w - chaise, pen, w - 20, pen, dash="5 4")
    s += L((w - chaise) / 2 + 10, 22, (w - chaise) / 2 + 10, pen - 4)
    return s + T((w - chaise) / 2 + 10, (22 + pen) / 2 - 7 * K(), nome, 11, True) + T((w - chaise) / 2 + 10, (22 + pen) / 2 + 7 * K(), f"{w}×{d}", 11)


def poltrona(w, d, fill, nome):
    s = R(0, 0, w, d, fill, rx=6)
    s += R(0, 0, w, 20, "#e6d8bf", rx=6) + R(0, 0, 16, d, "#e6d8bf", rx=6) + R(w - 16, 0, 16, d, "#e6d8bf", rx=6)
    return s


def letto(w, d, fill, nome, cuscini):
    s = R(0, 0, w, d, fill)
    s += R(0, 0, w, 8, "#d6cce6", rx=1)             # testiera (in alto)
    pw = (w - 20 - (cuscini - 1) * 6) / cuscini
    for i in range(cuscini):
        s += R(10 + i * (pw + 6), 14, pw, 34, "#fff", rx=6)
    s += L(0, 72, w, 72)                              # risvolto lenzuolo
    s += L(0, 72, 18, 90, dash="4 3")
    return s + etichetta(w, d, nome, cy=(72 + d) / 2)


def comodino(w, d, fill, nome):
    return R(0, 0, w, d, fill) + L(4, d - 8, w - 4, d - 8) + C(w / 2, d - 16, 2.5, "#fff", 1)


def armadio(w, d, fill, nome, ante):
    s = R(0, 0, w, d, fill)
    s += L(0, d - 6, w, d - 6)                         # filo ante (fronte)
    a = w / ante
    for i in range(1, ante):
        s += L(i * a, d - 6, i * a, d)
    s += L(6, d / 2 - 4, w - 6, d / 2 - 4, dash="6 4")  # asta appendiabiti
    for i in range(ante):                            # grucce stilizzate
        x = i * a + a / 2
        s += L(x - 12, d / 2 - 14, x + 12, d / 2 + 6, sw=0.8)
    return s + etichetta(w, d, nome, cy=d / 2 + 12) if d >= 55 else s


def cassettiera(w, d, fill, nome, cassetti):
    s = R(0, 0, w, d, fill) + L(0, d - 6, w, d - 6)
    c = w / cassetti
    for i in range(1, cassetti):
        s += L(i * c, d - 6, i * c, d)
    return s + etichetta(w, d, nome, cy=(d - 6) / 2)


def sedia(w, d, fill, nome):
    return R(3, 8, w - 6, d - 10, fill, rx=4) + R(2, 0, w - 4, 8, "#d8d8d8", rx=2)


def tavolo(w, d, fill, nome):
    return R(0, 0, w, d, fill, rx=3) + etichetta(w, d, nome)


def tavolo_tondo(w, d, fill, nome):
    return C(w / 2, d / 2, w / 2 - SW / 2, fill) + T(w / 2, d / 2 - 7 * K(), nome, 11, True) + T(w / 2, d / 2 + 7 * K(), f"Ø{w}", 11)


def tavolo_sedie(w, d, fill, nome, tw, td, per_lato):
    """Tavolo tw x td centrato, sedie sui lati lunghi (sopra e sotto)."""
    s = ""
    ty = (d - td) / 2
    tx = (w - tw) / 2
    cw = 42
    passo = tw / per_lato
    for i in range(per_lato):
        x = tx + i * passo + (passo - cw) / 2
        s += (f'<g transform="translate({x},{0})">' + sedia(cw, 45, "#f7f7f7", "") + "</g>")
        s += (f'<g transform="translate({x + cw},{d}) rotate(180)">' + sedia(cw, 45, "#f7f7f7", "") + "</g>")
    s += R(tx, ty, tw, td, fill, rx=3)
    return s + T(w / 2, d / 2 - 7 * K(), nome, 11, True) + T(w / 2, d / 2 + 7 * K(), f"{tw}×{td}", 11)


def mobile_tv(w, d, fill, nome):
    return R(0, 0, w, d, fill) + R(w * 0.18, 4, w * 0.64, 5, "#222", rx=1) + etichetta(w, d, nome, cy=d / 2 + 5)


def libreria(w, d, fill, nome):
    s = R(0, 0, w, d, fill)
    n = max(1, round(w / 50))
    for i in range(1, n):
        s += L(i * w / n, 0, i * w / n, d)
    return s + L(0, 0, w, d, sw=0.6) + L(w, 0, 0, d, sw=0.6)


def tappeto(w, d, fill, nome):
    s = R(0, 0, w, d, fill, rx=0, dash="8 5")
    s += R(8, 8, w - 16, d - 16, "none", rx=0, sw=0.8)
    return s + etichetta(w, d, nome)


def tavolino_tondo(w, d, fill, nome):
    return C(w / 2, d / 2, w / 2 - SW / 2, fill) + T(w / 2, d / 2, f"Ø{w}", 11)


# --- cucina (fronte in basso, muro in alto)
def base_cucina(w, d, fill, nome):
    return R(0, 0, w, d, fill) + L(0, d - 4, w, d - 4) + etichetta(w, d, nome, cy=(d - 4) / 2)


def lavello(w, d, fill, nome):
    s = R(0, 0, w, d, fill) + L(0, d - 4, w, d - 4)
    s += R(8, 12, w - 16, d - 24, "#fff", rx=8)
    return s + C(w / 2, 7, 2.5, "#fff", 1) + C(w / 2, d / 2 + 2, 3, "#fff", 1)


def piano_cottura(w, d, fill, nome):
    s = R(0, 0, w, d, fill) + L(0, d - 4, w, d - 4)
    for cx, cy, r in ((w * 0.3, d * 0.3, 9), (w * 0.7, d * 0.3, 7), (w * 0.3, d * 0.68, 7), (w * 0.7, d * 0.68, 10)):
        s += C(cx, cy, r, "#fff", 1.2)
    return s


def elettrodomestico(w, d, fill, nome, sigla):
    return R(0, 0, w, d, fill) + L(0, d - 4, w, d - 4) + L(0, 0, w, d - 4, sw=0.6) + T(w / 2, d / 2 - 2, sigla, 13, True)


# --- bagno (muro in alto)
def wc(w, d, fill, nome):
    return R(2, 0, w - 4, 18, fill) + E(w / 2, 18 + (d - 18) / 2, w / 2 - 1, (d - 18) / 2 - 1, "#fff")


def bidet(w, d, fill, nome):
    return R(4, 0, w - 8, 10, fill) + E(w / 2, 10 + (d - 10) / 2, w / 2 - 1, (d - 10) / 2 - 1, "#fff") + C(w / 2, 20, 2.5, "#fff", 1)


def lavabo(w, d, fill, nome):
    return R(0, 0, w, d, fill) + E(w / 2, d / 2 + 3, w / 2 - 10, d / 2 - 9, "#fff") + C(w / 2, 6, 2.5, "#fff", 1)


def doccia(w, d, fill, nome):
    s = R(0, 0, w, d, fill) + L(0, 0, w, d, sw=0.7) + L(w, 0, 0, d, sw=0.7) + C(w / 2, d / 2, 4, "#fff", 1)
    return s + T(w / 2, d - 12, f"doccia {w}×{d}", 10)


def vasca(w, d, fill, nome):
    return R(0, 0, w, d, fill) + R(8, 8, w - 16, d - 16, "#fff", rx=18) + C(22, d / 2, 3, "#fff", 1) + T(w / 2 + 10, d / 2, f"vasca {w}×{d}", 11)


def lavatrice(w, d, fill, nome):
    return R(0, 0, w, d, fill) + C(w / 2, d / 2 + 2, min(w, d) / 2 - 10, "#fff", 1.2) + T(w / 2, d / 2 + 2, "LV", 11, True)


def pianta(w, d, fill, nome):
    s = C(w / 2, d / 2, w / 2 - 1, fill, 1.2)
    for a in range(0, 360, 45):
        s += (f'<ellipse cx="{w/2}" cy="{d/2 - w*0.22}" rx="{w*0.09}" ry="{w*0.2}" fill="#b9d6ad" stroke="#6e8f63" '
              f'stroke-width="0.8" transform="rotate({a} {w/2} {d/2})"/>')
    return s


# ------------------------------------------------------------------ catalogo
# (categoria, file, nome, w, d, funzione, simmetria, extra)
# simmetria: 'tondo' -> 1 rotazione, 'doppia' -> r0/r90, None -> 4 rotazioni
CATALOGO = [
    ("soggiorno", "divano_3posti", "divano 3 posti", 220, 90, divano, None, {"posti": 3}),
    ("soggiorno", "divano_2posti", "divano 2 posti", 160, 90, divano, None, {"posti": 2}),
    ("soggiorno", "divano_angolare", "divano angolare", 240, 160, divano_angolare, None, {}),
    ("soggiorno", "poltrona", "poltrona", 80, 80, poltrona, None, {}),
    ("soggiorno", "tavolino", "tavolino", 100, 50, tavolo, "doppia", {}),
    ("soggiorno", "tavolino_tondo", "tavolino tondo", 60, 60, tavolino_tondo, "tondo", {}),
    ("soggiorno", "mobile_tv", "mobile TV", 180, 40, mobile_tv, None, {}),
    ("soggiorno", "libreria", "libreria", 100, 35, libreria, None, {}),
    ("soggiorno", "tappeto", "tappeto", 200, 140, tappeto, "doppia", {}),
    ("camera", "letto_matrimoniale", "letto matrimoniale", 160, 200, letto, None, {"cuscini": 2}),
    ("camera", "letto_piazza_e_mezza", "letto 1 piazza ½", 120, 200, letto, None, {"cuscini": 1}),
    ("camera", "letto_singolo", "letto singolo", 90, 200, letto, None, {"cuscini": 1}),
    ("camera", "comodino", "comodino", 45, 40, comodino, None, {}),
    ("camera", "armadio_2ante", "armadio 2 ante", 100, 60, armadio, None, {"ante": 2}),
    ("camera", "armadio_3ante", "armadio 3 ante", 150, 60, armadio, None, {"ante": 3}),
    ("camera", "armadio_4ante", "armadio 4 ante", 200, 60, armadio, None, {"ante": 4}),
    ("camera", "como", "comò", 100, 45, cassettiera, None, {"cassetti": 2}),
    ("camera", "scrivania", "scrivania", 120, 60, tavolo, None, {}),
    ("camera", "sedia", "sedia", 45, 50, sedia, None, {}),
    ("cucina", "modulo_base_60", "base", 60, 60, base_cucina, None, {}),
    ("cucina", "modulo_base_45", "base", 45, 60, base_cucina, None, {}),
    ("cucina", "lavello", "lavello", 80, 60, lavello, None, {}),
    ("cucina", "piano_cottura", "piano cottura", 60, 60, piano_cottura, None, {}),
    ("cucina", "frigorifero", "frigo", 60, 65, elettrodomestico, None, {"sigla": "FR"}),
    ("cucina", "lavastoviglie", "lavastoviglie", 60, 60, elettrodomestico, None, {"sigla": "LS"}),
    ("cucina", "colonna_forno", "forno", 60, 60, elettrodomestico, None, {"sigla": "FO"}),
    ("cucina", "tavolo_120x80_4sedie", "tavolo 4 posti", 120, 160, tavolo_sedie, "doppia", {"tw": 120, "td": 80, "per_lato": 2}),
    ("cucina", "tavolo_80x80_2sedie", "tavolo 2 posti", 80, 160, tavolo_sedie, "doppia", {"tw": 80, "td": 80, "per_lato": 1}),
    ("cucina", "tavolo_tondo_90", "tavolo", 90, 90, tavolo_tondo, "tondo", {}),
    ("bagno", "wc", "wc", 38, 55, wc, None, {}),
    ("bagno", "bidet", "bidet", 38, 55, bidet, None, {}),
    ("bagno", "lavabo_60", "lavabo", 60, 45, lavabo, None, {}),
    ("bagno", "mobile_lavabo_80", "mobile lavabo", 80, 50, lavabo, None, {}),
    ("bagno", "doccia_80x80", "doccia", 80, 80, doccia, None, {}),
    ("bagno", "doccia_100x80", "doccia", 100, 80, doccia, None, {}),
    ("bagno", "doccia_120x80", "doccia", 120, 80, doccia, None, {}),
    ("bagno", "vasca_170x70", "vasca", 170, 70, vasca, None, {}),
    ("bagno", "lavatrice", "lavatrice", 60, 60, lavatrice, None, {}),
    ("ingresso", "scarpiera", "scarpiera", 100, 35, box, None, {}),
    ("ingresso", "mobile_ingresso", "mobile", 80, 40, box, None, {}),
    ("ingresso", "armadio_ingresso", "armadio ingresso", 120, 60, armadio, None, {"ante": 2}),
    ("ingresso", "consolle", "consolle", 100, 30, box, None, {}),
    ("complementi", "pianta_40", "pianta", 40, 40, pianta, "tondo", {}),
    ("complementi", "pianta_60", "pianta", 60, 60, pianta, "tondo", {}),
]


def disegna(voce):
    cat, _, nome, w, d, fn, _, extra = voce
    return fn(w, d, COL[cat], nome, **extra)


def svg_pezzo(voce, rot):
    global ROT
    cat, file, nome, w, d, fn, _, extra = voce
    ROT = rot
    body = disegna(voce)
    ROT = 0
    if rot == 0:
        vw, vh, tr = w, d, ""
    elif rot == 90:
        vw, vh, tr = d, w, f"translate({d},0) rotate(90)"
    elif rot == 180:
        vw, vh, tr = w, d, f"translate({w},{d}) rotate(180)"
    else:
        vw, vh, tr = d, w, f"translate(0,{w}) rotate(270)"
    # margine di 1 cm per non tagliare il tratto; le dimensioni restano in scala
    m = 1
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{(vw+2*m)*PX_CM:.1f}" height="{(vh+2*m)*PX_CM:.1f}" '
            f'viewBox="{-m} {-m} {vw+2*m} {vh+2*m}" font-family="Helvetica, Arial, sans-serif">'
            f'<title>{nome} {w}x{d} cm</title><g transform="{tr}">{body}</g></svg>')


def rotazioni(sim):
    return [0] if sim == "tondo" else [0, 90] if sim == "doppia" else [0, 90, 180, 270]


# ------------------------------------------------------------------ foglio catalogo
def foglio_catalogo():
    # coordinate in cm (poi scalate a px con PX_CM): tutto in scala 1:50 come la pianta
    col_w = 330
    cats = list(COL)
    blocchi = []
    y = 0
    out = []
    ordine = ["soggiorno", "camera", "cucina", "bagno", "ingresso", "complementi"]
    titoli = {"soggiorno": "SOGGIORNO", "camera": "CAMERA", "cucina": "CUCINA",
              "bagno": "BAGNO", "ingresso": "INGRESSO / CORRIDOIO", "complementi": "COMPLEMENTI"}
    W = 1500
    x0, y = 40, 170
    out.append(f'<text x="40" y="60" font-size="44" font-weight="700" letter-spacing="3" fill="#1d1d1d">LIBRERIA ARREDI</text>')
    out.append(f'<text x="40" y="105" font-size="20" fill="#555">Scala 1:50 come la pianta (80 px = 1 m) · misure in cm · lato di utilizzo in basso (rotazione r0)</text>')
    for cat in ordine:
        voci = [v for v in CATALOGO if v[0] == cat]
        out.append(f'<text x="{x0}" y="{y}" font-size="24" font-weight="700" letter-spacing="2" fill="#1d1d1d">{titoli[cat]}</text>')
        out.append(f'<line x1="{x0}" y1="{y+10}" x2="{W-40}" y2="{y+10}" stroke="#bbb" stroke-width="1.5"/>')
        y += 40
        x = x0
        riga_h = 0
        for v in voci:
            w, d = v[3], v[4]
            if x + w > W - 40:
                x = x0
                y += riga_h + 60
                riga_h = 0
            out.append(f'<g transform="translate({x},{y})">{disegna(v)}</g>')
            out.append(f'<text x="{x + w/2}" y="{y + d + 20}" font-size="15" text-anchor="middle" fill="#333">{v[2]}</text>')
            out.append(f'<text x="{x + w/2}" y="{y + d + 38}" font-size="13" text-anchor="middle" fill="#777">{v[3]}×{v[4]} cm</text>')
            x += max(w, 110) + 45
            riga_h = max(riga_h, d)
        y += riga_h + 100
    H = y
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W*PX_CM:.0f}" height="{H*PX_CM:.0f}" '
            f'viewBox="0 0 {W} {H}" font-family="Helvetica, Arial, sans-serif">'
            f'<title>Libreria arredi - scala 1:50</title><rect width="{W}" height="{H}" fill="#fff"/>'
            + "".join(out) + "</svg>")


if __name__ == "__main__":
    base = "libreria_arredi"
    n = 0
    for v in CATALOGO:
        cat, file, nome, w, d, fn, sim, extra = v
        for rot in rotazioni(sim):
            s = svg_pezzo(v, rot)
            nomefile = f"{file}_{w}x{d}_r{rot}"
            for fmt in ("svg", "png"):
                os.makedirs(os.path.join(base, fmt, cat), exist_ok=True)
            with open(os.path.join(base, "svg", cat, nomefile + ".svg"), "w", encoding="utf-8") as f:
                f.write(s)
            cairosvg.svg2png(bytestring=s.encode(), write_to=os.path.join(base, "png", cat, nomefile + ".png"),
                             scale=PNG_SCALE)
            n += 1
    cat_svg = foglio_catalogo()
    with open(os.path.join(base, "catalogo_arredi.svg"), "w", encoding="utf-8") as f:
        f.write(cat_svg)
    cairosvg.svg2png(bytestring=cat_svg.encode(), write_to=os.path.join(base, "catalogo_arredi.png"), scale=2)
    print(f"{len(CATALOGO)} arredi, {n} file per formato")
