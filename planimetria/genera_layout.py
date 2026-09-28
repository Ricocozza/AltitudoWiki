"""Proposte di layout d'arredo per l'abitazione (Via Isonzo).

Riusa la geometria di genera_pianta_abitazione.py e i disegni di
genera_libreria_arredi.py (stessa scala: 80 px = 1 m, stampa 1:50 su A3).

Convenzione grafica opere (come negli elaborati edilizi):
  giallo = demolizioni, rosso = nuove costruzioni.
Le quote verdi sono le verifiche degli spazi di passaggio/uso, in cm.
"""
import genera_pianta_abitazione as gp
import genera_libreria_arredi as lib

S = gp.S
LX, LY, ME, MI = gp.LX, gp.LY, gp.ME, gp.MI
IX0, IX1, IY0, IY1 = gp.IN_X0, gp.IN_X1, gp.IN_Y0, gp.IN_Y1
C_OK = "#2e7d32"
C_DEM = "#f9c80e"

CAT = {v[1]: v for v in lib.CATALOGO}
FACING = {"giu": 0, "sx": 90, "su": 180, "dx": 270}   # verso cui guarda il lato di utilizzo

# ------------------------------------------------------------------ pareti interne esistenti
PARETI = {
    "long_bagno_salotto": (2.80, 0.30, 2.90, 4.70),
    "long_corr_camera":   (2.80, 4.70, 2.90, 7.90),
    "long_corr_cucina":   (2.80, 7.90, 2.90, 10.05),
    "bagno_corr":         (0.30, 3.00, 2.80, 3.10),
    "salotto_camera":     (2.90, 4.60, 6.15, 4.70),
    "camera_cucina":      (2.90, 7.80, 6.15, 7.90),
}


# ------------------------------------------------------------------ helper disegno
def mob(t, voce, x, y, facing="giu"):
    """Posiziona un arredo della libreria: (x, y) = angolo in alto a sinistra
    dell'ingombro già ruotato, in metri."""
    if isinstance(voce, str):
        voce = CAT[voce]
    w, d = voce[3], voce[4]
    rot = FACING[facing]
    lib.ROT = rot
    body = lib.disegna(voce)
    lib.ROT = 0
    tr = {0: "", 90: f"translate({d},0) rotate(90)", 180: f"translate({w},{d}) rotate(180)",
          270: f"translate(0,{w}) rotate(270)"}[rot]
    X, Y = gp.P(x, y)
    t.w(f'<g transform="translate({X:.1f},{Y:.1f}) scale({lib.PX_CM})"><g transform="{tr}">{body}</g></g>')


def su_misura(cat, nome, fn, w, d, **extra):
    """Voce fuori catalogo (es. tavolo 80x120 a parete, penisola)."""
    return (cat, "custom", nome, w, d, fn, None, extra)


def muro(t, r, colore=gp.C_WALL):
    t.rect(*r, fill=colore)


def demolito(t, r):
    t.rect(*r, fill=C_DEM, stroke="#b28704", stroke_width=1, stroke_dasharray="4 2")


def verifica(t, p1, p2, testo=None):
    """Quota verde di verifica spazio (valore in cm)."""
    (x1, y1), (x2, y2) = gp.P(*p1), gp.P(*p2)
    v = round(abs((p2[0] - p1[0]) + (p2[1] - p1[1])) * 100)
    testo = testo or str(v)
    t.w(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{C_OK}" stroke-width="1.4" '
        f'marker-start="url(#fr)" marker-end="url(#fr)"/>')
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    tw = len(testo) * 7 + 8
    t.w(f'<rect x="{mx-tw/2:.1f}" y="{my-8:.1f}" width="{tw}" height="16" rx="8" fill="{C_OK}"/>'
        f'<text x="{mx:.1f}" y="{my+0.5:.1f}" font-size="10.5" font-weight="700" fill="#fff" text-anchor="middle" '
        f'dominant-baseline="middle">{testo}</text>')


def scorrevole_esterno(t, y0, y1, xf, lato=-1):
    """Porta scorrevole esterno muro su parete verticale (binario sul lato 'lato')."""
    t.rect(xf, y0, xf + MI, y1, fill="#fff")
    t.line(xf, y0, xf + MI, y0, stroke=gp.C_WALL, stroke_width=1.5)
    t.line(xf, y1, xf + MI, y1, stroke=gp.C_WALL, stroke_width=1.5)
    xa = xf - 0.08 if lato < 0 else xf + MI + 0.02
    t.rect(xa, y0, xa + 0.06, y1, fill=gp.C_DOOR)
    t.rect(xa, y1, xa + 0.06, y1 + (y1 - y0), fill="none", stroke=gp.C_DOOR, stroke_width=1, stroke_dasharray="4 3")


