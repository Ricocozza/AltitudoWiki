"""Piante di dettaglio 1:25 di bagno, sala, corridoio e camera, dagli schizzi quotati.

Stesso stile e stessa scala della cucina (genera_cucina.py): 160 px = 1 m.
Ogni stanza è descritta da una specifica (misure, muri, aperture, impianti,
elementi esistenti, arredo proposto, testi della scheda) e disegnata con lo
stesso motore. Coordinate in cm: origine = angolo in alto a sinistra
dell'interno, u verso destra, v verso il basso, orientamento come lo schizzo.

Per ogni stanza genera:
  <stanza>_dettaglio_arredata.svg   scheda con arredo, verifiche e dubbi
  <stanza>_template_vuoto.svg       solo muri, aperture, impianti e sanitari
"""
import genera_pianta_abitazione as gp
import genera_libreria_arredi as lib
import genera_layout as gl
import genera_cucina as gc

S = gp.S                      # 160 px/m, impostato da genera_cucina
C_WALL, C_WIN, C_DOOR, C_OK = gp.C_WALL, gp.C_WIN, gp.C_DOOR, gl.C_OK
C_WARN, C_SOCK, C_RAD, C_SW = gc.C_WARN, gc.C_SOCK, gc.C_RAD, '#2a9d8f'
EXT, TRA = 30, 11             # muro esterno (ipotesi) e tramezzo (dallo schizzo cucina)


def m(cm):
    return cm / 100.0


def P(u, v):
    return gp.P(m(u), m(v))


def V(chiave):
    return gl.CAT[chiave]


def su_misura(cat, nome, w, d, fn, **extra):
    return (cat, 'custom', nome, w, d, fn, None, extra)


# ------------------------------------------------------------------ simboli generici
def finestra(t, sp, lato, a0, a1, ante):
    W, L, T = sp['W'], sp['L'], sp['muri']
    if lato in ('top', 'bottom'):
        v0, v1 = (-T['top'], 0) if lato == 'top' else (L, L + T['bottom'])
        t.rect(m(a0), m(v0), m(a1), m(v1), fill='#dbeafb', stroke=C_WIN, stroke_width=2)
        vm = (v0 + v1) / 2
        for dv in (-1.5, 1.5):
            t.line(m(a0), m(vm + dv), m(a1), m(vm + dv), stroke=C_WIN, stroke_width=1)
        face, sgn = (0, 1) if lato == 'top' else (L, -1)
    else:
        u0, u1 = (-T['left'], 0) if lato == 'left' else (W, W + T['right'])
        t.rect(m(u0), m(a0), m(u1), m(a1), fill='#dbeafb', stroke=C_WIN, stroke_width=2)
        um = (u0 + u1) / 2
        for du in (-1.5, 1.5):
            t.line(m(um + du), m(a0), m(um + du), m(a1), stroke=C_WIN, stroke_width=1)
        face, sgn = (0, 1) if lato == 'left' else (W, -1)
    Lf = (a1 - a0) / ante
    cerniere = [(a0, a0 + Lf)] if ante == 1 else [(a0, a0 + Lf), (a1, a1 - Lf)]
    if ante == 2:
        mid = (a0 + a1) / 2
        if lato in ('top', 'bottom'):
            t.line(m(mid), m(v0), m(mid), m(v1), stroke=C_WIN, stroke_width=1.5)
        else:
            t.line(m(u0), m(mid), m(u1), m(mid), stroke=C_WIN, stroke_width=1.5)
    for h, o in cerniere:
        if lato in ('top', 'bottom'):
            hp, tip, op = (m(h), m(face)), (m(h), m(face + sgn * Lf)), (m(o), m(face))
        else:
            hp, tip, op = (m(face), m(h)), (m(face + sgn * Lf), m(h)), (m(face), m(o))
        t.line(*hp, *tip, stroke=C_WIN, stroke_width=1.2, stroke_dasharray='5 3')
        t.arc(hp, tip, op, m(Lf), stroke=C_WIN, stroke_width=0.9, stroke_dasharray='5 3')


