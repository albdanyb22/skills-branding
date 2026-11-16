#!/usr/bin/env python3
"""
Variantes de color de un logo SVG para el brand board.

1) Inspeccionar (qué elementos tiene el logo y cuál es cuál):
     python logo_variants.py inspect logo.svg salida_dir/
   -> salida_dir/inspeccion.png: el logo con cada elemento numerado y coloreado
      distinto, y una tabla en consola (índice, tamaño, posición).

2) Generar variantes:
     python logo_variants.py build logo.svg paleta.json salida_dir/ \
         --acento 0,1,2 [--prefijo logo] [--tinta "#1D1D1B"]
   - Los elementos de --acento toman el color de cada entrada de la paleta;
     el resto queda en tinta. Sin --acento, el logo entero toma cada color.
   - Siempre genera además <prefijo>-tinta.svg (todo en tinta) y
     <prefijo>-blanco.svg (todo en blanco) para fondos de color.
   - Recorta el viewBox al contenido real (con un margen del 2%).
   - El SVG de salida no lleva <style> (el lienzo de diseño lo exige): cada
     forma lleva su `fill` directo.

paleta.json: [{"nombre": "Verde", "slug": "verde", "hex": "#20E064"}, ...]
(slug opcional: se deriva del nombre).

Requiere playwright (Chromium) para medir el contenido.
"""
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from xml.etree import ElementTree as ET

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)
SHAPES = {"path", "rect", "circle", "ellipse", "polygon", "polyline", "line", "text"}


def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def tag(el):
    return el.tag.split("}")[-1]


def leaf_shapes(root):
    """Formas en orden de documento (ignora <defs>, <style>, metadatos)."""
    out = []

    def walk(el, skip=False):
        t = tag(el)
        if t in ("defs", "style", "metadata", "title", "desc", "clipPath", "mask"):
            return
        if t in SHAPES:
            out.append(el)
        for ch in el:
            walk(ch)
    walk(root)
    return out


def strip_styles(root):
    """Quita <style>, class y style= ; deja fill explícito."""
    for parent in root.iter():
        for ch in list(parent):
            if tag(ch) in ("style", "metadata"):
                parent.remove(ch)
    for el in root.iter():
        el.attrib.pop("class", None)
        el.attrib.pop("style", None)
        el.attrib.pop("id", None)


def measure(svg_text, n):
    """bbox por forma y bbox total, medidos en Chromium."""
    from playwright.sync_api import sync_playwright
    html = f"<html><body style='margin:0'>{svg_text}</body></html>"
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.set_content(html)
        boxes = pg.evaluate("""() => {
          const s = document.querySelector('svg');
          const els = [...s.querySelectorAll('path,rect,circle,ellipse,polygon,polyline,line,text')];
          return els.map(e => { const r = e.getBBox(); return [r.x, r.y, r.width, r.height]; });
        }""")
        b.close()
    if not boxes:
        sys.exit("No encontré formas en el SVG.")
    x0 = min(b[0] for b in boxes); y0 = min(b[1] for b in boxes)
    x1 = max(b[0] + b[2] for b in boxes); y1 = max(b[1] + b[3] for b in boxes)
    return boxes, (x0, y0, x1 - x0, y1 - y0)


def load(path):
    tree = ET.parse(path)
    root = tree.getroot()
    strip_styles(root)
    return root


def to_text(root):
    return ET.tostring(root, encoding="unicode")


def inspect(args):
    root = load(args.svg)
    shapes = leaf_shapes(root)
    boxes, total = measure(to_text(root), len(shapes))
    hues = ["#E6194B", "#3CB44B", "#4363D8", "#F58231", "#911EB4", "#42D4F4", "#F032E6", "#BFEF45", "#469990", "#9A6324"]
    for i, el in enumerate(shapes):
        el.set("fill", hues[i % len(hues)])
    x, y, w, h = total
    pad = max(w, h) * 0.04
    root.set("viewBox", f"{x - pad:.2f} {y - pad:.2f} {w + 2 * pad:.2f} {h + 2 * pad:.2f}")
    root.attrib.pop("width", None); root.attrib.pop("height", None)
    labels = "".join(
        f"<text x='{b[0] + b[2] / 2:.1f}' y='{b[1] + b[3] / 2:.1f}' font-size='{max(w, h) * 0.035:.1f}' "
        f"text-anchor='middle' dominant-baseline='middle' font-family='sans-serif' font-weight='700' "
        f"fill='#000' stroke='#fff' stroke-width='{max(w, h) * 0.006:.1f}' paint-order='stroke'>{i}</text>"
        for i, b in enumerate(boxes))
    svg = to_text(root).replace("</svg>", labels + "</svg>")
    out = Path(args.salida); out.mkdir(parents=True, exist_ok=True)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1000, "height": int(1000 * (h + 2 * pad) / (w + 2 * pad)) + 1})
        pg.set_content(f"<html><body style='margin:0;background:#fff'>{svg.replace('<svg', '<svg width=\"1000\"', 1)}</body></html>")
        pg.screenshot(path=str(out / "inspeccion.png"))
        b.close()
    print(f"{len(shapes)} formas. Imagen: {out / 'inspeccion.png'}")
    print("idx  x       y       ancho   alto")
    for i, bx in enumerate(boxes):
        print(f"{i:<4} {bx[0]:<7.0f} {bx[1]:<7.0f} {bx[2]:<7.0f} {bx[3]:<7.0f}")


def build(args):
    pal = json.loads(Path(args.paleta).read_text(encoding="utf-8"))
    acc = {int(i) for i in args.acento.split(",")} if args.acento else None
    out = Path(args.salida); out.mkdir(parents=True, exist_ok=True)
    base = load(args.svg)
    boxes, (x, y, w, h) = measure(to_text(base), 0)
    pad = max(w, h) * 0.02
    vb = f"{x - pad:.2f} {y - pad:.2f} {w + 2 * pad:.2f} {h + 2 * pad:.2f}"

    def variant(fill_acc, fill_rest, name):
        root = load(args.svg)
        for i, el in enumerate(leaf_shapes(root)):
            el.set("fill", fill_acc if (acc is None or i in acc) else fill_rest)
        root.set("viewBox", vb)
        root.attrib.pop("width", None); root.attrib.pop("height", None)
        root.attrib.pop("version", None)
        (out / f"{name}.svg").write_text(to_text(root), encoding="utf-8")
        return name

    made = []
    for c in pal:
        s = c.get("slug") or slugify(c["nombre"])
        made.append(variant(c["hex"], args.tinta, f"{args.prefijo}-{s}"))
    made.append(variant(args.tinta, args.tinta, f"{args.prefijo}-tinta"))
    made.append(variant("#FFFFFF", "#FFFFFF", f"{args.prefijo}-blanco"))
    print("Generados:", ", ".join(m + ".svg" for m in made))
    print(f"Proporción (ancho/alto): {(w + 2 * pad) / (h + 2 * pad):.3f}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("inspect"); a.add_argument("svg"); a.add_argument("salida")
    b = sub.add_parser("build"); b.add_argument("svg"); b.add_argument("paleta"); b.add_argument("salida")
    b.add_argument("--acento", default=None, help="índices de formas que toman el color (ver inspect)")
    b.add_argument("--prefijo", default="logo")
    b.add_argument("--tinta", default="#1D1D1B")
    args = ap.parse_args()
    {"inspect": inspect, "build": build}[args.cmd](args)


if __name__ == "__main__":
    main()
