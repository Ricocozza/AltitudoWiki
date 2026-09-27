"""Pianta dell'abitazione (10,35 x 6,45 m) ricostruita dallo schizzo delle stanze.

Orientamento come lo schizzo: lato lungo verticale, ingressi in basso.
Coordinate in metri: origine = spigolo esterno in alto a sinistra,
x verso destra, y verso il basso.

Genera due tavole:
  pianta_abitazione_arredata.svg  -> con arredo indicativo
  pianta_abitazione_base.svg      -> solo muri, porte, finestre e griglia
"""
import math

# ------------------------------------------------------------------ dati
LX, LY = 6.45, 10.35      # sagoma esterna (da Allegato 1)
ME = 0.30                 # muro esterno (ipotesi)
MI = 0.10                 # tramezzo (ipotesi)

# asse tramezzi (misure ricavate dallo schizzo, proporzionate alla sagoma)
X_TR = 2.80               # filo sinistro del tramezzo corridoio | stanze
Y_BAGNO = 3.00            # filo superiore tramezzo bagno | corridoio
Y_SAL = 4.60              # filo superiore tramezzo salotto | camera
Y_CAM = 7.80              # filo superiore tramezzo camera | cucina

IN_X0, IN_X1 = ME, LX - ME
IN_Y0, IN_Y1 = ME, LY - ME

STANZE = {
    # nome: (x0, y0, x1, y1, colore)
    "BAGNO":         (IN_X0, IN_Y0, X_TR, Y_BAGNO, "#e6f1fa"),
    "CORRIDOIO":     (IN_X0, Y_BAGNO + MI, X_TR, IN_Y1, "#f3f3f1"),
    "SALOTTO":       (X_TR + MI, IN_Y0, IN_X1, Y_SAL, "#fcf2e2"),
    "CAMERA DA LETTO": (X_TR + MI, Y_SAL + MI, IN_X1, Y_CAM, "#efeaf7"),
    "CUCINA":        (X_TR + MI, Y_CAM + MI, IN_X1, IN_Y1, "#e8f4e8"),
}

# finestre: id, stanza, lato ('S'=sinistra,'D'=destra), y0, y1, ante
FINESTRE = [
    ("F1", "Bagno",     "S", 1.10, 2.00, 1),
    ("F2", "Corridoio", "S", 4.10, 5.10, 1),
    ("F3", "Salotto",   "D", 1.60, 2.80, 2),
    ("F4", "Camera",    "D", 5.85, 6.85, 2),
    ("F5", "Cucina",    "D", 8.20, 9.10, 1),
]

# ------------------------------------------------------------------ tavola
S = 80.0                  # unità SVG per metro (1 unità = 0,25 mm -> 1:50)
OX, OY = 190.0, 265.0
W_TAV, H_TAV = 1400, 1300
PX = OX + LX * S + 230    # colonna destra (cartiglio)

C_WALL = "#262626"
C_WIN = "#1565c0"
C_DOOR = "#c62828"
C_FURN = "#6d6d6d"
C_DIM = "#2b5d8a"


def P(x, y):
    return OX + x * S, OY + y * S


def fmt(m):
    return f"{m:.2f}".replace(".", ",")


