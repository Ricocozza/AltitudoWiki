"""Genera la planimetria digitale (SVG) del lotto di Via Isonzo
a partire dal "Tipo planimetrico - Allegato 1" (scala 1:200).

Tutte le misure sono in metri. Origine = spigolo SW del lotto su Via Isonzo,
asse x verso Est, asse y verso Nord.
"""
import math

# ---------------------------------------------------------------- dati sorgente
LATO_STRADA = 13.65   # fronte su Via Isonzo
LATO_NORD   = 15.50   # confine nord
LATO_OVEST  = 27.00   # confine ovest
LATO_EST    = 26.00   # confine est
GAR_W, GAR_L = 2.70, 5.65
CASA_W, CASA_D = 10.35, 6.45
QUOTA_NORD_GARAGE = 5.00
QUOTA_GARAGE_CASA = 5.70
MURO = 0.30           # spessore muri perimetrali (IPOTESI, non nel documento)

# ---------------------------------------------------------------- geometria lotto
A = (0.0, 0.0)
B = (LATO_STRADA, 0.0)
C = (LATO_STRADA, LATO_EST)
# D: intersezione cerchio (A, 27.00) e cerchio (C, 15.50), soluzione a ovest
def intersect(p0, r0, p1, r1):
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    d = math.hypot(dx, dy)
    a = (r0**2 - r1**2 + d**2) / (2 * d)
    h = math.sqrt(r0**2 - a**2)
    xm, ym = p0[0] + a * dx / d, p0[1] + a * dy / d
    s1 = (xm + h * dy / d, ym - h * dx / d)
    s2 = (xm - h * dy / d, ym + h * dx / d)
    return min(s1, s2, key=lambda p: p[0])
D = intersect(A, LATO_OVEST, C, LATO_NORD)

def y_nord(x):  # quota del confine nord all'ascissa x
    t = (x - D[0]) / (C[0] - D[0])
    return D[1] + t * (C[1] - D[1])

def x_ovest(y):  # ascissa del confine ovest alla quota y
    return A[0] + (D[0] - A[0]) * y / D[1]

# catena di quote verticale (come nel disegno) all'ascissa del filo ovest casa
X_CATENA = LATO_STRADA - CASA_W
Y_TOP = y_nord(X_CATENA)
GAR_TOP = Y_TOP - QUOTA_NORD_GARAGE
GAR_BOT = GAR_TOP - GAR_L
CASA_TOP = GAR_BOT - QUOTA_GARAGE_CASA
CASA_BOT = CASA_TOP - CASA_D
ARRETRAMENTO = CASA_BOT  # distanza casa - strada (derivata)

# garage: addossato al confine ovest, parallelo ad esso
u = ((D[0] - A[0]) / LATO_OVEST, (D[1] - A[1]) / LATO_OVEST)  # verso nord lungo confine
n = (u[1], -u[0])                                              # verso interno (est)
s0 = GAR_BOT / u[1]
G0 = (A[0] + u[0] * s0, A[1] + u[1] * s0)
GAR = [G0,
       (G0[0] + n[0] * GAR_W, G0[1] + n[1] * GAR_W),
       (G0[0] + n[0] * GAR_W + u[0] * GAR_L, G0[1] + n[1] * GAR_W + u[1] * GAR_L),
       (G0[0] + u[0] * GAR_L, G0[1] + u[1] * GAR_L)]

# ---------------------------------------------------------------- trasformazione SVG
S = 40.0                      # unità SVG per metro
X_MIN, Y_MAX = D[0], D[1]
OX, OY = 150.0, 170.0         # margine per quote
W_TAV, H_TAV = 1400, 1440

def P(x, y):
    return (OX + (x - X_MIN) * S, OY + (Y_MAX - y) * S)

def pts(poly):
    return " ".join(f"{P(*p)[0]:.1f},{P(*p)[1]:.1f}" for p in poly)

