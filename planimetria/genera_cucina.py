"""Cucina: pianta di dettaglio in scala 1:25 (160 px = 1 m) ricavata dallo schizzo.

Orientamento = come lo schizzo (lato lungo verticale):
  alto    parete esterna con finestra e calorifero (Sud)
  destra  parete esterna con ingresso secondario P2 e blocco cucina (Ovest)
  basso   tramezzo con la porta P6 verso il corridoio (Nord)
  sinistra tramezzo verso la camera da letto (Est)

Coordinate in cm: origine = angolo in alto a sinistra dell'interno del locale,
u verso destra (0..154), v verso il basso (0..400).
Gli elementi non quotati nello schizzo sono segnati con un numero arancione
e riepilogati nella colonna "punti da confermare".

Genera: cucina_dettaglio_arredata.svg e cucina_template_vuoto.svg
"""
import genera_pianta_abitazione as gp
import genera_libreria_arredi as lib
import genera_layout as gl

gp.S = 160.0
S = gp.S
GP_OX, GP_OY = 250.0, 270.0

W_CM, L_CM = 154, 400                      # interno locale
T_TOP, T_DX, T_SX, T_BOT = 30, 30, 11, 11  # spessori (30 = ipotesi, 11 dallo schizzo)
RUN_D = 62                                 # profondità blocco cucina
RUN_U0 = W_CM - RUN_D                      # fronte blocco = 92
Z_CUCINA = 250                             # fine zona cucina / inizio ingresso

C_WALL, C_WIN, C_DOOR, C_OK = gp.C_WALL, gp.C_WIN, gp.C_DOOR, gl.C_OK
C_WARN, C_SOCK, C_RAD = '#d98200', '#1a56c4', '#d9534f'


def m(cm):
    return cm / 100.0


def P(u, v):
    """cm interni -> pixel"""
    return gp.P(m(u), m(v))


# ------------------------------------------------------------------ arredi
def mob(t, voce, u, v, facing='sx'):
    """Arredo della libreria; (u,v) = angolo in alto a sinistra dell'ingombro ruotato (cm)."""
    cat, _, nome, w, d, fn, _, extra = voce
    rot = gl.FACING[facing]
    lib.ROT = rot
    body = lib.disegna(voce)
    lib.ROT = 0
    tr = {0: '', 90: f'translate({d},0) rotate(90)', 180: f'translate({w},{d}) rotate(180)',
          270: f'translate(0,{w}) rotate(270)'}[rot]
    X, Y = P(u, v)
    t.w(f'<g transform="translate({X:.1f},{Y:.1f}) scale({S/100})"><g transform="{tr}">{body}</g></g>')


def voce(nome, w, d, fn, **extra):
    return ('cucina', 'custom', nome, w, d, fn, None, extra)


# moduli lungo la parete destra, dall'alto: (v0, lunghezza, voce)
MODULI = [
    (0,   85, voce('lavello', 85, RUN_D, lib.lavello)),
    (85,  62, voce('piano cottura', 62, RUN_D, lib.piano_cottura)),
    (147, 45, voce('lavastoviglie', 45, RUN_D, lib.elettrodomestico, sigla='LS')),
    (192, 58, voce('frigorifero', 58, RUN_D, lib.elettrodomestico, sigla='FR')),
]


# ------------------------------------------------------------------ simboli
def punto(t, n, u, v):
    """Marcatore 'da confermare'."""
    X, Y = P(u, v)
    t.w(f'<g><circle cx="{X:.1f}" cy="{Y:.1f}" r="11" fill="{C_WARN}" stroke="#fff" stroke-width="1.5"/>'
        f'<text x="{X:.1f}" y="{Y+0.5:.1f}" font-size="12" font-weight="700" fill="#fff" text-anchor="middle" '
        f'dominant-baseline="middle">{n}</text></g>')


def presa(t, u, v, n, label_dx):
    """Presa 'n×' sulla faccia interna del muro a u (0 = sinistra, W = destra)."""
    X, Y = P(u, v)
    t.w(f'<g><rect x="{X-7:.1f}" y="{Y-13:.1f}" width="14" height="26" rx="2" fill="#fff" stroke="{C_SOCK}" stroke-width="1.8"/>'
        f'<circle cx="{X:.1f}" cy="{Y-6:.1f}" r="1.8" fill="{C_SOCK}"/><circle cx="{X:.1f}" cy="{Y+6:.1f}" r="1.8" fill="{C_SOCK}"/>'
        f'<text x="{X+label_dx:.1f}" y="{Y+0.5:.1f}" font-size="14" font-weight="700" fill="{C_SOCK}" '
        f'text-anchor="middle" dominant-baseline="middle">{n}×</text></g>')