def etichetta(t, nome, area, x, y, rot=0):
    X, Y = gp.P(x, y)
    w = max(len(nome) * 8.5 + 16, 88)
    t.w(f'<g transform="rotate({rot} {X:.1f} {Y:.1f})">'
        f'<rect x="{X-w/2:.1f}" y="{Y-17:.1f}" width="{w:.0f}" height="34" rx="4" fill="#fff" fill-opacity="0.92" stroke="#333" stroke-width="0.7"/>'
        f'<text x="{X:.1f}" y="{Y-6:.1f}" font-size="12" text-anchor="middle" dominant-baseline="middle" class="lbl">{nome}</text>'
        f'<text x="{X:.1f}" y="{Y+8:.1f}" font-size="10.5" fill="#444" text-anchor="middle" dominant-baseline="middle">{gp.fmt(area)} m²</text></g>')


def area(*rects):
    return sum((r[2] - r[0]) * (r[3] - r[1]) for r in rects)


# ------------------------------------------------------------------ arredi comuni
def bagno(t):
    mob(t, "mobile_lavabo_80", 0.40, 0.30)
    mob(t, "lavatrice", 1.20, 0.30)
    mob(t, "doccia_100x80", 1.80, 0.30)
    mob(t, "bidet", 0.30, 1.71, "dx")
    mob(t, "wc", 0.30, 2.36, "dx")


def cucina(t):
    # blocco sul muro degli ingressi (fronte verso l'alto)
    mob(t, "frigorifero", 4.15, IY1 - 0.65, "su")
    mob(t, "lavello", 4.75, IY1 - 0.60, "su")
    mob(t, "piano_cottura", 5.55, IY1 - 0.60, "su")
    # ritorno sul muro Sud, sotto la finestra F5 (fronte verso sinistra)
    mob(t, "modulo_base_60", IX1 - 0.60, 7.95, "sx")
    mob(t, "lavastoviglie", IX1 - 0.60, 8.55, "sx")
    mob(t, su_misura("cucina", "", lib.box, 60, 30), IX1 - 0.60, 9.15)   # compensatore angolo


def camera_matrimoniale_est(t):
    """Camera nell'ex salotto (lato Est cieco): letto a parete, armadio 200, comò."""
    x0 = 2.90
    cx = (x0 + IX1) / 2
    mob(t, "letto_matrimoniale", cx - 0.80, IY0)
    mob(t, "comodino", cx - 1.25, IY0)
    mob(t, "comodino", cx + 0.80, IY0)
    mob(t, "armadio_4ante", 3.95, 4.00, "su")
    mob(t, "como", x0, 2.45, "dx")


def tavolo_parete(t, y0=4.00):
    """Tavolo 80x120 a parete sotto F2 con 4 sedie (2 laterali + 2 in testa)."""
    mob(t, su_misura("soggiorno", "tavolo", lib.tavolo, 80, 120), IX0, y0)
    for yy in (y0 + 0.10, y0 + 0.65):
        mob(t, "sedia", IX0 + 0.85, yy, "sx")
    mob(t, "sedia", IX0 + 0.175, y0 - 0.50, "giu")
    mob(t, "sedia", IX0 + 0.175, y0 + 1.20, "su")