def fmt(m):  # 5.65 -> "5,65"
    return f"{m:.2f}".replace(".", ",")

out = []
w = out.append

# ---------------------------------------------------------------- quote
def quota(p1, p2, testo, off=0.0, lato=1, cls="dim"):
    """Quota allineata tra p1 e p2 (metri), spostata di off metri sulla normale."""
    (x1, y1), (x2, y2) = P(*p1), P(*p2)
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    nx, ny = -uy * lato, ux * lato
    o = off * S
    a = (x1 + nx * o, y1 + ny * o)
    b = (x2 + nx * o, y2 + ny * o)
    g = [f'<g class="{cls}">']
    # linee di richiamo
    g.append(f'<line x1="{x1 + nx*4:.1f}" y1="{y1 + ny*4:.1f}" x2="{a[0] + nx*6:.1f}" y2="{a[1] + ny*6:.1f}" class="ext"/>')
    g.append(f'<line x1="{x2 + nx*4:.1f}" y1="{y2 + ny*4:.1f}" x2="{b[0] + nx*6:.1f}" y2="{b[1] + ny*6:.1f}" class="ext"/>')
    g.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}"/>')
    # tick architettonici a 45°
    for (cx, cy) in (a, b):
        tx, ty = (ux + nx) * 5, (uy + ny) * 5
        g.append(f'<line x1="{cx-tx:.1f}" y1="{cy-ty:.1f}" x2="{cx+tx:.1f}" y2="{cy+ty:.1f}" class="tick"/>')
    mx, my = (a[0] + b[0]) / 2 + nx * 9, (a[1] + b[1]) / 2 + ny * 9
    ang = math.degrees(math.atan2(dy, dx))
    if ang > 90: ang -= 180
    if ang <= -90: ang += 180
    g.append(f'<text x="{mx:.1f}" y="{my:.1f}" transform="rotate({ang:.2f} {mx:.1f} {my:.1f})" '
             f'text-anchor="middle" dominant-baseline="middle">{testo}</text>')
    g.append("</g>")
    w("\n".join(g))

# ---------------------------------------------------------------- documento
w(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W_TAV*0.125:.0f}mm" height="{H_TAV*0.125:.0f}mm" viewBox="0 0 {W_TAV} {H_TAV}" font-family="Helvetica, Arial, sans-serif">
<title>Planimetria lotto Via Isonzo - scala 1:200</title>
<defs>
  <pattern id="grid50" width="{S/2}" height="{S/2}" patternUnits="userSpaceOnUse">
    <path d="M {S/2} 0 L 0 0 0 {S/2}" fill="none" stroke="#c9d6e3" stroke-width="0.5"/>
  </pattern>
  <pattern id="grid100" width="{S}" height="{S}" patternUnits="userSpaceOnUse">
    <rect width="{S}" height="{S}" fill="url(#grid50)"/>
    <path d="M {S} 0 L 0 0 0 {S}" fill="none" stroke="#9fb3c8" stroke-width="0.9"/>
  </pattern>
  <pattern id="hatchGarage" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
    <line x1="0" y1="0" x2="0" y2="8" stroke="#8a8a8a" stroke-width="1"/>
  </pattern>
  <pattern id="lawn" width="14" height="14" patternUnits="userSpaceOnUse">
    <circle cx="3" cy="3" r="0.9" fill="#9cc49a"/><circle cx="10" cy="10" r="0.9" fill="#9cc49a"/>
  </pattern>