def porta(t, sp, pid, lato, a0, a1, cerniera, verso_stanza):
    """Porta a battente. verso_stanza True = apre verso l'interno di questa stanza."""
    W, L, T = sp['W'], sp['L'], sp['muri']
    if lato == 'top':
        par, filo, spess, verso = 'h', -T['top'], T['top'], (1 if verso_stanza else -1)
    elif lato == 'bottom':
        par, filo, spess, verso = 'h', L, T['bottom'], (-1 if verso_stanza else 1)
    elif lato == 'left':
        par, filo, spess, verso = 'v', -T['left'], T['left'], (1 if verso_stanza else -1)
    else:
        par, filo, spess, verso = 'v', W, T['right'], (-1 if verso_stanza else 1)
    gp.porta_battente(t, pid, par, m(a0), m(a1), cerniera, verso, m(spess), m(filo))
    # etichetta porta sul muro
    um, vm = ((a0 + a1) / 2, filo + spess / 2) if par == 'h' else (filo + spess / 2, (a0 + a1) / 2)
    X, Y = P(um, vm)
    t.w(f'<g><rect x="{X-14:.1f}" y="{Y-9:.1f}" width="28" height="18" rx="9" fill="#fff" stroke="{C_DOOR}" stroke-width="1.3"/>'
        f'<text x="{X:.1f}" y="{Y+0.5:.1f}" font-size="10" font-weight="700" fill="{C_DOOR}" text-anchor="middle" '
        f'dominant-baseline="middle">{pid}</text></g>')


def radiatore(t, u0, v0, u1, v1):
    t.rect(m(u0), m(v0), m(u1), m(v1), fill='url(#rad)', stroke=C_RAD, stroke_width=1.5)


def presa(t, u, v, n, dx=22, dy=0):
    X, Y = P(u, v)
    t.w(f'<g><rect x="{X-7:.1f}" y="{Y-13:.1f}" width="14" height="26" rx="2" fill="#fff" stroke="{C_SOCK}" stroke-width="1.8"/>'
        f'<circle cx="{X:.1f}" cy="{Y-6:.1f}" r="1.8" fill="{C_SOCK}"/><circle cx="{X:.1f}" cy="{Y+6:.1f}" r="1.8" fill="{C_SOCK}"/>'
        + (f'<text x="{X+dx:.1f}" y="{Y+dy+0.5:.1f}" font-size="14" font-weight="700" fill="{C_SOCK}" '
           f'text-anchor="middle" dominant-baseline="middle">{n}×</text>' if n else '') + '</g>')


def interruttore(t, u, v):
    X, Y = P(u, v)
    t.w(f'<g><rect x="{X-8:.1f}" y="{Y-11:.1f}" width="16" height="22" rx="4" fill="#e7f6f3" stroke="{C_SW}" stroke-width="1.8"/>'
        f'<line x1="{X-3:.1f}" y1="{Y+4:.1f}" x2="{X+3:.1f}" y2="{Y-4:.1f}" stroke="{C_SW}" stroke-width="2"/></g>')


def etichetta(t, nome, sub, u, v, w=None):
    X, Y = P(u, v)
    w = w or max(len(nome) * 9 + 20, len(sub) * 6.2 + 16, 96)
    t.w(f'<g><rect x="{X-w/2:.1f}" y="{Y-17:.1f}" width="{w:.0f}" height="34" rx="4" fill="#fff" fill-opacity="0.92" '
        f'stroke="#333" stroke-width="0.7"/>'
        f'<text x="{X:.1f}" y="{Y-5:.1f}" font-size="12" text-anchor="middle" dominant-baseline="middle" class="lbl">{nome}</text>'
        f'<text x="{X:.1f}" y="{Y+9:.1f}" font-size="10.5" fill="#444" text-anchor="middle" dominant-baseline="middle">{sub}</text></g>')


def nota(t, testo, u, v, col=C_WARN, size=10, rot=0):
    X, Y = P(u, v)
    tr = f' transform="rotate({rot} {X:.1f} {Y:.1f})"' if rot else ''
    t.w(f'<text x="{X:.1f}" y="{Y:.1f}" font-size="{size}" font-weight="700" fill="{col}" text-anchor="middle" '
        f'dominant-baseline="middle"{tr}>{testo}</text>')


def tratteggio(t, u0, v0, u1, v1, col=C_WARN):
    t.rect(m(u0), m(v0), m(u1), m(v1), fill='none', stroke=col, stroke_width=1.2, stroke_dasharray='5 3')


def catena(t, sp, lato, segmenti, off, size=11):
    W, L, T = sp['W'], sp['L'], sp['muri']
    for a, b, txt in segmenti:
        if lato == 'top':
            p1, p2, la = (m(a), m(-T['top'])), (m(b), m(-T['top'])), -1
        elif lato == 'bottom':
            p1, p2, la = (m(a), m(L + T['bottom'])), (m(b), m(L + T['bottom'])), 1
        elif lato == 'left':
            p1, p2, la = (m(-T['left']), m(a)), (m(-T['left']), m(b)), 1
        else:
            p1, p2, la = (m(W + T['right']), m(a)), (m(W + T['right']), m(b)), -1
        t.quota(p1, p2, txt, off=off, lato=la, size=size)