class Tav:
    def __init__(self):
        self.o = []

    def w(self, s):
        self.o.append(s)

    def rect(self, x0, y0, x1, y1, **a):
        (X0, Y0), (X1, Y1) = P(x0, y0), P(x1, y1)
        attrs = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in a.items())
        self.w(f'<rect x="{X0:.1f}" y="{Y0:.1f}" width="{X1-X0:.1f}" height="{Y1-Y0:.1f}" {attrs}/>')

    def line(self, x0, y0, x1, y1, **a):
        (X0, Y0), (X1, Y1) = P(x0, y0), P(x1, y1)
        attrs = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in a.items())
        self.w(f'<line x1="{X0:.1f}" y1="{Y0:.1f}" x2="{X1:.1f}" y2="{Y1:.1f}" {attrs}/>')

    def arc(self, c, a, b, r, **attrs):
        """Arco di centro c da a a b (metri), verso corretto automatico."""
        (Ax, Ay), (Bx, By), (Cx, Cy) = P(*a), P(*b), P(*c)
        cross = (Ax - Cx) * (By - Cy) - (Ay - Cy) * (Bx - Cx)
        sweep = 1 if cross > 0 else 0
        at = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
        self.w(f'<path d="M {Ax:.1f} {Ay:.1f} A {r*S:.1f} {r*S:.1f} 0 0 {sweep} {Bx:.1f} {By:.1f}" fill="none" {at}/>')

    def text(self, x, y, s, size=12, anchor="middle", rot=0, **a):
        X, Y = P(x, y)
        attrs = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in a.items())
        tr = f' transform="rotate({rot} {X:.1f} {Y:.1f})"' if rot else ""
        self.w(f'<text x="{X:.1f}" y="{Y:.1f}" font-size="{size}" text-anchor="{anchor}" '
               f'dominant-baseline="middle"{tr} {attrs}>{s}</text>')

    # --------------------------------------------------------- quote
    def quota(self, p1, p2, testo, off, lato=1, size=12):
        (x1, y1), (x2, y2) = P(*p1), P(*p2)
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        nx, ny = -uy * lato, ux * lato
        o = off * S
        a = (x1 + nx * o, y1 + ny * o)
        b = (x2 + nx * o, y2 + ny * o)
        g = [f'<g class="dim">',
             f'<line x1="{x1+nx*6:.1f}" y1="{y1+ny*6:.1f}" x2="{a[0]+nx*5:.1f}" y2="{a[1]+ny*5:.1f}" class="ext"/>',
             f'<line x1="{x2+nx*6:.1f}" y1="{y2+ny*6:.1f}" x2="{b[0]+nx*5:.1f}" y2="{b[1]+ny*5:.1f}" class="ext"/>',
             f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}"/>']
        for cx, cy in (a, b):
            tx, ty = (ux + nx) * 4, (uy + ny) * 4
            g.append(f'<line x1="{cx-tx:.1f}" y1="{cy-ty:.1f}" x2="{cx+tx:.1f}" y2="{cy+ty:.1f}" class="tick"/>')
        mx, my = (a[0] + b[0]) / 2 + nx * 9, (a[1] + b[1]) / 2 + ny * 9
        ang = math.degrees(math.atan2(dy, dx))
        if ang > 90: ang -= 180
        if ang <= -90: ang += 180
        g.append(f'<text x="{mx:.1f}" y="{my:.1f}" font-size="{size}" transform="rotate({ang:.1f} {mx:.1f} {my:.1f})" '
                 f'text-anchor="middle" dominant-baseline="middle">{testo}</text></g>')
        self.w("\n".join(g))

    def catena(self, asse, punti, fisso, off, lato, size=11):
        for a, b in zip(punti, punti[1:]):
            p1, p2 = ((a, fisso), (b, fisso)) if asse == "x" else ((fisso, a), (fisso, b))
            self.quota(p1, p2, fmt(b - a), off, lato, size)


# ------------------------------------------------------------------ serramenti
def finestra(t, fid, lato, y0, y1, ante):
    xw0, xw1 = (0, ME) if lato == "S" else (LX - ME, LX)
    t.rect(xw0, y0, xw1, y1, fill="#ffffff")
    # telaio + vetro
    t.rect(xw0, y0, xw1, y1, fill="#dbeafb", stroke=C_WIN, stroke_width=2)
    xm = (xw0 + xw1) / 2
    t.line(xm - 0.03, y0, xm - 0.03, y1, stroke=C_WIN, stroke_width=1.2)
    t.line(xm + 0.03, y0, xm + 0.03, y1, stroke=C_WIN, stroke_width=1.2)
    # apertura ante verso l'interno (tratteggio)
    face = xw1 if lato == "S" else xw0
    d = 1 if lato == "S" else -1
    L = (y1 - y0) / ante
    for i in range(ante):
        ya, yb = y0 + i * L, y0 + (i + 1) * L
        hinge = ya if (ante == 1 or i == 0) else yb
        other = yb if hinge == ya else ya
        tip = (face + d * L, hinge)
        t.line(face, hinge, *tip, stroke=C_WIN, stroke_width=1, stroke_dasharray="4 3")
        t.arc((face, hinge), tip, (face, other), L, stroke=C_WIN, stroke_width=0.8, stroke_dasharray="4 3")
    # etichetta
    xl = -0.55 if lato == "S" else LX + 0.55
    cy = (y0 + y1) / 2
    X, Y = P(xl, cy)
    t.w(f'<g><rect x="{X-24:.1f}" y="{Y-19:.1f}" width="48" height="38" rx="4" fill="{C_WIN}"/>'
        f'<text x="{X:.1f}" y="{Y-6:.1f}" font-size="13" font-weight="700" fill="#fff" text-anchor="middle" dominant-baseline="middle">{fid}</text>'
        f'<text x="{X:.1f}" y="{Y+9:.1f}" font-size="11" fill="#fff" text-anchor="middle" dominant-baseline="middle">{round((y1-y0)*100)} cm</text></g>')