</defs>
<style>
  .dim line {{ stroke:#2b5d8a; stroke-width:0.8; }}
  .dim .ext {{ stroke-width:0.5; }}
  .dim .tick {{ stroke-width:1.4; }}
  .dim text {{ fill:#2b5d8a; font-size:13px; font-weight:600; }}
  .lbl {{ fill:#222; font-weight:700; letter-spacing:1.5px; }}
  .note {{ fill:#444; font-size:11px; }}
</style>
<rect width="{W_TAV}" height="{H_TAV}" fill="#ffffff"/>
''')

# titolo
w(f'<text x="{OX}" y="60" font-size="26" class="lbl">PLANIMETRIA LOTTO — VIA ISONZO</text>')
w(f'<text x="{OX}" y="86" font-size="13" fill="#555">Ridisegno digitale del “Tipo planimetrico – Allegato 1” · misure in metri · Nord in alto</text>')

# lotto: giardino
lotto = [A, B, C, D]
w(f'<polygon points="{pts(lotto)}" fill="#f3f8f1"/>')
w(f'<polygon points="{pts(lotto)}" fill="url(#lawn)"/>')

# casa: griglia 1 m / 50 cm per arredo
casa = [(LATO_STRADA - CASA_W, CASA_BOT), (LATO_STRADA, CASA_BOT), (LATO_STRADA, CASA_TOP), (LATO_STRADA - CASA_W, CASA_TOP)]
interno = [(casa[0][0] + MURO, CASA_BOT + MURO), (LATO_STRADA - MURO, CASA_BOT + MURO),
           (LATO_STRADA - MURO, CASA_TOP - MURO), (casa[0][0] + MURO, CASA_TOP - MURO)]
x0, y0 = P(*interno[3])
x1, y1 = P(*interno[1])
w(f'<g><rect x="{x0:.1f}" y="{y0:.1f}" width="{x1-x0:.1f}" height="{y1-y0:.1f}" fill="#ffffff"/>')
w(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1-x0:.1f}" height="{y1-y0:.1f}" fill="url(#grid100)"/></g>')
# muri perimetrali (poché)
w(f'<path d="M {pts(casa)} Z M {pts(interno[::-1])} Z" fill="#2f2f2f" fill-rule="evenodd"/>')

# garage
w(f'<polygon points="{pts(GAR)}" fill="url(#hatchGarage)" stroke="#2f2f2f" stroke-width="3"/>')
gc = P(sum(p[0] for p in GAR) / 4, sum(p[1] for p in GAR) / 4)
ang_g = -math.degrees(math.atan2(u[0], u[1]))
w(f'<g transform="rotate({-90 + ang_g:.2f} {gc[0]:.1f} {gc[1]:.1f})">'
  f'<rect x="{gc[0]-52:.1f}" y="{gc[1]-12:.1f}" width="104" height="24" fill="#fff" stroke="#2f2f2f" stroke-width="0.8"/>'
  f'<text x="{gc[0]:.1f}" y="{gc[1]+5:.1f}" text-anchor="middle" font-size="14" class="lbl">GARAGE</text></g>')

# confine del lotto
w(f'<polygon points="{pts(lotto)}" fill="none" stroke="#111" stroke-width="3.2" stroke-linejoin="miter"/>')

# recinzione su strada con pilastri (posizioni indicative dal disegno)
for xp in (0.0, 3.0, 12.75, LATO_STRADA):
    px, py = P(xp, 0)
    w(f'<rect x="{px-5:.1f}" y="{py-5:.1f}" width="10" height="10" fill="#fff" stroke="#111" stroke-width="1.5"/>')

# etichetta casa + superfici
cx, cy = P(LATO_STRADA - CASA_W / 2, (CASA_TOP + CASA_BOT) / 2)
lorda = CASA_W * CASA_D
netta = (CASA_W - 2 * MURO) * (CASA_D - 2 * MURO)
w(f'<rect x="{cx-110:.1f}" y="{cy-34:.1f}" width="220" height="62" rx="3" fill="#fff" fill-opacity="0.92" stroke="#2f2f2f" stroke-width="0.8"/>')
w(f'<text x="{cx:.1f}" y="{cy-10:.1f}" text-anchor="middle" font-size="18" class="lbl">ABITAZIONE</text>')
w(f'<text x="{cx:.1f}" y="{cy+8:.1f}" text-anchor="middle" class="note">Sup. lorda {fmt(lorda)} m²</text>')
w(f'<text x="{cx:.1f}" y="{cy+22:.1f}" text-anchor="middle" class="note">Sup. interna ≈ {fmt(netta)} m² (muri 30 cm)</text>')

# strada
sx0, sy = P(D[0] - 0.5, 0)
sx1, _ = P(LATO_STRADA + 2.2, 0)
w(f'<rect x="{sx0:.1f}" y="{sy+68:.1f}" width="{sx1-sx0:.1f}" height="60" fill="#e6e6e6"/>')
w(f'<line x1="{sx0:.1f}" y1="{sy+98:.1f}" x2="{sx1:.1f}" y2="{sy+98:.1f}" stroke="#fff" stroke-width="2" stroke-dasharray="18 12"/>')
w(f'<text x="{(sx0+sx1)/2:.1f}" y="{sy+104:.1f}" text-anchor="middle" font-size="17" class="lbl" fill="#333">VIA ISONZO</text>')

# ---------------------------------------------------------------- quote
quota(D, C, fmt(LATO_NORD), off=1.0, lato=-1)
quota(A, B, fmt(LATO_STRADA), off=0.9, lato=1)
quota(A, D, fmt(LATO_OVEST), off=1.6, lato=-1)
quota(B, C, fmt(LATO_EST), off=2.6, lato=1)
# casa
quota(casa[3], casa[2], fmt(CASA_W), off=0.7, lato=-1)
# garage
quota(GAR[0], GAR[1], fmt(GAR_W), off=0.7, lato=1)
# catena verticale
xc = X_CATENA - 0.55
quota((xc, Y_TOP), (xc, GAR_TOP), fmt(QUOTA_NORD_GARAGE), lato=1)
quota((xc, GAR_TOP), (xc, GAR_BOT), fmt(GAR_L), lato=1)
quota((xc, GAR_BOT), (xc, CASA_TOP), fmt(QUOTA_GARAGE_CASA), lato=1)
quota((xc, CASA_TOP), (xc, CASA_BOT), fmt(CASA_D), lato=1)
quota((xc, CASA_BOT), (xc, 0), "≈" + fmt(ARRETRAMENTO), lato=1, cls="dim derived")

# ---------------------------------------------------------------- nord
nx_, ny_ = W_TAV - 150, 330
w(f'''<g transform="translate({nx_},{ny_})">
  <circle r="42" fill="none" stroke="#111" stroke-width="1.5"/>
  <line x1="-52" y1="0" x2="52" y2="0" stroke="#111" stroke-width="0.8"/>
  <line x1="0" y1="52" x2="0" y2="-52" stroke="#111" stroke-width="0.8"/>
  <polygon points="0,-44 12,12 0,4" fill="#111"/>
  <polygon points="0,-44 -12,12 0,4" fill="#fff" stroke="#111" stroke-width="1"/>
  <text y="-60" text-anchor="middle" font-size="18" class="lbl">N</text>
</g>''')

# ---------------------------------------------------------------- scala grafica
bx, by = W_TAV - 360, 470
w(f'<g transform="translate({bx},{by})"><text y="-12" font-size="12" class="lbl">SCALA GRAFICA</text>')
for i in range(5):
    w(f'<rect x="{i*S:.1f}" y="0" width="{S:.1f}" height="8" fill="{"#111" if i % 2 == 0 else "#fff"}" stroke="#111" stroke-width="1"/>')
for i in (0, 1, 2, 3, 4, 5):
    w(f'<text x="{i*S:.1f}" y="24" text-anchor="middle" font-size="11">{i}</text>')
w(f'<text x="{5*S+10:.1f}" y="24" font-size="11">m</text></g>')

# ---------------------------------------------------------------- legenda / cartiglio
lx, ly = W_TAV - 360, 560
leg = [
    ('<rect width="26" height="14" fill="#2f2f2f"/>', "Muratura perimetrale (30 cm, ipotesi)"),
    ('<rect width="26" height="14" fill="url(#hatchGarage)" stroke="#2f2f2f" stroke-width="1.5"/>', "Garage (2,70 × 5,65)"),
    ('<rect width="26" height="14" fill="url(#grid100)" stroke="#9fb3c8"/>', "Griglia arredo: 1 m / 50 cm"),
    ('<rect width="26" height="14" fill="url(#lawn)" stroke="#9cc49a"/>', "Area scoperta / giardino"),
    ('<line x1="0" y1="7" x2="26" y2="7" stroke="#111" stroke-width="3"/>', "Confine di proprietà"),
    ('<rect x="8" y="2" width="10" height="10" fill="#fff" stroke="#111" stroke-width="1.5"/>', "Pilastro recinzione (indicativo)"),
]
w(f'<g transform="translate({lx},{ly})"><text y="0" font-size="12" class="lbl">LEGENDA</text>')
for i, (sym, txt) in enumerate(leg):
    yy = 16 + i * 26
    w(f'<g transform="translate(0,{yy})">{sym}<text x="36" y="11" font-size="12">{txt}</text></g>')
w('</g>')

# dati riepilogo
area_lotto = 0.5 * abs(sum(lotto[i][0] * lotto[(i+1) % 4][1] - lotto[(i+1) % 4][0] * lotto[i][1] for i in range(4)))
rx, ry = W_TAV - 360, 760
dati = [
    ("Lotto", f"≈ {fmt(area_lotto)} m²"),
    ("Abitazione (lorda)", f"{fmt(CASA_W)} × {fmt(CASA_D)} = {fmt(lorda)} m²"),
    ("Abitazione (interna)", f"≈ {fmt(netta)} m²"),
    ("Garage", f"{fmt(GAR_W)} × {fmt(GAR_L)} = {fmt(GAR_W*GAR_L)} m²"),
    ("Distanza casa–strada", f"≈ {fmt(ARRETRAMENTO)} m (derivata)"),
]
w(f'<g transform="translate({rx},{ry})"><text y="0" font-size="12" class="lbl">DATI DIMENSIONALI</text>')
for i, (k, v) in enumerate(dati):
    yy = 22 + i * 20
    w(f'<text x="0" y="{yy}" font-size="12" fill="#555">{k}</text><text x="310" y="{yy}" font-size="12" text-anchor="end" font-weight="600">{v}</text>')
    w(f'<line x1="0" y1="{yy+6}" x2="310" y2="{yy+6}" stroke="#ddd" stroke-width="0.8"/>')
w('</g>')

nota = [
    "NOTE",
    "Quote in metri, come da Allegato 1 (scala 1:200).",
    "Il documento originale non riporta finestre, porte",
    "né tramezzi interni: la sagoma dell'abitazione è",
    "lasciata libera con griglia per il posizionamento",
    "dell'arredo. Spessore muri 30 cm = ipotesi.",
    "Quote con ≈ ricavate per differenza.",
    "Stampa al 100% → scala 1:200.",
]
w(f'<g transform="translate({rx},{ry+140})">')
for i, t in enumerate(nota):
    attr = 'class="lbl"' if i == 0 else 'fill="#555"'
    w(f'<text x="0" y="{i*17}" font-size="{12 if i == 0 else 11}" {attr}>{t}</text>')
w('</g>')

# cornice tavola
w(f'<rect x="20" y="20" width="{W_TAV-40}" height="{H_TAV-40}" fill="none" stroke="#111" stroke-width="1.5"/>')
w('</svg>')

with open("planimetria_via_isonzo.svg", "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print(f"D = ({D[0]:.3f}, {D[1]:.3f})  arretramento casa = {ARRETRAMENTO:.2f} m  lotto = {area_lotto:.1f} m²")
print(f"estensione disegno: x max {P(LATO_STRADA,0)[0]:.0f}, y max {P(0,0)[1]:.0f}")
