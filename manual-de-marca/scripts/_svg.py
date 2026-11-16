"""Utilidades compartidas: leer el SVG, medir formas en Chromium y renderizar.

Todas las medidas están en unidades del viewBox del SVG original (espacio raíz),
así que respetan las transformaciones de grupos anidados.
"""
import json
import re
import unicodedata
from pathlib import Path
from xml.etree import ElementTree as ET

SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"
ET.register_namespace("", SVG_NS)
ET.register_namespace("xlink", XLINK_NS)
SHAPES = ("path", "rect", "circle", "ellipse", "polygon", "polyline", "line", "text")
SKIP = ("defs", "style", "metadata", "title", "desc", "clipPath", "mask", "symbol", "pattern", "linearGradient", "radialGradient")


def slugify(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def tag(el):
    return el.tag.split("}")[-1]


def parse(path):
    return ET.parse(path).getroot()


def leaf_shapes(root):
    """Formas visibles en orden de documento (el mismo orden que querySelectorAll)."""
    out = []

    def walk(el):
        if tag(el) in SKIP:
            return
        if tag(el) in SHAPES:
            out.append(el)
        for ch in el:
            walk(ch)
    walk(root)
    return out


def to_text(root):
    return ET.tostring(root, encoding="unicode")


_MEASURE_JS = """() => {
  const s = document.querySelector('svg');
  const inv = s.getScreenCTM().inverse();
  const skip = new Set(['defs','clipPath','mask','symbol','pattern']);
  const els = [...s.querySelectorAll('path,rect,circle,ellipse,polygon,polyline,line,text')]
     .filter(e => { let p = e.parentElement; while (p && p !== s) { if (skip.has(p.tagName)) return false; p = p.parentElement; } return true; });
  return els.map(e => {
    const b = e.getBBox();
    const m = inv.multiply(e.getScreenCTM());
    const pts = [[b.x,b.y],[b.x+b.width,b.y],[b.x,b.y+b.height],[b.x+b.width,b.y+b.height]].map(([x,y]) =>
      [m.a*x + m.c*y + m.e, m.b*x + m.d*y + m.f]);
    const xs = pts.map(p=>p[0]), ys = pts.map(p=>p[1]);
    const cs = getComputedStyle(e);
    return {bbox:[Math.min(...xs), Math.min(...ys), Math.max(...xs)-Math.min(...xs), Math.max(...ys)-Math.min(...ys)],
            fill: cs.fill, stroke: cs.stroke, strokeWidth: cs.strokeWidth, opacity: cs.opacity, tag: e.tagName};
  });
}"""


def _page_html(svg_text, width=None, bg="transparent"):
    if width:
        svg_text = re.sub(r"<svg\b", f'<svg width="{width}"', svg_text, count=1)
    return (f"<html><body style='margin:0;background:{bg}'>"
            f"<div style='display:inline-block;line-height:0'>{svg_text}</div></body></html>")


def measure(svg_path_or_text):
    """Devuelve (formas, bbox_total). formas: lista de dicts con bbox y colores computados."""
    from playwright.sync_api import sync_playwright
    text = Path(svg_path_or_text).read_text(encoding="utf-8") if not str(svg_path_or_text).lstrip().startswith("<") else svg_path_or_text
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1200, "height": 1200})
        pg.set_content(_page_html(text, width=1000))
        shapes = pg.evaluate(_MEASURE_JS)
        b.close()
    # se conservan todas (también las vacías) para que los índices coincidan con leaf_shapes()
    boxes = [s["bbox"] for s in shapes if s["bbox"][2] > 0 or s["bbox"][3] > 0]
    if not boxes:
        raise SystemExit("No encontré formas en el SVG (¿está vacío o todo el contenido es una imagen incrustada?).")
    return shapes, union(boxes)


def union(boxes):
    x0 = min(b[0] for b in boxes); y0 = min(b[1] for b in boxes)
    x1 = max(b[0] + b[2] for b in boxes); y1 = max(b[1] + b[3] for b in boxes)
    return [x0, y0, x1 - x0, y1 - y0]


def rgb_to_hex(css):
    """'rgb(1, 2, 3)' -> '#010203'. Devuelve el texto tal cual si no es rgb (none, url(...))."""
    m = re.match(r"rgba?\((\d+),\s*(\d+),\s*(\d+)", css or "")
    if not m:
        return css
    return "#" + "".join(f"{int(v):02X}" for v in m.groups())


def set_viewbox(root, box, pad_ratio=0.0):
    x, y, w, h = box
    pad = max(w, h) * pad_ratio
    root.set("viewBox", f"{x - pad:.3f} {y - pad:.3f} {w + 2 * pad:.3f} {h + 2 * pad:.3f}")
    for a in ("width", "height", "x", "y"):
        root.attrib.pop(a, None)


def render_png(svg_text, out, width, bg=None):
    """Renderiza a PNG con el ancho dado. bg=None -> fondo transparente."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": max(int(width), 1), "height": 10})
        pg.set_content(_page_html(svg_text, width=int(width), bg=bg or "transparent"))
        el = pg.query_selector("div")
        el.screenshot(path=str(out), omit_background=bg is None)
        b.close()


def render_pdf(svg_text, out, width_mm=100):
    """PDF vectorial del SVG, con la página del tamaño del logo."""
    from playwright.sync_api import sync_playwright
    m = re.search(r'viewBox="([\d.\-e ]+)"', svg_text)
    _, _, w, h = (float(v) for v in m.group(1).split())
    height_mm = width_mm * h / w
    svg_sized = re.sub(r"<svg\b", f'<svg width="{width_mm}mm" height="{height_mm}mm"', svg_text, count=1)
    html = f"<html><head><style>@page{{size:{width_mm}mm {height_mm}mm;margin:0}}body{{margin:0}}</style></head><body>{svg_sized}</body></html>"
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.set_content(html)
        pg.pdf(path=str(out), width=f"{width_mm}mm", height=f"{height_mm}mm", print_background=False)
        b.close()


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def parse_groups(spec, n):
    """{"isotipo": [0,1,"3-5"], ...} -> {"isotipo": {0,1,3,4,5}}. "resto" toma lo no asignado."""
    out, used = {}, set()
    for name, items in spec.items():
        if items == "resto":
            continue
        idx = set()
        for it in items:
            if isinstance(it, str) and "-" in it:
                a, b = it.split("-"); idx |= set(range(int(a), int(b) + 1))
            else:
                idx.add(int(it))
        out[name] = idx; used |= idx
    for name, items in spec.items():
        if items == "resto":
            out[name] = set(range(n)) - used
    return out
