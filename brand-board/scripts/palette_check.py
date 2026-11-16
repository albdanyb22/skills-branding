#!/usr/bin/env python3
"""
Revisa la paleta para el brand board: qué color de texto y qué versión del logo
va sobre cada fondo, con su contraste WCAG.

    python palette_check.py paleta.json [--tinta "#1D1D1B"]

Para cada color imprime: contraste con tinta y con blanco, y la recomendación
(texto/logo en tinta o en blanco). Úsalo antes de asignar colores a las piezas:
un fondo donde ninguno de los dos llega a 4.5:1 sirve solo para titulares
grandes (≥ 3:1) o como acento, no como fondo de texto corrido.

paleta.json: [{"nombre": "Verde", "hex": "#20E064"}, ...]
"""
import argparse
import json
from pathlib import Path


def lum(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def ratio(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paleta")
    ap.add_argument("--tinta", default="#1D1D1B")
    a = ap.parse_args()
    pal = json.loads(Path(a.paleta).read_text(encoding="utf-8"))
    print(f"{'color':<14}{'hex':<10}{'vs tinta':>9}{'vs blanco':>10}   usar")
    for c in pal:
        rt, rw = ratio(c["hex"], a.tinta), ratio(c["hex"], "#FFFFFF")
        best = "tinta" if rt >= rw else "blanco"
        r = max(rt, rw)
        note = "" if r >= 4.5 else ("  (solo titulares grandes)" if r >= 3 else "  (solo acento)")
        print(f"{c['nombre']:<14}{c['hex']:<10}{rt:>9.1f}{rw:>10.1f}   {best}{note}")


if __name__ == "__main__":
    main()