def finestra_cucina(t, u0, u1):
    """Finestra a due ante sulla parete alta (spessore T_TOP), ante apribili all'interno."""
    t.rect(m(u0), m(-T_TOP), m(u1), 0, fill='#ffffff')
    t.rect(m(u0), m(-T_TOP), m(u1), 0, fill='#dbeafb', stroke=C_WIN, stroke_width=2)
    um = (u0 + u1) / 2
    t.line(m(u0), m(-T_TOP / 2 - 1.5), m(u1), m(-T_TOP / 2 - 1.5), stroke=C_WIN, stroke_width=1)
    t.line(m(u0), m(-T_TOP / 2 + 1.5), m(u1), m(-T_TOP / 2 + 1.5), stroke=C_WIN, stroke_width=1)
    t.line(m(um), m(-T_TOP), m(um), 0, stroke=C_WIN, stroke_width=1.5)
    L = (u1 - u0) / 2
    for hinge, other in ((u0, um), (u1, um)):
        tip = (m(hinge), m(L))
        t.line(m(hinge), 0, *tip, stroke=C_WIN, stroke_width=1.2, stroke_dasharray='5 3')
        t.arc((m(hinge), 0), tip, (m(other), 0), m(L), stroke=C_WIN, stroke_width=0.9, stroke_dasharray='5 3')


# ------------------------------------------------------------------ tavola
def genera(arredata, nome_file):
    gp.OX, gp.OY = GP_OX, GP_OY
    t = gp.Tav()
    w = t.w
    W = 1400 if arredata else 800
    H = 1200 if arredata else 1250
    gp.OX = GP_OX if arredata else 240.0
    gp.OY = 330.0 if arredata else 290.0
    ox, oy = gp.OX, gp.OY
    c_grid = '#c3cfdb'

    titolo = 'CUCINA — PIANTA DI DETTAGLIO' if arredata else 'CUCINA — TEMPLATE VUOTO'
    w(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W*0.25:.0f}mm" height="{H*0.25:.0f}mm" viewBox="0 0 {W} {H}" font-family="Helvetica, Arial, sans-serif">
<title>{titolo} - scala 1:25</title>
<defs>
  <pattern id="g10" width="16" height="16" patternUnits="userSpaceOnUse" x="{ox}" y="{oy}">
    <path d="M 16 0 L 0 0 0 16" fill="none" stroke="{c_grid}" stroke-width="0.35"/></pattern>
  <pattern id="g50" width="80" height="80" patternUnits="userSpaceOnUse" x="{ox}" y="{oy}">
    <rect width="80" height="80" fill="url(#g10)"/>
    <path d="M 80 0 L 0 0 0 80" fill="none" stroke="#a9bccf" stroke-width="0.7"/></pattern>
  <pattern id="g100" width="160" height="160" patternUnits="userSpaceOnUse" x="{ox}" y="{oy}">
    <rect width="160" height="160" fill="url(#g50)"/>
    <path d="M 160 0 L 0 0 0 160" fill="none" stroke="#7f98b3" stroke-width="1"/></pattern>
  <pattern id="rad" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
    <line x1="0" y1="0" x2="0" y2="6" stroke="{C_RAD}" stroke-width="1.2"/></pattern>
  <pattern id="col" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(-45)">
    <line x1="0" y1="0" x2="0" y2="7" stroke="#8a8a8a" stroke-width="1"/></pattern>
  <marker id="fr" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M 0 1 L 9 5 L 0 9 z" fill="{C_OK}"/></marker>