# ------------------------------------------------------------------ layout
def layout_A(t):
    pareti = dict(PARETI)
    for r in pareti.values():
        muro(t, r)
    finestre(t)
    bagno(t)
    # salotto
    cx = (2.90 + IX1) / 2
    mob(t, "tappeto", cx - 1.00, 1.15)
    mob(t, "mobile_tv", cx - 0.90, IY0)
    mob(t, "tavolino", cx - 0.50, 1.40)
    mob(t, "divano_3posti", cx - 1.10, 2.30, "su")
    mob(t, "poltrona", 2.95, 1.10, "dx")
    mob(t, "libreria", 4.60, 4.25, "su")
    # camera
    mob(t, "letto_matrimoniale", cx - 0.80, 4.70)
    mob(t, "comodino", cx - 1.25, 4.70)
    mob(t, "comodino", cx + 0.80, 4.70)
    # corridoio abitabile: pranzo + guardaroba + ingresso
    tavolo_parete(t)
    mob(t, "armadio_4ante", IX0, 5.95, "dx")
    mob(t, "scarpiera", IX0, 8.05, "dx")
    mob(t, "consolle", 2.50, 6.50, "sx")
    mob(t, "pianta_40", 2.35, 9.55)
    cucina(t)
    # porte
    gp.porta_scorrevole(t, 1.85, 2.65, gp.Y_BAGNO, MI, -1)
    gp.porta_battente(t, "P4", "v", 3.65, 4.45, 1, +1, MI, 2.80)
    scorrevole_esterno(t, 4.80, 5.60, 2.80, -1)
    gp.porta_battente(t, "P6", "v", 8.05, 8.85, 0, +1, MI, 2.80)
    porte_esterne(t)
    # verifiche
    verifica(t, (1.65, 4.40), (2.80, 4.40))
    verifica(t, (0.90, 7.00), (2.50, 7.00))
    verifica(t, (5.25, 0.70), (5.25, 2.30))
    verifica(t, (4.525, 6.70), (4.525, 7.80))
    verifica(t, (5.325, 5.80), (IX1, 5.80))
    verifica(t, (5.20, 7.90), (5.20, IY1 - 0.60))
    verifica(t, (0.85, 2.55), (2.80, 2.55))
    etichetta(t, "SALOTTO", area((2.90, 0.30, 6.15, 4.60)), cx, 3.75)
    etichetta(t, "CAMERA", area((2.90, 4.70, 6.15, 7.80)), cx - 0.95, 7.25)
    etichetta(t, "CUCINA", area((2.90, 7.90, 6.15, 10.05)), 4.00, 8.45)
    etichetta(t, "BAGNO", area((0.30, 0.30, 2.80, 3.00)), 1.55, 1.75)
    etichetta(t, "INGRESSO · PRANZO", area((0.30, 3.10, 2.80, 10.05)), 1.70, 7.10, -90)
    zone = [("Salotto", (2.90, 0.30, 6.15, 4.60)), ("Camera", (2.90, 4.70, 6.15, 7.80)),
            ("Cucina", (2.90, 7.90, 6.15, 10.05)), ("Bagno", (0.30, 0.30, 2.80, 3.00)),
            ("Ingresso · pranzo", (0.30, 3.10, 2.80, 10.05))]
    return zone


def layout_B(t):
    for k in ("long_bagno_salotto", "bagno_corr", "salotto_camera"):
        muro(t, PARETI[k])
    for k in ("long_corr_camera", "long_corr_cucina", "camera_cucina"):
        demolito(t, PARETI[k])
    finestre(t)
    bagno(t)
    camera_matrimoniale_est(t)
    # disimpegno: armadio contro il muro del bagno
    mob(t, "armadio_3ante", IX0, 3.10)
    # living
    mob(t, "tappeto", 3.30, 5.10)
    mob(t, "mobile_tv", 3.40, 4.70)
    mob(t, "tavolino", 3.80, 5.45)
    mob(t, "divano_3posti", 3.20, 6.35, "su")
    mob(t, "poltrona", 2.30, 5.30, "dx")
    mob(t, "pianta_60", 5.50, 5.15)
    # angolo studio sotto F2
    mob(t, "scrivania", IX0, 5.30, "dx")
    mob(t, "sedia", 0.95, 5.675, "sx")
    # pranzo
    mob(t, "tavolo_120x80_4sedie", 1.20, 7.40, "sx")
    mob(t, "scarpiera", IX0, 8.05, "dx")
    cucina(t)
    gp.porta_scorrevole(t, 1.85, 2.65, gp.Y_BAGNO, MI, -1)
    gp.porta_battente(t, "P4", "v", 3.65, 4.45, 1, +1, MI, 2.80)
    porte_esterne(t)
    verifica(t, (5.30, 5.10), (5.30, 6.35))
    verifica(t, (4.95, 7.25), (4.95, IY1 - 0.60))
    verifica(t, (4.525, 2.30), (4.525, 4.00))
    verifica(t, (1.45, 5.90), (2.30, 5.90))
    verifica(t, (1.70, 8.60), (1.70, IY1))
    verifica(t, (1.00, 3.70), (1.00, 5.30))
    cx = (2.90 + IX1) / 2
    etichetta(t, "CAMERA", area((2.90, 0.30, 6.15, 4.60)), cx, 3.15)
    etichetta(t, "BAGNO", area((0.30, 0.30, 2.80, 3.00)), 1.55, 1.75)
    etichetta(t, "ZONA GIORNO", area((0.30, 4.70, 6.15, 10.05)), 3.75, 7.62)
    zone = [("Camera", (2.90, 0.30, 6.15, 4.60)), ("Bagno", (0.30, 0.30, 2.80, 3.00)),
            ("Disimpegno", (0.30, 3.10, 2.80, 4.70)),
            ("Living · pranzo · cucina", (0.30, 4.70, 6.15, 10.05))]
    return zone