# ------------------------------------------------------------------ BAGNO
def bagno_fissi(t, sp):
    # doccia 80 x 103 nell'angolo in alto a destra, vetro sul lato sinistro
    mob = gc.mob
    mob(t, su_misura('bagno', 'doccia', 80, 103, lib.doccia), 65, 0, 'giu')
    t.line(m(65), 0, m(65), m(103), stroke='#5b8db8', stroke_width=4)
    X, Y = P(141, 50)
    t.w(f'<g><rect x="{X-5:.1f}" y="{Y-14:.1f}" width="9" height="28" rx="2" fill="#fff" stroke="#555" stroke-width="1.2"/>'
        f'<circle cx="{X-14:.1f}" cy="{Y:.1f}" r="9" fill="#fff" stroke="#555" stroke-width="1.2"/></g>')
    mob(t, V('wc'), 17, 0, 'giu')
    mob(t, V('bidet'), 0, 104, 'dx')
    mob(t, su_misura('bagno', 'lavabo 100', 100, 48, lib.lavabo), 0, 165, 'dx')
    radiatore(t, 135, 203, 145, 241)
    # simbolo "X (+1)" sopra la doccia
    X, Y = P(65, -15)
    t.w(f'<g><circle cx="{X:.1f}" cy="{Y:.1f}" r="9" fill="#fff" stroke="#555" stroke-width="1.4"/>'
        f'<line x1="{X-6:.1f}" y1="{Y-6:.1f}" x2="{X+6:.1f}" y2="{Y+6:.1f}" stroke="#555" stroke-width="1.4"/>'
        f'<line x1="{X-6:.1f}" y1="{Y+6:.1f}" x2="{X+6:.1f}" y2="{Y-6:.1f}" stroke="#555" stroke-width="1.4"/></g>')


def bagno_arredo(t, sp):
    gc.mob(t, su_misura('bagno', 'colonna', 60, 30, lib.box), 115, 108, 'sx')
    t.rect(0, m(175), m(4), m(255), fill='#cfe3f3', stroke='#5b8db8', stroke_width=1.2)
    nota(t, 'specchio', -15, 215, '#ffffff', 9, -90)
    tratteggio(t, 72, 108, 112, 146, '#5b8db8')
    nota(t, 'tappeto', 92, 127, '#5b8db8', 9)


BAGNO = dict(
    nome='BAGNO', file='bagno', W=145, L=275,
    muri=dict(top=EXT, left=EXT, right=TRA, bottom=TRA),
    orient='Come lo schizzo e la pianta generale: in alto muro esterno (Est), a sinistra '
           'muro esterno con finestra (Nord), in basso la porta sul corridoio.',
    finestre=[('left', 83, 163, 1)],
    porte=[('P3', 'bottom', 57, 127, 1, True)],
    prese=[(0, 150, 2, 22, 0), (145, 193, 1, -22, 0)],
    interruttori=[(145, 176)],
    fissi=bagno_fissi, arredo=bagno_arredo,
    marcatori=[(1, 36, 72), (2, 64, 206), (3, 85, -15), (4, 128, 176), (5, 120, 222)],
    etichetta=None,
    quote=[('top', [(0, 65, '65'), (65, 145, '80')], 0.40), ('top', [(0, 145, '145')], 0.95),
           ('left', [(0, 83, '83'), (83, 163, '80'), (163, 275, '112')], 0.40), ('left', [(0, 275, '275')], 0.95),
           ('bottom', [(0, 57, '57'), (57, 127, '70'), (127, 145, '18')], 0.40),
           ('right', [(0, 103, '103'), (103, 193, '90'), (193, 275, '82')], 0.40)],
    letture=[
        ('✔', 'Locale 145 × 275 cm (≈ 4,0 m²)', 'barre gialle'),
        ('✔', 'Finestra a sinistra: 83 dall\'alto, larga 80', 'quote rosse'),
        ('✔', 'Porta P3: 57 + 70 + 18 = 145, apre nel bagno', 'stessa porta del corridoio (60 + 68 + 22)'),
        ('✔', 'Doccia 80 × 103 in alto a destra, vetro di 103', 'miscelatore sulla parete destra'),
        ('⚠', 'WC in alto, bidet sotto la finestra, lavabo da 100', 'posizioni lungo le pareti non quotate'),
        ('⚠', 'Rettangolo vicino alla porta: termoarredo?', 'disegnato ≈ 40 × 10'),
        ('✔', 'Prese: 2× a sinistra, 1× a destra 90 cm sotto la doccia', 'verde sopra la presa: interruttore'),
    ],
    dubbi=[
        'WC: distanza dell\'asse dal muro sinistro (ho messo 36 cm)',
        'Bidet e lavabo: dove iniziano lungo la parete sinistra',
        'Simbolo "X (+1)" sopra la doccia: punto luce o aspiratore?',
        'Simbolo verde a destra: interruttore? (anche nel corridoio)',
        'Termoarredo vicino alla porta: misure',
    ],
    proposta=['Elementi esistenti mantenuti. Aggiunti: colonna 30 cm accanto',
              'alla doccia, specchio sopra il lavabo, tappeto doccia.',
              'La lavatrice (60×60) non entra con lo spazio di carico.'],
    verifiche=[
        (True, 'Davanti al lavabo ≥ 85 cm liberi (minimo 55–60)'),
        (True, 'Davanti al bidet 60 cm fino alla colonna'),
        (True, 'Arco della porta libero: lavabo a 9 cm'),
        (True, 'Ingresso doccia 80 cm libero'),
        (False, 'Davanti al WC 49 cm fino al bidet (consigliati 55–60)'),
        (False, 'Asse WC a 36 cm dal muro, 10 cm dal vetro (consigliati ≥ 40)'),
    ],
)