</defs>
<style>
  .dim line {{ stroke:{gp.C_DIM}; stroke-width:0.7; }} .dim .ext {{ stroke-width:0.45; }}
  .dim .tick {{ stroke-width:1.3; }} .dim text {{ fill:{gp.C_DIM}; font-weight:600; }}
  .lbl {{ font-weight:700; letter-spacing:1px; fill:#1d1d1d; }}
  .t {{ fill:#2b2b2b; }} .s {{ fill:#666; }}
</style>
<rect width="{W}" height="{H}" fill="#fff"/>''')
    if arredata:
        w(f'<rect x="20" y="20" width="{W-40}" height="{H-40}" fill="none" stroke="#111" stroke-width="1.5"/>')
        w('<text x="50" y="68" font-size="30" class="lbl">CUCINA — PIANTA DI DETTAGLIO</text>')
        w('<text x="50" y="98" font-size="15" fill="#555">Scala 1:25 (A3) · misure in cm · orientamento come lo schizzo · '
          'BOZZA: i punti arancioni vanno confermati</text>')

    # --- muri e pavimento
    t.rect(m(-T_SX), m(-T_TOP), m(W_CM + T_DX), m(L_CM + T_BOT), fill=C_WALL)
    t.rect(0, 0, m(W_CM), m(L_CM), fill='#fbfaf7')
    t.rect(0, 0, m(W_CM), m(L_CM), fill='url(#g100)')

    # --- finestra + calorifero + elemento d'angolo
    finestra_cucina(t, 37, 99)
    t.rect(m(77), 0, m(92), m(10), fill='url(#rad)', stroke=C_RAD, stroke_width=1.5)
    t.rect(0, 0, m(26), m(20), fill='url(#col)', stroke='#555', stroke_width=1.5)
    punto(t, 1, 68, -T_TOP / 2 - 26)
    punto(t, 2, 84, 26)
    punto(t, 3, -26, 12)
    t.text(m(13), m(10), '26', size=10, fill='#555', font_weight='700')

    # --- porte
    gp.porta_battente(t, 'P6', 'h', m(15), m(94), 0, -1, m(T_BOT), m(L_CM))
    gp.porta_battente(t, 'P2', 'v', m(310), m(382), 1, +1, m(T_DX), m(W_CM))
    punto(t, 4, W_CM + T_DX + 72, 340)

    # --- prese
    presa(t, 0, 30, 2, 22)
    presa(t, 0, 268, 2, 22)
    presa(t, W_CM, 262, 1, -22)

    # --- limite zona cucina / ingresso
    t.line(0, m(Z_CUCINA), m(W_CM), m(Z_CUCINA), stroke=C_DOOR, stroke_width=1.4, stroke_dasharray='9 6')

    if arredata:
        for v0, ln, vc in MODULI:
            mob(t, vc, RUN_U0, v0, 'sx')
        punto(t, 5, RUN_U0 + 9, 192)
        # ingombri di apertura (tratteggio arancione)
        t.rect(m(RUN_U0 - 60), m(147), m(RUN_U0), m(192), fill='none', stroke=C_WARN, stroke_width=1.2, stroke_dasharray='5 3')
        t.text(m(RUN_U0 - 30), m(169.5), 'sportello', size=9, fill=C_WARN, font_weight='600')
        t.arc((m(RUN_U0), m(250)), (m(RUN_U0), m(192)), (m(RUN_U0 - 58), m(250)), m(58),
              stroke=C_WARN, stroke_width=1.2, stroke_dasharray='5 3')
        t.line(m(RUN_U0), m(250), m(RUN_U0 - 58), m(250), stroke=C_WARN, stroke_width=1.2, stroke_dasharray='5 3')
        # tavolo a ribalta opzionale sulla parete sinistra (aperto 30 cm)
        t.rect(0, m(160), m(30), m(240), fill='#fff8ec', stroke=C_WARN, stroke_width=1.4, stroke_dasharray='6 3')
        X, Y = P(15, 200)
        t.w(f'<text x="{X:.1f}" y="{Y:.1f}" font-size="11" font-weight="700" fill="{C_WARN}" text-anchor="middle" '
            f'dominant-baseline="middle" transform="rotate(-90 {X:.1f} {Y:.1f})">ribalta 80×30 (opz.)</text>')
        # verifiche di spazio
        gl.verifica(t, (0.0, 1.20), (m(RUN_U0), 1.20))
        etich = [('INGRESSO', '150×154', 77, 290, 0)]
        for nome, sub, u, v, rot in etich:
            X, Y = P(u, v)
            w(f'<g transform="rotate({rot} {X:.1f} {Y:.1f})"><rect x="{X-52:.1f}" y="{Y-17:.1f}" width="104" height="34" rx="4" '
              f'fill="#fff" fill-opacity="0.9" stroke="#333" stroke-width="0.7"/>'
              f'<text x="{X:.1f}" y="{Y-5:.1f}" font-size="12" text-anchor="middle" dominant-baseline="middle" class="lbl">{nome}</text>'
              f'<text x="{X:.1f}" y="{Y+9:.1f}" font-size="10.5" fill="#444" text-anchor="middle" dominant-baseline="middle">{sub}</text></g>')
        X, Y = P(46, 75)
        w(f'<g><rect x="{X-52:.1f}" y="{Y-17:.1f}" width="104" height="34" rx="4" fill="#fff" fill-opacity="0.9" stroke="#333" stroke-width="0.7"/>'
          f'<text x="{X:.1f}" y="{Y-5:.1f}" font-size="12" text-anchor="middle" dominant-baseline="middle" class="lbl">CUCINA</text>'
          f'<text x="{X:.1f}" y="{Y+9:.1f}" font-size="10.5" fill="#444" text-anchor="middle" dominant-baseline="middle">250×154 · lineare</text></g>')

    # --- quote
    t.quota((0, m(-T_TOP)), (m(W_CM), m(-T_TOP)), str(W_CM), off=0.95, lato=-1, size=13)
    t.quota((0, m(-T_TOP)), (m(37), m(-T_TOP)), '≈37', off=0.40, lato=-1, size=11)
    t.quota((m(37), m(-T_TOP)), (m(99), m(-T_TOP)), '≈62', off=0.40, lato=-1, size=11)
    t.quota((m(99), m(-T_TOP)), (m(W_CM), m(-T_TOP)), '≈55', off=0.40, lato=-1, size=11)
    t.quota((m(-T_SX), 0), (m(-T_SX), m(L_CM)), str(L_CM), off=0.95, lato=1, size=13)
    t.quota((m(-T_SX), 0), (m(-T_SX), m(Z_CUCINA)), '250', off=0.40, lato=1, size=11)
    t.quota((m(-T_SX), m(Z_CUCINA)), (m(-T_SX), m(L_CM)), '150', off=0.40, lato=1, size=11)
    xr = W_CM + T_DX
    for (a, b, txt) in ((0, 85, '≈85'), (85, 147, '62'), (147, 192, '45'), (192, 250, '58')):
        t.quota((m(xr), m(a)), (m(xr), m(b)), txt, off=0.40, lato=-1, size=11)
    for (a, b, txt) in ((250, 310, '60'), (310, 382, '≈72'), (382, 400, '18')):
        t.quota((m(xr), m(a)), (m(xr), m(b)), txt, off=1.10, lato=-1, size=11)
    yb = L_CM + T_BOT
    for (a, b, txt) in ((0, 15, '15'), (15, 94, '≈79'), (94, W_CM, '60')):
        t.quota((m(a), m(yb)), (m(b), m(yb)), txt, off=0.40, lato=1, size=11)

    if arredata:
        # ------------------------------------------------ colonna destra
        X0 = 820
        y = 150

        def head(txt):
            nonlocal y
            w(f'<text x="{X0}" y="{y}" font-size="13" class="lbl">{txt}</text>')
            y += 22

        def row(txt, col='#2b2b2b', size=12, bold=False, dx=0, after=17):
            nonlocal y
            b = ' font-weight="700"' if bold else ''
            w(f'<text x="{X0+dx}" y="{y}" font-size="{size}" fill="{col}"{b}>{txt}</text>')
            y += after

        head('COME HO LETTO LO SCHIZZO')
        letto = [
            ('✔', C_OK, 'Locale 154 × 400 cm (≈ 6,2 m²)', 'barre gialle'),
            ('✔', C_OK, 'Zona cucina 250 + ingresso 150 = 400', 'linea rossa tratteggiata'),
            ('✔', C_OK, 'Parete destra: cucina lineare di 250 cm', 'quota "250 cm"'),
            ('⚠', C_WARN, 'Profondità blocco 62; moduli 85+62+45+58', '"62", "45", "58" + 85 per differenza'),
            ('✔', C_OK, 'Porta P6: 15 + 79 + 60 = 154', 'luce ricavata per differenza'),
            ('⚠', C_WARN, 'Porta P2: luce ≈72, apre all\'esterno', '150 − 60 − 18; verso dal disegno'),
            ('✔', C_OK, 'Prese: 2× e 2× a sinistra, 1× a destra', 'posizione e altezza indicative'),
        ]
        for ic, col, a, b in letto:
            w(f'<text x="{X0}" y="{y}" font-size="13" font-weight="700" fill="{col}">{ic}</text>'
              f'<text x="{X0+22}" y="{y}" font-size="12" class="t">{a}</text>')
            y += 15
            w(f'<text x="{X0+22}" y="{y}" font-size="10.5" class="s">{b}</text>')
            y += 20
        y += 6

        head('PUNTI DA CONFERMARE')
        dubbi = [
            ('1', 'Finestra: larghezza (≈62), altezza dal pavimento'),
            ('2', 'Calorifero: dimensioni (disegnato ≈15×10)'),
            ('3', 'Elemento d\'angolo "26 cm" in alto a sinistra: cos\'è?'),
            ('4', 'Porta P2: larghezza e verso di apertura'),
            ('5', 'Moduli a destra: sono i mobili esistenti? tipo dei 45 e 58'),
        ]
        for n, txt in dubbi:
            w(f'<circle cx="{X0+8}" cy="{y-4}" r="9" fill="{C_WARN}"/>'
              f'<text x="{X0+8}" y="{y-3.5}" font-size="11" font-weight="700" fill="#fff" text-anchor="middle" dominant-baseline="middle">{n}</text>'
              f'<text x="{X0+26}" y="{y}" font-size="12" class="t">{txt}</text>')
            y += 22
        row('Non ho posizionato i numeri "11" e "18 cm" in basso a destra.', '#666', 11, after=24)

        head('VERIFICHE DI SPAZIO')
        ver = [
            (C_OK, '✔', 'Corsia libera 92 cm (minimo 90 per cucina a parete unica)'),
            (C_OK, '✔', 'Arco porta P6 (79 cm) non interferisce con il blocco'),
            (C_OK, '✔', 'Piano cottura: 85 cm e 45 cm di appoggio ai lati (≥ 40)'),
            (C_OK, '✔', 'Parete esterna a destra: cappa con scarico diretto'),
            (C_WARN, '⚠', 'Sportello lavastoviglie aperto: restano ≈ 32 cm'),
            (C_WARN, '⚠', 'Frigo: cerniere lato disimpegno, sportello verso l\'area libera'),
            (C_WARN, '⚠', 'Tavolo vero non entra: 92 cm − 60 = 32 cm per le sedie'),
        ]
        for col, ic, txt in ver:
            w(f'<text x="{X0}" y="{y}" font-size="13" font-weight="700" fill="{col}">{ic}</text>'
              f'<text x="{X0+22}" y="{y}" font-size="12" class="t">{txt}</text>')
            y += 19
        y += 8

        head('ALTEZZE (h 2,30 m da confermare)')
        row('Base 90 + paraschizzi 55 + pensile 72 = 217 cm: restano 13 cm.', after=17)
        row('Colonne e frigo da incasso: altezza massima ≈ 2,20 m.', after=24)

        head('LEGENDA')
        leg = [
            (f'<rect width="26" height="12" fill="{C_WALL}"/>', 'Muro (30 cm ipotesi, 11 cm tramezzo)'),
            (f'<rect width="26" height="12" fill="#dbeafb" stroke="{C_WIN}" stroke-width="2"/>', 'Finestra, ante all\'interno'),
            (f'<rect width="26" height="12" fill="url(#rad)" stroke="{C_RAD}" stroke-width="1.5"/>', 'Calorifero'),
            (f'<rect x="6" y="-1" width="14" height="14" rx="2" fill="#fff" stroke="{C_SOCK}" stroke-width="1.8"/>', 'Presa (n× = quantità)'),
            (f'<line x1="0" y1="6" x2="26" y2="6" stroke="{C_WARN}" stroke-width="1.5" stroke-dasharray="5 3"/>', 'Ingombro apertura / opzionale'),
            (f'<circle cx="13" cy="6" r="9" fill="{C_WARN}"/>', 'Da confermare'),
        ]
        for i, (sym, txt) in enumerate(leg):
            xx = X0 + (i % 2) * 290
            yy = y + (i // 2) * 26
            w(f'<g transform="translate({xx},{yy})">{sym}<text x="36" y="10" font-size="11.5" class="t">{txt}</text></g>')
        y += 3 * 26 + 14
        row('Libreria arredi in scala 1:50: per usarla qui ingrandire i pezzi ×2.', '#666', 11)
        w(f'<g transform="translate({X0},{y+10})"><text y="-8" font-size="11" class="lbl">SCALA GRAFICA 1:25</text>')
        for i in range(2):
            w(f'<rect x="{i*160}" y="0" width="160" height="7" fill="{"#111" if i%2==0 else "#fff"}" stroke="#111"/>')
        for i in range(3):
            w(f'<text x="{i*160}" y="22" font-size="10" text-anchor="middle">{i}</text>')
        w('<text x="332" y="22" font-size="10">m</text></g>')
    else:
        X, Y = gp.P(0, m(L_CM + 120))
        w(f'<text x="{ox}" y="{Y:.1f}" font-size="11" fill="#666">Scala 1:25 (160 px = 1 m) · griglia 10 / 50 / 100 cm · '
          f'pezzi libreria (80 px/m) ×2</text>')
        w(f'<text x="{ox}" y="{Y+16:.1f}" font-size="11" fill="#d98200">Elementi arancioni da confermare: finestra, calorifero, '
          f'angolo 26 cm, P2</text>')

    w('</svg>')
    with open(nome_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(t.o))


if __name__ == '__main__':
    genera(True, 'cucina_dettaglio_arredata.svg')
    genera(False, 'cucina_template_vuoto.svg')
    print('ok')