def layout_C(t):
    for k, r in PARETI.items():
        (demolito if k == "long_corr_cucina" else muro)(t, r)
    finestre(t)
    bagno(t)
    camera_matrimoniale_est(t)
    # cameretta / studio
    mob(t, "letto_singolo", 4.15, 6.90, "sx")
    mob(t, "scrivania", 4.60, 4.70)
    mob(t, "sedia", 4.975, 5.30, "su")
    mob(t, "armadio_2ante", 2.90, 5.80, "dx")
    # soggiorno nel corridoio
    tavolo_parete(t)
    mob(t, "divano_2posti", IX0, 6.00, "dx")
    mob(t, "mobile_tv", 2.40, 5.90, "sx")
    mob(t, "scarpiera", IX0, 8.05, "dx")
    mob(t, "pianta_40", 2.35, 9.55)
    cucina(t)
    gp.porta_scorrevole(t, 1.85, 2.65, gp.Y_BAGNO, MI, -1)
    gp.porta_battente(t, "P4", "v", 3.65, 4.45, 1, +1, MI, 2.80)
    gp.porta_battente(t, "P5", "v", 4.80, 5.60, 1, +1, MI, 2.80)
    porte_esterne(t)
    verifica(t, (1.20, 6.80), (2.40, 6.80))
    verifica(t, (1.65, 4.40), (2.80, 4.40))
    verifica(t, (4.525, 2.30), (4.525, 4.00))
    verifica(t, (5.20, 5.80), (5.20, 6.90))
    verifica(t, (5.20, 7.90), (5.20, IY1 - 0.60))
    cx = (2.90 + IX1) / 2
    etichetta(t, "CAMERA", area((2.90, 0.30, 6.15, 4.60)), cx, 3.15)
    etichetta(t, "CAMERETTA", area((2.90, 4.70, 6.15, 7.80)), 4.30, 6.35)
    etichetta(t, "BAGNO", area((0.30, 0.30, 2.80, 3.00)), 1.55, 1.75)
    etichetta(t, "CUCINA", area((2.90, 7.90, 6.15, 10.05)), 4.15, 8.45)
    etichetta(t, "SOGGIORNO", area((0.30, 3.10, 2.80, 10.05)), 1.75, 8.30)
    zone = [("Camera", (2.90, 0.30, 6.15, 4.60)), ("Cameretta · studio", (2.90, 4.70, 6.15, 7.80)),
            ("Bagno", (0.30, 0.30, 2.80, 3.00)),
            ("Soggiorno · pranzo · cucina", (0.30, 3.10, 2.80, 10.05), (2.80, 7.90, 6.15, 10.05))]
    return zone


def finestre(t):
    for fid, _, lato, y0, y1, ante in gp.FINESTRE:
        gp.finestra(t, fid, lato, y0, y1, ante, tag=False)


def porte_esterne(t):
    gp.porta_battente(t, "P1", "h", 1.20, 2.20, 1, -1, ME, IY1)
    gp.porta_battente(t, "P2", "h", 3.10, 4.00, 0, -1, ME, IY1)