# ------------------------------------------------------------------ SALA


def sala_arredo(t, sp):
    mob = gc.mob
    mob(t, V('tappeto'), 20, 80, 'giu')
    mob(t, V('mobile_tv'), 30, 0, 'giu')
    mob(t, V('tavolino'), 70, 105, 'giu')
    mob(t, V('divano_3posti'), 10, 200, 'su')
    mob(t, V('tavolo_120x80_4sedie'), 250, 185, 'giu')
    mob(t, V('pianta_60'), 330, 10, 'giu')


SALA = dict(
    nome='SALA', file='sala', W=400, L=400,
    muri=dict(top=EXT, right=EXT, left=TRA, bottom=TRA),
    orient='Come lo schizzo e la pianta generale: in alto muro esterno cieco (Est), '
           'a destra finestra (Sud), a sinistra la porta sul corridoio.',
    finestre=[('right', 120, 290, 2)],
    porte=[('P4', 'left', 300, 380, 1, True)],
    prese=[(100, 0, 2, 0, 84), (300, 0, 2, 0, 24), (320, 400, 1, 0, -24)],
    interruttori=[],
    fissi=lambda t, sp: radiatore(t, 388, 165, 400, 245),
    arredo=sala_arredo,
    extra=lambda t, sp: presa(t, 174, 149, 0),
    marcatori=[(1, 372, 135), (2, 372, 255), (3, 192, 135), (4, 28, 296)],
    etichetta=('SALA', '400×400 · 16 m²', 120, 345),
    quote=[('top', [(0, 100, '100'), (100, 300, '200'), (300, 400, '100')], 0.40), ('top', [(0, 400, '400')], 0.95),
           ('right', [(0, 120, '120'), (120, 290, '≈170'), (290, 400, '110')], 0.40),
           ('left', [(0, 300, '≈300'), (300, 380, '≈80'), (380, 400, '≈20')], 0.40), ('left', [(0, 400, '400')], 0.95),
           ('bottom', [(0, 320, '320'), (320, 400, '80')], 0.40)],
    letture=[
        ('✔', 'Locale 400 × 400 cm (16 m²)', 'barre gialle'),
        ('✔', 'Prese 2× sulla parete in alto, a 1 m dagli angoli', 'quote "1m"'),
        ('✔', 'Finestra a destra: 120 dall\'alto, 110 dal basso', 'larghezza ≈170 per differenza'),
        ('✔', 'Calorifero sotto la finestra', 'misure non quotate'),
        ('⚠', 'Presa al centro della stanza', 'a pavimento o punto luce a soffitto?'),
        ('✔', 'Presa in basso a 80 cm dall\'angolo destro', 'quota "80 cm"'),
        ('⚠', 'Porta P4 a sinistra, vicino all\'angolo in basso', 'larghezza ≈80 dal disegno'),
    ],
    dubbi=[
        'Finestra: larghezza (170?) e altezza del davanzale',
        'Calorifero: lunghezza e profondità',
        'Simbolo al centro: presa a pavimento o punto luce?',
        'Porta P4: larghezza e distanza dall\'angolo in basso',
    ],
    proposta=['TV sulla parete cieca in alto, dove ci sono già le prese 2×:',
              'la luce arriva di lato, senza riflessi sullo schermo. Divano di',
              'fronte alla TV, tavolo 4 posti vicino alla finestra: cucina e',
              'corridoio sono troppo stretti per mangiare, la sala è l\'unico posto.'],
    verifiche=[
        (True, 'TV–divano 160 cm: adatta a una TV da 50–55"'),
        (True, 'Tavolino a 45 cm dal divano'),
        (True, 'Passaggio dietro il divano 110 cm, dalla porta al tavolo'),
        (True, 'Arco della porta P4 libero'),
        (True, 'Tavolo a 18 cm dal calorifero, luce naturale sul tavolo'),
        (True, 'Presa al centro utile per una lampada accanto al divano'),
        (False, 'Dietro le sedie in basso 55 cm: ok per sedersi, non per passare'),
        (False, 'Ante della finestra aperte toccano una sedia: meglio anta-ribalta'),
    ],
)

