#!/usr/bin/env python3
"""
Convierte un texto en contornos SVG con una fuente real (con kerning), para
slogans, nombres de sub-marca o de edificio que acompañan al logo. Así el SVG
entregado no depende de que el proveedor tenga la fuente instalada.

    python text_to_svg.py "Conecta. Vive. Pertenece." fuente.woff salida.svg \
        [--color "#1D1D1B"] [--tracking 0]

- fuente: .ttf, .otf o .woff (no .woff2 si falta el módulo brotli).
- tracking: espaciado extra en milésimas de em (como en Illustrator).
Las fuentes de Google Fonts se obtienen con npm:  npm i @fontsource/<familia>
(los archivos quedan en node_modules/@fontsource/<familia>/files/).

Requiere fontTools y uharfbuzz (pip install --break-system-packages uharfbuzz).
El SVG sale en unidades de la fuente (1 em = unitsPerEm) con el viewBox
ajustado a la caja tipográfica: de la altura de mayúsculas a la línea base, y
el descendente si el texto lo tiene. La línea base queda en y = 0.
"""
import argparse
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("texto"); ap.add_argument("fuente"); ap.add_argument("salida")
    ap.add_argument("--color", default="#1D1D1B")
    ap.add_argument("--tracking", type=float, default=0)
    a = ap.parse_args()
    import uharfbuzz as hb
    from fontTools.pens.boundsPen import BoundsPen
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    from fontTools.ttLib import TTFont
    data = Path(a.fuente).read_bytes()
    font = TTFont(a.fuente)
    if a.fuente.endswith((".woff", ".woff2")):
        import io
        buf = io.BytesIO(); font.flavor = None; font.save(buf); data = buf.getvalue(); font = TTFont(io.BytesIO(data))
    upem = font["head"].unitsPerEm
    face = hb.Face(data); hbfont = hb.Font(face)
    buf = hb.Buffer(); buf.add_str(a.texto); buf.guess_segment_properties()
    hb.shape(hbfont, buf, {"kern": True, "liga": True})
    gs = font.getGlyphSet(); order = font.getGlyphOrder()
    pen = SVGPathPen(gs); bpen = BoundsPen(gs)
    x = 0
    track = a.tracking / 1000 * upem
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        name = order[info.codepoint]
        t = (1, 0, 0, -1, x + pos.x_offset, -pos.y_offset)   # SVG: y hacia abajo
        gs[name].draw(TransformPen(pen, t)); gs[name].draw(TransformPen(bpen, t))
        x += pos.x_advance + track
    x -= track
    os2 = font["OS/2"]
    cap = getattr(os2, "sCapHeight", 0) or upem * 0.7
    x0, y0, x1, y1 = bpen.bounds
    top = min(y0, -cap); bottom = max(y1, 0)
    vb = f"{min(0, x0):.1f} {top:.1f} {max(x, x1) - min(0, x0):.1f} {bottom - top:.1f}"
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">'
           f'<path fill="{a.color}" d="{pen.getCommands()}"/></svg>')
    Path(a.salida).write_text(svg, encoding="utf-8")
    print(f"{a.salida} · ancho {max(x, x1):.0f} u · altura de mayúsculas {cap} u · upem {upem}")


if __name__ == "__main__":
    main()