# ------------------------------------------------------------------ testi schede
SCHEDE = {
    "A": dict(
        titolo="LAYOUT A — ESSENZIALE",
        sotto="Nessuna opera muraria · solo arredo",
        concept=["Distribuzione invariata. Il corridoio (17 m², il 31%",
                 "della casa) diventa uno spazio abitabile: ingresso,",
                 "zona pranzo sotto la finestra F2 e guardaroba."],
        opere=["• P5 camera → porta scorrevole esterno muro",
               "  (risolve il conflitto anta / comodino)"],
        pro=["• Costo minimo, nessuna pratica edilizia",
             "• Salotto e camera separati e silenziosi",
             "• Guardaroba 200 cm + scarpiera all'ingresso",
             "• Divano a 1,60 m dalla TV: fino a 55\""],
        contro=["• Cucina chiusa 7 m² senza tavolo",
                "• Camera senza armadio al suo interno",
                "• Pranzo nel passaggio verso le stanze"]),
    "B": dict(
        titolo="LAYOUT B — OPEN SPACE",
        sotto="Demolizioni · zona giorno unica di 31 m²",
        concept=["La camera va sul lato Est (cieco, verso il",
                 "confine: il più silenzioso). Corridoio, vecchia",
                 "camera e cucina diventano un unico ambiente con",
                 "due finestre a Sud: living, pranzo, cucina, studio."],
        opere=["• Demolire tramezzo corridoio/camera/cucina (5,35 m)",
               "• Demolire tramezzo camera/cucina (3,25 m)",
               "• Verificare se il muro longitudinale è portante:",
               "  se sì serve una trave (progetto strutturale)"],
        pro=["• Zona giorno luminosa, flessibile, conviviale",
             "• Camera 14 m² con armadio 200 cm e comò",
             "• Angolo studio / smart working sotto F2",
             "• Corridoio ridotto a un disimpegno di 4 m²"],
        contro=["• Opere + pratica edilizia (CILA) + possibile",
                "  intervento strutturale",
                "• Cucina a vista: serve una cappa efficiente",
                "• Una sola camera"]),
    "C": dict(
        titolo="LAYOUT C — DUE CAMERE",
        sotto="Demolizione del solo tramezzo corridoio/cucina",
        concept=["Camera matrimoniale nell'ex salotto, cameretta o",
                 "studio nell'ex camera. Il corridoio diventa un",
                 "soggiorno compatto, aperto sulla cucina."],
        opere=["• Demolire tramezzo corridoio/cucina (2,15 m)",
               "• P5: invertire il lato cerniera (verso la cucina)"],
        pro=["• Due camere: figli, ospiti o studio chiuso",
             "• Opere minime, impianti cucina invariati",
             "• Casa più versatile e rivendibile"],
        contro=["• Soggiorno largo 2,50 m: divano 2 posti,",
                "  TV a 1,20 m (max 40-43\")",
                "• Pranzo nel passaggio verso le camere",
                "• Cameretta 10 m²: niente letto matrimoniale"]),
}

BEST = ["Passaggi principali ≥ 90 cm · lato letto ≥ 60 cm",
        "Fronte armadio ≥ 90 cm · piede letto ≥ 70 cm",
        "Tavolino–divano 40-45 cm",
        "TV: distanza ≈ 1,2-1,5 × diagonale",
        "Corsia cucina ≥ 120 cm · frigo-lavello-cottura",
        "Dietro la sedia per alzarsi ≥ 75 cm",
        "WC: asse ≥ 40 cm dal muro, ≥ 55 cm libero davanti"]


def genera(chiave, fn, nome_file):
    t = gp.Tav()
    w = t.w
    sc = SCHEDE[chiave]
    W, H = 1400, 1100
    gp.OX, gp.OY = 150.0, 200.0
    PX = gp.OX + LX * S + 150
    w(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W*0.25:.0f}mm" height="{H*0.25:.0f}mm" viewBox="0 0 {W} {H}" font-family="Helvetica, Arial, sans-serif">
<title>{sc["titolo"]} - pianta Via Isonzo</title>
<defs>
  <pattern id="g50" width="{S/2}" height="{S/2}" patternUnits="userSpaceOnUse" x="{gp.OX + ME*S}" y="{gp.OY + ME*S}">
    <path d="M {S/2} 0 L 0 0 0 {S/2}" fill="none" stroke="#d3dce6" stroke-width="0.4"/></pattern>
  <pattern id="g100" width="{S}" height="{S}" patternUnits="userSpaceOnUse" x="{gp.OX + ME*S}" y="{gp.OY + ME*S}">
    <rect width="{S}" height="{S}" fill="url(#g50)"/>
    <path d="M {S} 0 L 0 0 0 {S}" fill="none" stroke="#bfccd9" stroke-width="0.7"/></pattern>
  <marker id="fr" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M 0 1 L 9 5 L 0 9 z" fill="{C_OK}"/></marker>
