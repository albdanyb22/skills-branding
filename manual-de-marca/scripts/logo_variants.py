#!/usr/bin/env python3
"""
Genera variantes de COLOR del logo, solo las que la persona aprobó.

    python logo_variants.py logo.svg spec.json salida/ [--version horizontal]

spec.json:
{
  "grupos":   {"isotipo": [0, 1, "2-4"], "logotipo": "resto", "acento": [5]},
  "variantes": [
    {"nombre": "positivo",   "colores": {}},                       # colores originales
    {"nombre": "negativo",   "colores": {"*": "#FFFFFF", "acento": "#F8AE15"}},
    {"nombre": "monocromo",  "colores": {"*": "#1D1D1B"}},
    {"nombre": "grises",     "modo": "grises"},                    # luminancia de cada color original
    {"nombre": "sobre-azul", "colores": {"isotipo": "#F8AE15", "*": "#FFFFFF"}}
  ]
}
    {"nombre": "monocromo-calado", "colores": {"*": "#1D1D1B"}, "calar": ["punto"]}
"calar": grupos que se perforan (dejan ver el fondo). Úsalo cuando, al pasar a
un color, un detalle interior se fundiría con la forma de detrás.
"*" pinta todo lo que no tenga un grupo con color propio. Un grupo ausente
conserva su color original. Los degradados se reemplazan por color plano solo
donde la variante asigna un color.

Salida: salida/<version>_<variante>.svg (viewBox recortado al contenido, sin
<style> ni clases: cada forma con su fill explícito) y un PNG de vista previa de
cada una sobre un fondo de contraste, más salida/hoja_variantes.png con todas juntas.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import _svg  # noqa: E402


def lum(hexc):
    h = hexc.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    lin = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def gray(hexc):
    L = lum(hexc)
    v = 12.92 * L if L <= 0.0031308 else 1.055 * L ** (1 / 2.4) - 0.055
    g = round(v * 255)
    return f"#{g:02X}{g:02X}{g:02X}"


def knockout(root, leaves, calar, total):
    """Cala (perfora) las formas `calar`: dejan ver el fondo, sea del color que sea."""
    import copy
    from xml.etree import ElementTree as ET
    ns = "{%s}" % _svg.SVG_NS
    kids = [ch for ch in root if _svg.tag(ch) not in ("defs", "style", "metadata")]
    mask_root = copy.deepcopy(root)
    m_leaves = _svg.leaf_shapes(mask_root)
    m_par = {c: p for p in mask_root.iter() for c in p}
    for i, el in enumerate(m_leaves):
        if i in calar:
            el.set("fill", "#000000"); el.attrib.pop("stroke", None)
        else:
            m_par[el].remove(el)
    par = {c: p for p in root.iter() for c in p}
    for i, el in enumerate(leaves):
        if i in calar:
            par[el].remove(el)
    x, y, w, h = total
    mask = ET.Element(ns + "mask", {"id": "calado", "maskUnits": "userSpaceOnUse",
                                    "x": f"{x - w}", "y": f"{y - h}", "width": f"{3 * w}", "height": f"{3 * h}"})
    ET.SubElement(mask, ns + "rect", {"x": f"{x - w}", "y": f"{y - h}", "width": f"{3 * w}", "height": f"{3 * h}", "fill": "#FFFFFF"})
    for ch in mask_root:
        if _svg.tag(ch) not in ("defs", "style", "metadata", "mask"):
            mask.append(ch)
    defs = ET.Element(ns + "defs"); defs.append(mask)
    g = ET.Element(ns + "g", {"mask": "url(#calado)"})
    for ch in kids:
        root.remove(ch); g.append(ch)
    root.append(defs); root.append(g)


def preview_bg(colors):
    """Fondo de vista previa: oscuro si el logo es mayormente claro."""
    ls = [lum(c) for c in colors if c.startswith("#")]
    return "#2B2B2B" if ls and sum(ls) / len(ls) > 0.6 else "#FFFFFF"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("svg"); ap.add_argument("spec"); ap.add_argument("salida")
    ap.add_argument("--version", default="principal")
    a = ap.parse_args()
    spec = _svg.load_json(a.spec)
    out = Path(a.salida); out.mkdir(parents=True, exist_ok=True)
    shapes, total = _svg.measure(Path(a.svg).read_text(encoding="utf-8"))
    groups = _svg.parse_groups(spec.get("grupos", {}), len(shapes))
    orig = [_svg.rgb_to_hex(s["fill"]) for s in shapes]
    made = []
    for v in spec["variantes"]:
        root = _svg.parse(a.svg)
        leaves = _svg.leaf_shapes(root)
        # fijar fills computados antes de quitar estilos, para no perder colores de clases
        for el, c in zip(leaves, orig):
            if c.startswith("#"):
                el.set("fill", c)
        for el in root.iter():
            el.attrib.pop("class", None); el.attrib.pop("style", None)
        for parent in root.iter():
            for ch in list(parent):
                if _svg.tag(ch) in ("style", "metadata"):
                    parent.remove(ch)
        cols = v.get("colores", {})
        used = []
        for i, el in enumerate(leaves):
            if i >= len(orig):
                break
            c = None
            for g, idx in groups.items():
                if i in idx and g in cols:
                    c = cols[g]
            if c is None and "*" in cols:
                c = cols["*"]
            if v.get("modo") == "grises" and orig[i].startswith("#"):
                c = gray(orig[i])
            if c:
                el.set("fill", c)
            used.append(c or orig[i])
        calar = set().union(*(groups[g] for g in v.get("calar", [])))
        if calar:
            knockout(root, leaves, calar, total)
        _svg.set_viewbox(root, total, 0.0)
        root.attrib.pop("version", None)
        name = f"{_svg.slugify(a.version)}_{_svg.slugify(v['nombre'])}"
        text = _svg.to_text(root)
        (out / f"{name}.svg").write_text(text, encoding="utf-8")
        bg = v.get("fondo_preview") or preview_bg(used)
        pad_root = _svg.parse(out / f"{name}.svg"); _svg.set_viewbox(pad_root, total, 0.12)
        _svg.render_png(_svg.to_text(pad_root), out / f"{name}_preview.png", 800, bg=bg)
        made.append((name, bg))
    # hoja de contacto
    tiles = "".join(
        f"<div style='background:{bg};padding:24px;display:flex;flex-direction:column;gap:12px;align-items:center'>"
        f"<img src='{n}_preview.png' style='width:360px'><div style='font:14px sans-serif;color:{'#fff' if lum(bg) < 0.4 else '#333'}'>{n}</div></div>"
        for n, bg in made)
    html = f"<html><body style='margin:0;display:grid;grid-template-columns:repeat(3,408px);gap:8px;background:#ddd;padding:8px'>{tiles}</body></html>"
    from playwright.sync_api import sync_playwright
    (out / "_hoja.html").write_text(html, encoding="utf-8")
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1250, "height": 400})
        pg.goto((out / "_hoja.html").resolve().as_uri()); pg.screenshot(path=str(out / "hoja_variantes.png"), full_page=True); b.close()
    (out / "_hoja.html").unlink()
    print("Generadas:", ", ".join(n + ".svg" for n, _ in made))
    print("Hoja:", out / "hoja_variantes.png")


if __name__ == "__main__":
    main()
