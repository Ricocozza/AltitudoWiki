# Libreria arredi – scala 1:50

Stessa scala della pianta `pianta_abitazione_template`:

| Formato | Scala | Da usare con |
|---|---|---|
| `svg/` | 80 px = 1 m | `pianta_abitazione_template.svg` |
| `png/` | 240 px = 1 m | `pianta_abitazione_template.png` |

## Nomi dei file
`<arredo>_<larghezza>x<profondità>_r<rotazione>` – misure in cm.

- **r0**: lato di utilizzo (seduta, ante, cassetti, lato d'ingresso nel letto) **in basso**, schienale / lato muro in alto.
- **r90 / r180 / r270**: stesso pezzo ruotato in senso orario. Milanote non ruota le immagini, per questo ci sono le 4 versioni.
- Pezzi tondi: una sola versione. Pezzi simmetrici (tappeto, tavolini, tavoli con sedie): r0 e r90.

## Mantenere la scala in Milanote
Milanote ridimensiona le immagini in base alla larghezza della card. Per restare in scala:
1. Imposta la pianta a una larghezza di riferimento (es. template PNG = 1884 px → 6,45 m + margini).
2. Ridimensiona ogni mobile con lo stesso rapporto; in alternativa verifica con la griglia:
   1 quadretto grande = 1 m, 1 quadretto piccolo = 50 cm.

`catalogo_arredi.svg/.png`: panoramica di tutti i pezzi con nome e misure.