</defs>
<style>.lbl {{ font-weight:700; letter-spacing:1px; fill:#1d1d1d; }} .dim line {{ stroke:{gp.C_DIM}; stroke-width:0.7; }} .dim .ext {{ stroke-width:0.45; }} .dim .tick {{ stroke-width:1.3; }} .dim text {{ fill:{gp.C_DIM}; font-weight:600; }}</style>
<rect width="{W}" height="{H}" fill="#fff"/>
<rect x="20" y="20" width="{W-40}" height="{H-40}" fill="none" stroke="#111" stroke-width="1.5"/>
<text x="50" y="68" font-size="30" class="lbl">{sc["titolo"]}</text>
<text x="50" y="98" font-size="15" fill="#555">{sc["sotto"]} · Via Isonzo · scala 1:50 (A3) · misure in metri, verifiche in cm</text>''')

    # pavimento + griglia, poi muri perimetrali
    t.rect(IX0, IY0, IX1, IY1, fill="#fbfaf7")
    t.rect(IX0, IY0, IX1, IY1, fill="url(#g100)")
    for r in ((0, 0, LX, ME), (0, LY - ME, LX, LY), (0, 0, ME, LY), (LX - ME, 0, LX, LY)):
        muro(t, r)
    w('<g id="layout">')
    zone = fn(t)
    w('</g>')
    # quadro elettrico
    X, Y = gp.P(IX0, 9.20)
    w(f'<rect x="{X:.1f}" y="{Y-12:.1f}" width="10" height="24" fill="#ffca28" stroke="#111" stroke-width="1.2"/>')
    t.quota((0, 0), (LX, 0), gp.fmt(LX), off=0.55, lato=-1, size=12)
    t.quota((0, 0), (0, LY), gp.fmt(LY), off=0.55, lato=1, size=12)

    # ------------------------------------------------ scheda
    y = 150

    def blocco(titolo, righe, colore="#1d1d1d"):
        nonlocal y
        w(f'<text x="{PX}" y="{y}" font-size="13" class="lbl" fill="{colore}">{titolo}</text>')
        y += 20
        for r in righe:
            w(f'<text x="{PX}" y="{y}" font-size="12.5" fill="#333" xml:space="preserve">{r}</text>')
            y += 18
        y += 14

    blocco("CONCEPT", sc["concept"])
    blocco("OPERE", sc["opere"], "#8a6d00")
    blocco("VANTAGGI", sc["pro"], C_OK)
    blocco("SVANTAGGI", sc["contro"], "#c62828")

    # superfici
    w(f'<text x="{PX}" y="{y}" font-size="13" class="lbl">SUPERFICI NETTE</text>')
    y += 20
    for nome, *rects in zone:
        a = area(*rects)
        w(f'<text x="{PX}" y="{y}" font-size="12.5">{nome}</text>'
          f'<text x="{PX+360}" y="{y}" font-size="12.5" text-anchor="end" font-weight="600">{gp.fmt(a)} m²</text>'
          f'<line x1="{PX}" y1="{y+5}" x2="{PX+360}" y2="{y+5}" stroke="#e3e3e3"/>')
        y += 19
    y += 22

    blocco("BEST PRACTICE VERIFICATE", ["• " + b for b in BEST])

    # legenda
    leg = [(f'<rect width="26" height="12" fill="{gp.C_WALL}"/>', "Muro esistente"),
           (f'<rect width="26" height="12" fill="{C_DEM}" stroke="#b28704" stroke-dasharray="4 2"/>', "Da demolire"),
           (f'<rect width="26" height="12" fill="#dbeafb" stroke="{gp.C_WIN}" stroke-width="2"/>', "Finestra"),
           (f'<path d="M 0 12 L 0 -6 A 18 18 0 0 1 18 12" fill="none" stroke="{gp.C_DOOR}" stroke-width="1.5"/>', "Porta"),
           (f'<line x1="0" y1="6" x2="26" y2="6" stroke="{C_OK}" stroke-width="1.5"/><rect x="6" y="0" width="14" height="12" rx="6" fill="{C_OK}"/>', "Verifica spazio (cm)")]
    w(f'<g transform="translate({PX},{y})"><text font-size="13" class="lbl">LEGENDA</text>')
    for i, (sym, txt) in enumerate(leg):
        w(f'<g transform="translate({(i % 2) * 190},{16 + (i // 2) * 24})">{sym}<text x="36" y="10" font-size="12">{txt}</text></g>')
    w('</g></svg>')
    with open(nome_file, "w", encoding="utf-8") as f:
        f.write("\n".join(t.o))


if __name__ == "__main__":
    genera("A", layout_A, "layout_A_essenziale.svg")
    genera("B", layout_B, "layout_B_open_space.svg")
    genera("C", layout_C, "layout_C_due_camere.svg")
    print("ok")