def porta_battente(t, pid, parete, a0, a1, cerniera, verso, spessore, filo):
    """parete 'v' (x=filo..filo+spessore) o 'h' (y=filo..filo+spessore);
    a0..a1 luce lungo la parete; cerniera 0/1 = su a0/a1; verso +1/-1 lato di apertura."""
    w = a1 - a0
    if parete == "v":
        t.rect(filo, a0, filo + spessore, a1, fill="#ffffff")
        face = filo + spessore if verso > 0 else filo
        h = a0 if cerniera == 0 else a1
        o = a1 if cerniera == 0 else a0
        tip = (face + verso * w, h)
        H, O = (face, h), (face, o)
        t.line(filo, a0, filo + spessore, a0, stroke=C_WALL, stroke_width=1.5)
        t.line(filo, a1, filo + spessore, a1, stroke=C_WALL, stroke_width=1.5)
    else:
        t.rect(a0, filo, a1, filo + spessore, fill="#ffffff")
        face = filo + spessore if verso > 0 else filo
        h = a0 if cerniera == 0 else a1
        o = a1 if cerniera == 0 else a0
        tip = (h, face + verso * w)
        H, O = (h, face), (o, face)
        t.line(a0, filo, a0, filo + spessore, stroke=C_WALL, stroke_width=1.5)
        t.line(a1, filo, a1, filo + spessore, stroke=C_WALL, stroke_width=1.5)
    t.line(*H, *tip, stroke=C_DOOR, stroke_width=2.5)
    t.arc(H, tip, O, w, stroke=C_DOOR, stroke_width=1, stroke_dasharray="5 3")
    return tip


def porta_scorrevole(t, a0, a1, filo, spessore, verso_tasca=-1):
    """Scorrevole a scomparsa su parete orizzontale."""
    w = a1 - a0
    t.rect(a0, filo, a1, filo + spessore, fill="#ffffff")
    ym = filo + spessore / 2
    t.rect(a0 - 0.02, ym - 0.025, a1 + 0.02, ym + 0.025, fill=C_DOOR)
    p0, p1 = (a0 - w, a0) if verso_tasca < 0 else (a1, a1 + w)
    t.line(p0, ym, p1, ym, stroke=C_DOOR, stroke_width=1.2, stroke_dasharray="4 3")
    t.line(a0, filo, a0, filo + spessore, stroke=C_WALL, stroke_width=1.5)
    t.line(a1, filo, a1, filo + spessore, stroke=C_WALL, stroke_width=1.5)


def tag_porta(t, pid, x, y, larg):
    X, Y = P(x, y)
    t.w(f'<g><circle cx="{X:.1f}" cy="{Y:.1f}" r="15" fill="#fff" stroke="{C_DOOR}" stroke-width="1.6"/>'
        f'<text x="{X:.1f}" y="{Y-3:.1f}" font-size="10" font-weight="700" fill="{C_DOOR}" text-anchor="middle" dominant-baseline="middle">{pid}</text>'
        f'<text x="{X:.1f}" y="{Y+7:.1f}" font-size="8" fill="{C_DOOR}" text-anchor="middle" dominant-baseline="middle">{larg}</text></g>')


# ------------------------------------------------------------------ arredo
def mobile(t, x0, y0, x1, y1, label=None, size=9, rot=0, fill="#fafafa", dash=None, col=C_FURN):
    extra = {"stroke_dasharray": dash} if dash else {}
    t.rect(x0, y0, x1, y1, fill=fill, stroke=col, stroke_width=1.3, rx=2, **extra)
    if label:
        t.text((x0 + x1) / 2, (y0 + y1) / 2, label, size=size, rot=rot, fill=col)