# ------------------------------------------------------------------ CORRIDOIO


def corridoio_arredo(t, sp):
    mob = gc.mob
    mob(t, su_misura('ingresso', 'armadio', 150, 40, lib.armadio, ante=3), 0, 30, 'dx')
    mob(t, V('consolle'), 120, 290, 'sx')
    t.rect(m(146), m(300), m(150), m(380), fill='#cfe3f3', stroke='#5b8db8', stroke_width=1.2)
    mob(t, V('scarpiera'), 0, 390, 'dx')
    tratteggio(t, 45, 200, 105, 430, '#9c8b6e')
    nota(t, 'passatoia 60×230', 75, 315, '#9c8b6e', 10, -90)


CORRIDOIO = dict(
    nome='CORRIDOIO', file='corridoio', W=150, L=570,
    muri=dict(left=EXT, bottom=EXT, top=TRA, right=TRA),
    orient='Come lo schizzo e la pianta generale: in alto il bagno, a destra sala, camera '
           'e cucina, a sinistra la finestra (Nord), in basso l\'ingresso.',
    finestre=[('left', 210, 370, 2)],
    porte=[('P3', 'top', 60, 128, 1, False), ('P4', 'right', 26, 106, 1, False),
           ('P5', 'right', 146, 218, 0, False), ('P6', 'right', 446, 525, 0, False),
           ('P1', 'bottom', 43, 123, 0, True)],
    prese=[(150, 232, 1, -22, 0)],
    interruttori=[(137, 0), (150, 545)],
    fissi=lambda t, sp: radiatore(t, 0, 245, 12, 335),
    arredo=corridoio_arredo,
    marcatori=[(1, 26, 290), (2, 83, 535), (3, 137, 24), (4, 130, 120)],
    etichetta=('CORRIDOIO', '150×570 · 8,6 m²', 92, 192),
    top_off=1.40,
    quote=[('top', [(0, 60, '60'), (60, 128, '68'), (128, 150, '22')], 0.95), ('top', [(0, 150, '150')], 1.40),
           ('left', [(0, 210, '210'), (210, 370, '≈160'), (370, 570, '200')], 0.40), ('left', [(0, 570, '570')], 0.95),
           ('right', [(0, 26, '≈26'), (26, 106, '≈80'), (106, 146, '40'), (146, 218, '≈72'),
                      (218, 446, '228'), (446, 525, '79'), (525, 570, '45')], 1.05),
           ('bottom', [(0, 43, '≈43'), (43, 123, '≈80'), (123, 150, '≈27')], 0.40)],
    letture=[
        ('✔', 'Corridoio 150 × 570 cm (≈ 8,6 m²)', 'barre gialle'),
        ('✔', 'Porta bagno: 60 + 68 + 22 = 150, apre nel bagno', 'coerente con il bagno (70)'),
        ('✔', 'Finestra a sinistra: 210 dall\'alto, 200 dal basso', 'con calorifero; larghezza ≈160'),
        ('✔', 'A destra: sala · 40 · camera · 228 · cucina · 45', 'porte che aprono nelle stanze'),
        ('⚠', 'Larghezza porte sala e camera dal disegno (≈80, ≈72)', 'cucina 79 dal dettaglio cucina'),
        ('⚠', 'Ingresso principale in basso: larghezza non quotata', 'disegnato ≈80, apertura ipotizzata'),
        ('✔', 'Presa a destra dopo la camera, 2 interruttori (verdi)', '"ELETTRICI" in alto a destra'),
    ],
    dubbi=[
        'Finestra (≈160) e calorifero: misure',
        'Porta d\'ingresso: larghezza, posizione, verso di apertura',
        '"ELETTRICI" in alto: interruttori o quadro elettrico?',
        'Porte sala e camera: larghezze e tratto di 26 cm in alto',
    ],
    proposta=['Armadio poco profondo (40 cm) sul muro cieco a sinistra,',
              'consolle con specchio di fronte alla finestra, scarpiera',
              'vicino all\'ingresso dietro l\'anta. Le porte delle stanze',
              'aprono verso le stanze: il corridoio resta libero.'],
    verifiche=[
        (True, 'Davanti all\'armadio 110 cm (minimo 90–100)'),
        (True, 'Tra consolle e calorifero 108 cm'),
        (True, 'P3, P4, P5, P6 aprono nelle stanze: nessun ingombro qui'),
        (True, 'Porta d\'ingresso con cerniera a sinistra: interruttore lato maniglia'),
        (False, 'Un armadio da 60 cm ridurrebbe il passaggio a 90 cm'),
    ],
)

# ------------------------------------------------------------------ CAMERA


def camera_arredo(t, sp):
    mob = gc.mob
    mob(t, V('letto_matrimoniale'), 0, 90, 'dx')
    mob(t, V('comodino'), 0, 45, 'dx')
    mob(t, V('comodino'), 0, 250, 'dx')
    mob(t, V('armadio_4ante'), 100, 340, 'su')
    mob(t, V('como'), 255, 110, 'sx')


CAMERA = dict(
    nome='CAMERA DA LETTO', file='camera', W=300, L=400,
    muri=dict(top=EXT, left=TRA, right=TRA, bottom=TRA),
    orient='Ruotata come lo schizzo (e come la cucina): in alto la finestra (Sud), '
           'a sinistra la sala, a destra la cucina, in basso la porta sul corridoio.',
    finestre=[('top', 70, 234, 2)],
    porte=[('P5', 'bottom', 15, 87, 0, True)],
    prese=[(0, 80, 2, 22, 0), (300, 315, 2, -22, 0)],
    interruttori=[],
    fissi=lambda t, sp: radiatore(t, 110, 0, 190, 12),
    arredo=camera_arredo,
    marcatori=[(1, 152, 26), (2, 98, 372)],
    etichetta=('CAMERA', '300×400 · 12 m²', 222, 290),
    quote=[('top', [(0, 70, '70'), (70, 234, '≈164'), (234, 300, '66')], 0.40), ('top', [(0, 300, '300')], 0.95),
           ('left', [(0, 80, '80'), (80, 400, '320')], 0.40), ('left', [(0, 400, '400')], 0.95),
           ('right', [(0, 315, '315'), (315, 400, '85')], 0.40),
           ('bottom', [(0, 15, '≈15'), (15, 87, '≈72'), (87, 300, '≈213')], 0.40)],
    letture=[
        ('✔', 'Camera 300 × 400 cm (12 m²)', 'barre gialle'),
        ('✔', 'Finestra in alto: 70 + 164 + 66 = 300', 'calorifero sotto la finestra'),
        ('✔', 'Prese 2× a sinistra, 80 cm dalla finestra', 'quota "80"'),
        ('✔', 'Prese 2× a destra, 85 cm dalla parete della porta', 'quota "85 cm"'),
        ('⚠', 'Porta in basso a sinistra, apre verso la parete', 'larghezza ≈72 dal disegno'),
        ('✔', 'Schizzo ruotato come la cucina', 'in alto = Sud (finestra)'),
    ],
    dubbi=[
        'Finestra: altezza del davanzale; calorifero: misure',
        'Porta P5: larghezza e distanza dall\'angolo',
    ],
    proposta=['Testiera sulla parete cieca a sinistra: il letto non è sotto la',
              'finestra né allineato alla porta, accesso da entrambi i lati,',
              'comodino accanto alla presa 2×. Armadio sulla parete della',
              'porta, comò di fronte al letto.'],
    verifiche=[
        (True, 'Lato finestra del letto: 90 cm di passaggio'),
        (True, 'Davanti all\'armadio 90 cm (minimo 70–90)'),
        (True, 'Ante della finestra (82 cm) non toccano il letto'),
        (True, 'Arco della porta libero: armadio a 13 cm'),
        (True, 'Presa a destra accessibile sopra l\'armadio'),
        (False, 'Piedi del letto–comò 55 cm (consigliati 60–70)'),
    ],
)

STANZE = [BAGNO, SALA, CORRIDOIO, CAMERA]