def arredo(t):
    g = C_FURN
    t.w('<g id="arredo">')
    # --- BAGNO
    mobile(t, 1.80, IN_Y0, X_TR, 1.20, fill="#eef6fc")                      # doccia 100x90
    t.line(1.80, IN_Y0, X_TR, 1.20, stroke=g, stroke_width=0.6)
    t.line(X_TR, IN_Y0, 1.80, 1.20, stroke=g, stroke_width=0.6)
    cx, cy = P(2.30, 0.75)
    t.w(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="4" fill="#fff" stroke="{g}"/>')
    t.text(2.30, 1.05, "doccia 100×90", size=8, fill=g)
    mobile(t, 0.50, IN_Y0, 1.10, 0.78)                                      # lavabo
    X, Y = P(0.80, 0.52)
    t.w(f'<ellipse cx="{X:.1f}" cy="{Y:.1f}" rx="16" ry="11" fill="#fff" stroke="{g}"/>')
    t.text(0.80, 0.90, "lavabo", size=8, fill=g)
    mobile(t, IN_X0, 2.41, 0.48, 2.79)                                      # wc: cassetta
    X, Y = P(0.68, 2.60)
    t.w(f'<ellipse cx="{X:.1f}" cy="{Y:.1f}" rx="{0.22*S:.1f}" ry="{0.17*S:.1f}" fill="#fff" stroke="{g}" stroke-width="1.3"/>')
    t.text(1.08, 2.60, "wc", size=8, fill=g, anchor="start")
    # --- SALOTTO
    cxs = (X_TR + MI + IN_X1) / 2
    mobile(t, cxs - 0.90, IN_Y0, cxs + 0.90, 0.72, "mobile TV 180×40", size=8)
    t.line(cxs - 0.60, 0.66, cxs + 0.60, 0.66, stroke="#222", stroke_width=3)
    mobile(t, cxs - 0.50, 1.35, cxs + 0.50, 1.85, "tavolino", size=8)
    # divano 220x90 (schienale verso il basso)
    sx0, sx1, sy0, sy1 = cxs - 1.10, cxs + 1.10, 2.10, 3.00
    mobile(t, sx0, sy0, sx1, sy1, fill="#f5ecdc")
    t.rect(sx0, sy1 - 0.20, sx1, sy1, fill="#e9dcc4", stroke=g, stroke_width=1)
    t.rect(sx0, sy0, sx0 + 0.20, sy1, fill="#e9dcc4", stroke=g, stroke_width=1)
    t.rect(sx1 - 0.20, sy0, sx1, sy1, fill="#e9dcc4", stroke=g, stroke_width=1)
    t.line(cxs, sy0, cxs, sy1 - 0.20, stroke=g, stroke_width=0.8)
    t.text(cxs, 2.45, "divano 220×90", size=8, fill=g)
    # --- CAMERA
    cxc = cxs
    bx0, bx1, by0, by1 = cxc - 0.80, cxc + 0.80, Y_SAL + MI, Y_SAL + MI + 2.00
    mobile(t, bx0, by0, bx1, by1, fill="#f6f2fb")
    t.rect(bx0, by0, bx1, by0 + 0.08, fill="#d9d0e8", stroke=g, stroke_width=1)
    mobile(t, bx0 + 0.10, by0 + 0.15, cxc - 0.05, by0 + 0.50, fill="#fff")
    mobile(t, cxc + 0.05, by0 + 0.15, bx1 - 0.10, by0 + 0.50, fill="#fff")
    t.line(bx0, by0 + 0.75, bx1, by0 + 0.75, stroke=g, stroke_width=0.8)
    t.text(cxc, by0 + 1.35, "letto matrimoniale", size=9, fill=g)
    t.text(cxc, by0 + 1.55, "160×200", size=9, fill=g)
    mobile(t, bx1, by0, bx1 + 0.45, by0 + 0.40, "com.", size=8)
    mobile(t, bx0 - 0.45, by0, bx0, by0 + 0.40, "com.", size=8, dash="4 3", col="#e65100", fill="#fff3e0")
    # --- CUCINA: blocco su parete ingressi
    ky0 = IN_Y1 - 0.60
    mobile(t, 4.20, ky0, 4.80, IN_Y1, "frigo", size=8, fill="#f0f0f0")
    mobile(t, 4.80, ky0, 5.50, IN_Y1)
    t.rect(4.90, ky0 + 0.10, 5.40, IN_Y1 - 0.08, fill="#fff", stroke=g, stroke_width=1, rx=5)
    t.text(5.15, ky0 + 0.30, "lavello", size=8, fill=g)
    mobile(t, 5.50, ky0, IN_X1, IN_Y1)
    for dx, dy in ((0.17, 0.17), (0.45, 0.17), (0.17, 0.43), (0.45, 0.43)):
        X, Y = P(5.50 + dx, ky0 + dy)
        t.w(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="{0.09*S:.1f}" fill="#fff" stroke="{g}"/>')
    # tavolo a parete + 2 sedie
    mobile(t, 5.45, 8.15, IN_X1, 9.05, "tavolo", size=8, rot=-90)
    mobile(t, 5.00, 8.25, 5.40, 8.62)
    mobile(t, 5.00, 8.58 + 0.02, 5.40, 8.97)
    # --- CORRIDOIO
    mobile(t, IN_X0, 5.45, 0.90, 7.60, fill="#f4efe6")
    t.line(0.42, 5.50, 0.42, 7.55, stroke=g, stroke_width=0.8, stroke_dasharray="6 3")
    t.text(0.68, 6.52, "armadio 215×60", size=9, rot=-90, fill=g)
    mobile(t, 2.25, 6.25, X_TR, 7.25, "mobile", size=8, rot=-90)
    mobile(t, IN_X0, 8.60, 0.70, 9.85, "scarpiera", size=8, rot=-90)
    t.w("</g>")


# ------------------------------------------------------------------ tavola
def genera(con_arredo, nome_file):
    t = Tav()
    w = t.w
    titolo = "PIANTA ABITAZIONE — ARREDO" if con_arredo else "PIANTA ABITAZIONE — BASE PER ARREDO"
    w(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W_TAV*0.25:.0f}mm" height="{H_TAV*0.25:.0f}mm" viewBox="0 0 {W_TAV} {H_TAV}" font-family="Helvetica, Arial, sans-serif">
<title>{titolo} - Via Isonzo - scala 1:50</title>
<defs>
  <pattern id="g50" width="{S/2}" height="{S/2}" patternUnits="userSpaceOnUse" x="{OX + ME*S}" y="{OY + ME*S}">
    <path d="M {S/2} 0 L 0 0 0 {S/2}" fill="none" stroke="#b9c7d6" stroke-width="0.4"/>
  </pattern>
  <pattern id="g100" width="{S}" height="{S}" patternUnits="userSpaceOnUse" x="{OX + ME*S}" y="{OY + ME*S}">
    <rect width="{S}" height="{S}" fill="url(#g50)"/>
    <path d="M {S} 0 L 0 0 0 {S}" fill="none" stroke="#9fb3c8" stroke-width="0.8"/>
  </pattern>
</defs>
<style>
  .dim line {{ stroke:{C_DIM}; stroke-width:0.7; }}
  .dim .ext {{ stroke-width:0.45; }}
  .dim .tick {{ stroke-width:1.3; }}
  .dim text {{ fill:{C_DIM}; font-weight:600; }}
  .lbl {{ font-weight:700; letter-spacing:1.2px; fill:#1d1d1d; }}
</style>
<rect width="{W_TAV}" height="{H_TAV}" fill="#ffffff"/>
<rect x="20" y="20" width="{W_TAV-40}" height="{H_TAV-40}" fill="none" stroke="#111" stroke-width="1.5"/>
<text x="{OX-150}" y="62" font-size="26" class="lbl">{titolo}</text>
<text x="{OX-150}" y="88" font-size="13" fill="#555">Via Isonzo · sagoma 10,35 × 6,45 m (Allegato 1) · distribuzione da schizzo · misure in metri · stampa 100% = scala 1:50 (A3)</text>''')

    # muri: sagoma piena, poi stanze
    t.rect(0, 0, LX, LY, fill=C_WALL)
    w('<g id="stanze">')
    for nome, (x0, y0, x1, y1, col) in STANZE.items():
        t.rect(x0, y0, x1, y1, fill=col)
        t.rect(x0, y0, x1, y1, fill="url(#g100)", opacity="0.55" if con_arredo else "1")
    w('</g>')

    # serramenti
    w('<g id="finestre">')
    for fid, _, lato, y0, y1, ante in FINESTRE:
        finestra(t, fid, lato, y0, y1, ante)
    w('</g><g id="porte">')
    # P1 ingresso principale (parete in basso)
    porta_battente(t, "P1", "h", 1.20, 2.20, 1, -1, ME, IN_Y1)
    # P2 ingresso secondario cucina
    porta_battente(t, "P2", "h", 3.10, 4.00, 0, -1, ME, IN_Y1)
    # P3 bagno scorrevole
    porta_scorrevole(t, 1.85, 2.65, Y_BAGNO, MI, -1)
    # P4 salotto, P5 camera, P6 cucina (tramezzo corridoio)
    porta_battente(t, "P4", "v", 3.65, 4.45, 1, +1, MI, X_TR)
    porta_battente(t, "P5", "v", 4.80, 5.60, 0, +1, MI, X_TR)
    porta_battente(t, "P6", "v", 8.05, 8.85, 0, +1, MI, X_TR)
    w('</g>')

    if con_arredo:
        arredo(t)

    # tag porte
    tag_porta(t, "P1", 1.70, LY + 0.45, "100")
    tag_porta(t, "P2", 3.55, LY + 0.45, "90")
    tag_porta(t, "P3", 2.25, Y_BAGNO + 0.40, "80")
    tag_porta(t, "P4", X_TR - 0.35, 4.05, "80")
    tag_porta(t, "P5", X_TR - 0.35, 5.20, "80")
    tag_porta(t, "P6", X_TR - 0.35, 8.45, "80")

    # quadro elettrico
    X, Y = P(IN_X0, 9.20)
    w(f'<g><rect x="{X:.1f}" y="{Y-12:.1f}" width="10" height="24" fill="#ffca28" stroke="#111" stroke-width="1.2"/>'
      f'<path d="M {X+6:.1f} {Y-8:.1f} L {X+2:.1f} {Y+1:.1f} L {X+6:.1f} {Y+1:.1f} L {X+3:.1f} {Y+9:.1f}" fill="none" stroke="#111" stroke-width="1.2"/></g>')
    t.text(-0.55, 9.20, "QE", size=12, font_weight="700", fill="#111")

    # etichette stanze
    def etichetta(nome, x, y, rot=0):
        x0, y0, x1, y1, _ = STANZE[nome]
        a = (x1 - x0) * (y1 - y0)
        X, Y = P(x, y)
        wbox = max(len(nome) * 9 + 20, 150)
        w(f'<g transform="rotate({rot} {X:.1f} {Y:.1f})">'
          f'<rect x="{X-wbox/2:.1f}" y="{Y-22:.1f}" width="{wbox}" height="44" rx="4" fill="#fff" fill-opacity="0.9" stroke="#333" stroke-width="0.7"/>'
          f'<text x="{X:.1f}" y="{Y-8:.1f}" font-size="13" text-anchor="middle" dominant-baseline="middle" class="lbl">{nome}</text>'
          f'<text x="{X:.1f}" y="{Y+10:.1f}" font-size="11" fill="#444" text-anchor="middle" dominant-baseline="middle">{fmt(a)} m² · {fmt(x1-x0)}×{fmt(y1-y0)}</text></g>')
    cxs = (X_TR + MI + IN_X1) / 2
    if con_arredo:
        etichetta("BAGNO", 1.40, 1.75)
        etichetta("SALOTTO", cxs + 0.25, 3.85)
        etichetta("CAMERA DA LETTO", cxs, 7.25)
        etichetta("CUCINA", 4.20, 8.55)
        etichetta("CORRIDOIO", 1.55, 6.40, rot=-90)
    else:
        for nome, (x0, y0, x1, y1, _) in STANZE.items():
            etichetta(nome, (x0 + x1) / 2, (y0 + y1) / 2, rot=-90 if nome == "CORRIDOIO" else 0)

    # quote
    t.quota((0, 0), (LX, 0), fmt(LX), off=1.15, lato=-1, size=13)
    t.catena("x", [0, IN_X0, X_TR, X_TR + MI, IN_X1, LX], 0, off=0.75, lato=-1)
    t.quota((0, 0), (0, LY), fmt(LY), off=1.55, lato=1, size=13)
    t.catena("y", [0, IN_Y0, Y_BAGNO, Y_BAGNO + MI, IN_Y1, LY], 0, off=1.1, lato=1)
    t.catena("y", [0, IN_Y0, Y_SAL, Y_SAL + MI, Y_CAM, Y_CAM + MI, IN_Y1, LY], LX, off=1.15, lato=-1)

    # lati / orientamento
    t.text(LX / 2, -1.85, "LATO EST · in aderenza al confine", size=11, fill="#777", letter_spacing="1")
    t.text(LX / 2, LY + 1.05, "LATO OVEST · ingressi (verso giardino/garage)", size=11, fill="#777", letter_spacing="1")
    t.text(-2.25, LY / 2, "LATO NORD", size=11, fill="#777", rot=-90, letter_spacing="1")
    t.text(LX + 1.95, LY / 2, "LATO SUD · verso Via Isonzo", size=11, fill="#777", rot=90, letter_spacing="1")

    # ------------------------------------------------ colonna destra
    y = 150
    # nord: il lato sinistro della pianta è il Nord
    w(f'''<g transform="translate({PX+60},{y+50})">
  <circle r="34" fill="none" stroke="#111" stroke-width="1.4"/>
  <line x1="-44" y1="0" x2="44" y2="0" stroke="#111" stroke-width="0.7"/>
  <line x1="0" y1="-44" x2="0" y2="44" stroke="#111" stroke-width="0.7"/>
  <g transform="rotate(-90)"><polygon points="0,-36 10,10 0,3" fill="#111"/><polygon points="0,-36 -10,10 0,3" fill="#fff" stroke="#111"/></g>
  <text x="-58" y="5" font-size="16" class="lbl" text-anchor="middle">N</text>
</g>
<text x="{PX+120}" y="{y+38}" font-size="11" fill="#555">Nord a sinistra: pianta ruotata</text>
<text x="{PX+120}" y="{y+54}" font-size="11" fill="#555">come lo schizzo (ingressi in basso)</text>''')
    # scala grafica
    y = 280
    w(f'<g transform="translate({PX},{y})"><text y="-12" font-size="12" class="lbl">SCALA GRAFICA</text>')
    for i in range(4):
        w(f'<rect x="{i*S}" y="0" width="{S}" height="8" fill="{"#111" if i%2==0 else "#fff"}" stroke="#111"/>')
    for i in range(5):
        w(f'<text x="{i*S}" y="24" font-size="11" text-anchor="middle">{i}</text>')
    w(f'<text x="{4*S+12}" y="24" font-size="11">m</text></g>')

    # abaco serramenti
    y = 350
    w(f'<g transform="translate({PX},{y})"><text y="0" font-size="12" class="lbl">ABACO SERRAMENTI</text>')
    righe = [("F1", "Bagno", "90", "1", "lato N, a 0,80 dall'angolo"),
             ("F2", "Corridoio", "100", "1", "lato N, a 0,80 dal bagno"),
             ("F3", "Salotto", "120", "2", "lato S, a 1,30 dall'angolo"),
             ("F4", "Camera", "100", "2", "lato S, a 1,15 dal salotto"),
             ("F5", "Cucina", "90", "1", "lato S, a 0,30 dalla camera"),
             ("P1", "Ingresso princ.", "100", "1", "battente, apre verso interno"),
             ("P2", "Ingresso cucina", "90", "1", "battente, apre verso interno"),
             ("P3", "Bagno", "80", "1", "scorrevole a scomparsa"),
             ("P4", "Salotto", "80", "1", "battente"),
             ("P5", "Camera", "80", "1", "battente"),
             ("P6", "Cucina", "80", "1", "battente")]
    w(f'<text x="0" y="22" font-size="10" fill="#777">ID</text><text x="34" y="22" font-size="10" fill="#777">LOCALE</text>'
      f'<text x="140" y="22" font-size="10" fill="#777">L cm</text><text x="178" y="22" font-size="10" fill="#777">ANTE</text>'
      f'<text x="214" y="22" font-size="10" fill="#777">POSIZIONE / TIPO</text>')
    for i, (rid, loc, lg, an, pos) in enumerate(righe):
        yy = 42 + i * 19
        col = C_WIN if rid.startswith("F") else C_DOOR
        w(f'<text x="0" y="{yy}" font-size="11" font-weight="700" fill="{col}">{rid}</text>'
          f'<text x="34" y="{yy}" font-size="11">{loc}</text><text x="140" y="{yy}" font-size="11">{lg}</text>'
          f'<text x="190" y="{yy}" font-size="11">{an}</text><text x="214" y="{yy}" font-size="10" fill="#444">{pos}</text>'
          f'<line x1="0" y1="{yy+6}" x2="440" y2="{yy+6}" stroke="#e2e2e2"/>')
    w('</g>')

    # superfici
    y = 610
    w(f'<g transform="translate({PX},{y})"><text y="0" font-size="12" class="lbl">SUPERFICI NETTE</text>')
    tot = 0
    for i, (nome, (x0, y0, x1, y1, col)) in enumerate(STANZE.items()):
        a = (x1 - x0) * (y1 - y0); tot += a
        yy = 22 + i * 19
        w(f'<rect x="0" y="{yy-10}" width="14" height="12" fill="{col}" stroke="#999"/>'
          f'<text x="22" y="{yy}" font-size="11">{nome.title()}</text>'
          f'<text x="230" y="{yy}" font-size="11" text-anchor="end">{fmt(x1-x0)} × {fmt(y1-y0)}</text>'
          f'<text x="320" y="{yy}" font-size="11" text-anchor="end" font-weight="600">{fmt(a)} m²</text>')
    yy = 22 + len(STANZE) * 19 + 4
    w(f'<line x1="0" y1="{yy-12}" x2="320" y2="{yy-12}" stroke="#333"/>'
      f'<text x="22" y="{yy+2}" font-size="11" font-weight="700">Totale netto</text>'
      f'<text x="320" y="{yy+2}" font-size="11" text-anchor="end" font-weight="700">{fmt(tot)} m²</text>'
      f'<text x="22" y="{yy+20}" font-size="11" fill="#555">Superficie lorda</text>'
      f'<text x="320" y="{yy+20}" font-size="11" text-anchor="end" fill="#555">{fmt(LX*LY)} m²</text></g>')

    # legenda
    y = 800
    leg = [(f'<rect width="26" height="12" fill="{C_WALL}"/>', "Muro esterno 30 cm / tramezzo 10 cm"),
           (f'<rect width="26" height="12" fill="#dbeafb" stroke="{C_WIN}" stroke-width="2"/>', "Finestra (tratteggio = apertura anta)"),
           (f'<path d="M 0 12 L 0 -8 M 0 -8 A 20 20 0 0 1 20 12" fill="none" stroke="{C_DOOR}" stroke-width="1.5"/>', "Porta a battente"),
           (f'<rect y="4" width="26" height="4" fill="{C_DOOR}"/>', "Porta scorrevole a scomparsa"),
           (f'<rect width="26" height="12" fill="url(#g100)" stroke="#9fb3c8"/>', "Griglia 1 m / 50 cm"),
           ('<rect width="10" height="14" fill="#ffca28" stroke="#111"/>', "Quadro elettrico")]
    if con_arredo:
        leg.append(('<rect width="26" height="12" fill="#fff3e0" stroke="#e65100" stroke-dasharray="4 3"/>', "Elemento in conflitto (vedi note)"))
    w(f'<g transform="translate({PX},{y})"><text y="0" font-size="12" class="lbl">LEGENDA</text>')
    for i, (sym, txt) in enumerate(leg):
        w(f'<g transform="translate(0,{18 + i*24})">{sym}<text x="38" y="10" font-size="11">{txt}</text></g>')
    w('</g>')

    # note
    y = 800 + 18 + len(leg) * 24 + 22
    note = ["NOTE",
            "Sagoma esterna da Allegato 1; tramezzi e serramenti",
            "ricavati dallo schizzo in proporzione: verificare in",
            "loco prima di ordinare mobili su misura.",
            "Spessori muri 30/10 cm e larghezze porte = ipotesi.",
            "Griglia allineata al filo interno dei muri."]
    if con_arredo:
        note += ["Arredo indicativo (dimensioni standard).",
                 "Camera: con P5 in questa posizione l'anta urta",
                 "il comodino lato porta → valutare porta scorrevole",
                 "o spostare P5 verso la cucina."]
    w(f'<g transform="translate({PX},{y})">')
    for i, s in enumerate(note):
        attr = 'class="lbl" font-size="12"' if i == 0 else 'font-size="11" fill="#555"'
        w(f'<text y="{i*16}" {attr}>{s}</text>')
    w('</g></svg>')

    with open(nome_file, "w", encoding="utf-8") as f:
        f.write("\n".join(t.o))


if __name__ == "__main__":
    genera(True, "pianta_abitazione_arredata.svg")
    genera(False, "pianta_abitazione_base.svg")
    for n, (x0, y0, x1, y1, _) in STANZE.items():
        print(f"{n:16s} {x1-x0:.2f} x {y1-y0:.2f} = {(x1-x0)*(y1-y0):.2f} m2")