# ------------------------------------------------------------------ tavola
def genera(sp, arredata):
    W, L, T = sp['W'], sp['L'], sp['muri']
    top_off = sp.get('top_off', 0.95)
    destra_extra = 60 + max([o for lato, _, o in sp['quote'] if lato == 'right'] + [0.4]) * S
    gp.OX = 110 + 0.95 * S + T['left'] * 1.6
    gp.OY = (150 if arredata else 40) + top_off * S + T['top'] * 1.6
    ox, oy = gp.OX, gp.OY
    X0 = ox + (W + T['right']) * 1.6 + destra_extra + 40
    Wt = int(X0 + 600) if arredata else int(max(X0 + 10, ox + 640))
    Ht = int(max(oy + (L + T['bottom']) * 1.6 + 150, 1180 if arredata else 0))
    t = gp.Tav()
    w = t.w
    titolo = f"{sp['nome']} — {'PIANTA DI DETTAGLIO' if arredata else 'TEMPLATE VUOTO'}"
    w(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{Wt*0.25:.0f}mm" height="{Ht*0.25:.0f}mm" viewBox="0 0 {Wt} {Ht}" font-family="Helvetica, Arial, sans-serif">
<title>{titolo} - scala 1:25</title>
<defs>
  <pattern id="g10" width="16" height="16" patternUnits="userSpaceOnUse" x="{ox}" y="{oy}">
    <path d="M 16 0 L 0 0 0 16" fill="none" stroke="#c3cfdb" stroke-width="0.35"/></pattern>
  <pattern id="g50" width="80" height="80" patternUnits="userSpaceOnUse" x="{ox}" y="{oy}">
    <rect width="80" height="80" fill="url(#g10)"/>
    <path d="M 80 0 L 0 0 0 80" fill="none" stroke="#a9bccf" stroke-width="0.7"/></pattern>
  <pattern id="g100" width="160" height="160" patternUnits="userSpaceOnUse" x="{ox}" y="{oy}">
    <rect width="160" height="160" fill="url(#g50)"/>
    <path d="M 160 0 L 0 0 0 160" fill="none" stroke="#7f98b3" stroke-width="1"/></pattern>
  <pattern id="rad" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
    <line x1="0" y1="0" x2="0" y2="6" stroke="{C_RAD}" stroke-width="1.2"/></pattern>
  <marker id="fr" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M 0 1 L 9 5 L 0 9 z" fill="{C_OK}"/></marker>
</defs>
<style>
  .dim line {{ stroke:{gp.C_DIM}; stroke-width:0.7; }} .dim .ext {{ stroke-width:0.45; }}
  .dim .tick {{ stroke-width:1.3; }} .dim text {{ fill:{gp.C_DIM}; font-weight:600; }}
  .lbl {{ font-weight:700; letter-spacing:1px; fill:#1d1d1d; }} .t {{ fill:#2b2b2b; }} .s {{ fill:#666; }}
</style>
<rect width="{Wt}" height="{Ht}" fill="#fff"/>''')
    if arredata:
        w(f'<rect x="20" y="20" width="{Wt-40}" height="{Ht-40}" fill="none" stroke="#111" stroke-width="1.5"/>')
        w(f'<text x="50" y="68" font-size="30" class="lbl">{titolo}</text>')
        w('<text x="50" y="98" font-size="15" fill="#555">Scala 1:25 · misure in cm · orientamento come lo schizzo · '
          'BOZZA: i punti arancioni vanno confermati</text>')

    # muri, pavimento, aperture, impianti
    t.rect(m(-T['left']), m(-T['top']), m(W + T['right']), m(L + T['bottom']), fill=C_WALL)
    t.rect(0, 0, m(W), m(L), fill='#fbfaf7')
    t.rect(0, 0, m(W), m(L), fill='url(#g100)')
    for lato, a0, a1, ante in sp['finestre']:
        finestra(t, sp, lato, a0, a1, ante)
    sp['fissi'](t, sp)
    if arredata:
        sp['arredo'](t, sp)
    for pid, lato, a0, a1, cern, dentro in sp['porte']:
        porta(t, sp, pid, lato, a0, a1, cern, dentro)
    for u, v, n, dx, dy in sp['prese']:
        presa(t, u, v, n, dx, dy)
    if 'extra' in sp:
        sp['extra'](t, sp)
    for u, v in sp['interruttori']:
        interruttore(t, u, v)
    for n, u, v in sp['marcatori']:
        gc.punto(t, n, u, v)
    for lato, seg, off in sp['quote']:
        catena(t, sp, lato, seg, off, 13 if len(seg) == 1 else 11)
    if arredata and sp.get('etichetta'):
        etichetta(t, *sp['etichetta'])

    if not arredata:
        Y = oy + (L + T['bottom']) * 1.6 + 110
        w(f'<text x="{ox}" y="{Y:.0f}" font-size="11" fill="#666">{sp["nome"].title()} · scala 1:25 (160 px = 1 m) · '
          f'griglia 10 / 50 / 100 cm · pezzi libreria (80 px/m) ×2</text>')
        w(f'<text x="{ox}" y="{Y+16:.0f}" font-size="11" fill="{C_WARN}">Punti arancioni da confermare: '
          f'vedi la pianta di dettaglio</text>')
    else:
        y = 150

        def head(txt):
            nonlocal y
            w(f'<text x="{X0}" y="{y}" font-size="13" class="lbl">{txt}</text>')
            y += 22

        def riga(txt, col='#2b2b2b', size=12, after=17):
            nonlocal y
            w(f'<text x="{X0}" y="{y}" font-size="{size}" fill="{col}">{txt}</text>')
            y += after

        head('ORIENTAMENTO')
        parole, linea, righe = sp['orient'].split(), '', []
        for p in parole:
            if len(linea) + len(p) > 78:
                righe.append(linea)
                linea = ''
            linea += p + ' '
        righe.append(linea)
        for r in righe:
            riga(r.strip(), '#444', 11.5, 16)
        y += 10

        head('COME HO LETTO LO SCHIZZO')
        for ic, a, b in sp['letture']:
            col = C_OK if ic == '✔' else C_WARN
            w(f'<text x="{X0}" y="{y}" font-size="13" font-weight="700" fill="{col}">{ic}</text>'
              f'<text x="{X0+22}" y="{y}" font-size="12" class="t">{a}</text>')
            y += 15
            w(f'<text x="{X0+22}" y="{y}" font-size="10.5" class="s">{b}</text>')
            y += 19
        y += 6

        head('PUNTI DA CONFERMARE')
        for i, txt in enumerate(sp['dubbi'], 1):
            w(f'<circle cx="{X0+8}" cy="{y-4}" r="9" fill="{C_WARN}"/>'
              f'<text x="{X0+8}" y="{y-3.5}" font-size="11" font-weight="700" fill="#fff" text-anchor="middle" '
              f'dominant-baseline="middle">{i}</text><text x="{X0+26}" y="{y}" font-size="12" class="t">{txt}</text>')
            y += 22
        y += 6

        head('ARREDO PROPOSTO')
        for r in sp['proposta']:
            riga(r, '#2b2b2b', 12, 17)
        y += 10

        head('VERIFICHE DI SPAZIO')
        for okv, txt in sp['verifiche']:
            col, ic = (C_OK, '✔') if okv else (C_WARN, '⚠')
            w(f'<text x="{X0}" y="{y}" font-size="13" font-weight="700" fill="{col}">{ic}</text>'
              f'<text x="{X0+22}" y="{y}" font-size="12" class="t">{txt}</text>')
            y += 19
        y += 12

        head('LEGENDA')
        leg = [
            (f'<rect width="26" height="12" fill="{C_WALL}"/>', 'Muro (30 esterno ipotesi, 11 tramezzo)'),
            (f'<rect width="26" height="12" fill="#dbeafb" stroke="{C_WIN}" stroke-width="2"/>', 'Finestra, ante all\'interno'),
            (f'<rect width="26" height="12" fill="url(#rad)" stroke="{C_RAD}" stroke-width="1.5"/>', 'Calorifero / termoarredo'),
            (f'<rect x="6" y="-1" width="14" height="14" rx="2" fill="#fff" stroke="{C_SOCK}" stroke-width="1.8"/>', 'Presa (n× = quantità)'),
            (f'<rect x="5" y="-3" width="16" height="18" rx="4" fill="#e7f6f3" stroke="{C_SW}" stroke-width="1.8"/>', 'Interruttore'),
            (f'<circle cx="13" cy="6" r="9" fill="{C_WARN}"/>', 'Da confermare'),
        ]
        for i, (sym, txt) in enumerate(leg):
            xx = X0 + (i % 2) * 290
            yy = y + (i // 2) * 26
            w(f'<g transform="translate({xx},{yy})">{sym}<text x="36" y="10" font-size="11.5" class="t">{txt}</text></g>')
        y += 3 * 26 + 14
        w(f'<g transform="translate({X0},{y+10})"><text y="-8" font-size="11" class="lbl">SCALA GRAFICA 1:25</text>')
        for i in range(2):
            w(f'<rect x="{i*160}" y="0" width="160" height="7" fill="{"#111" if i % 2 == 0 else "#fff"}" stroke="#111"/>')
        for i in range(3):
            w(f'<text x="{i*160}" y="22" font-size="10" text-anchor="middle">{i}</text>')
        w('<text x="332" y="22" font-size="10">m</text></g>')
        if y + 40 > Ht - 30:
            print(f'ATTENZIONE: colonna testi oltre il foglio in {sp["file"]} ({y} > {Ht})')

    w('</svg>')
    nome = f"{sp['file']}_{'dettaglio_arredata' if arredata else 'template_vuoto'}.svg"
    with open(nome, 'w', encoding='utf-8') as f:
        f.write('\n'.join(t.o))
    return nome, Wt, Ht


if __name__ == '__main__':
    for sp in STANZE:
        for arr in (True, False):
            print(*genera(sp, arr))
