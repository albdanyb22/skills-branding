#!/usr/bin/env python3
"""
Genera las imágenes de "Usos incorrectos" con el logo real (no con un dibujo
aproximado), cada una con su X roja.

    python incorrect_uses.py logo.svg salida/ --grupos grupos.json --nombre "Mi Marca" \
        [--color-falso "#E5484D"] [--fondo-malo "#F8AE15"]

Genera en salida/: deformar.png, rotar.png, recolorear.png, tipografia.png,
proporciones.png, sombra.png, contorno.png, contraste.png y hoja_incorrectos.png.
- tipografia: el isotipo con el nombre escrito en una fuente genérica.
- proporciones: el isotipo agrandado 1,4× respecto al logotipo.
- contraste: el logo positivo sobre --fondo-malo (elige un color de la paleta
  con poco contraste según color_system.py).
Si el logo no tiene isotipo (solo logotipo), tipografia y proporciones se omiten.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import _svg  # noqa: E402
from compose import group_svg  # noqa: E402

X = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" style="position:absolute;right:14px;top:14px;width:44px">'
     '<circle cx="50" cy="50" r="46" fill="#E5484D"/><path d="M32 32 68 68M68 32 32 68" stroke="#fff" stroke-width="11" stroke-linecap="round"/></svg>')


def tile(svg_inner, vb, out, bg="#FFFFFF", css=""):
    from playwright.sync_api import sync_playwright
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="{vb}" style="width:420px;height:260px;{css}">{svg_inner}</svg>'
    html = (f"<html><body style='margin:0'><div style='position:relative;width:520px;height:340px;background:{bg};"
            f"display:flex;align-items:center;justify-content:center;overflow:hidden'>{svg}{X}</div></body></html>")
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 520, "height": 340})
        pg.set_content(html); pg.screenshot(path=str(out)); b.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("svg"); ap.add_argument("salida")
    ap.add_argument("--grupos", required=True); ap.add_argument("--nombre", required=True)
    ap.add_argument("--color-falso", default="#E5484D"); ap.add_argument("--fondo-malo", default="#F8AE15")
    a = ap.parse_args()
    out = Path(a.salida); out.mkdir(parents=True, exist_ok=True)
    raw = Path(a.svg).read_text(encoding="utf-8")
    shapes, total = _svg.measure(raw)
    groups = _svg.parse_groups(_svg.load_json(a.grupos), len(shapes))
    root = _svg.parse(a.svg)
    inner = "".join(_svg.to_text(ch) for ch in root)
    x, y, w, h = total
    p = max(w, h) * 0.08
    vb = f"{x - p:.2f} {y - p:.2f} {w + 2 * p:.2f} {h + 2 * p:.2f}"
    cx, cy = x + w / 2, y + h / 2
    made = []

    def save(name, *args, **kw):
        tile(*args, **kw, out=out / f"{name}.png"); made.append(name)

    made.append("deformar")  # estirado real: preserveAspectRatio="none"
    s = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" preserveAspectRatio="none" style="width:440px;height:150px">{inner}</svg>'
    tile_html = s
    from playwright.sync_api import sync_playwright  # deformar: estirado real
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page(viewport={"width": 520, "height": 340})
        pg.set_content(f"<html><body style='margin:0'><div style='position:relative;width:520px;height:340px;background:#fff;display:flex;align-items:center;justify-content:center'>{tile_html}{X}</div></body></html>")
        pg.screenshot(path=str(out / "deformar.png")); b.close()
    save("rotar", f'<g transform="rotate(-18 {cx:.2f} {cy:.2f})">{inner}</g>', vb)
    rec = _svg.parse(a.svg)
    for el in rec.iter():
        el.attrib.pop("class", None); el.attrib.pop("style", None)
    for el in _svg.leaf_shapes(rec):
        el.set("fill", a.color_falso)
    save("recolorear", "".join(_svg.to_text(ch) for ch in rec if _svg.tag(ch) != "style"), vb)
    iso = groups.get("isotipo")
    if iso:
        ib = _svg.union([shapes[i]["bbox"] for i in iso])
        rest = set(range(len(shapes))) - iso
        rb = _svg.union([shapes[i]["bbox"] for i in rest]) if rest else None
        fs = (rb[3] if rb else ib[3]) * 0.9
        tx = (rb[0] if rb else ib[0] + ib[2] * 1.2)
        ty = (rb[1] + rb[3] if rb else cy)
        txt = (f'<text x="{tx:.2f}" y="{ty:.2f}" font-family="Times New Roman, serif" font-style="italic" '
               f'font-size="{fs:.2f}" fill="{shapes[min(rest)]["fill"] if rest else "#333"}">{a.nombre}</text>')
        save("tipografia", group_svg(root, iso, ib, ib[0], ib[1], 1) + txt, vb)
        if rest:
            k = 1.4
            big = group_svg(root, iso, ib, ib[0] - ib[2] * (k - 1) / 2, ib[1] - ib[3] * (k - 1) / 2, k)
            save("proporciones", big + group_svg(root, rest, rb, rb[0], rb[1], 1), vb)
    d = max(w, h) * 0.02
    save("sombra", f'<defs><filter id="sh" x="-20%" y="-20%" width="140%" height="160%"><feDropShadow dx="{d:.2f}" dy="{d:.2f}" stdDeviation="{d * 0.8:.2f}" flood-opacity="0.55"/></filter></defs><g filter="url(#sh)">{inner}</g>', vb)
    con = _svg.parse(a.svg)
    for el in _svg.leaf_shapes(con):
        el.set("stroke", "#1D1D1B"); el.set("stroke-width", f"{max(w, h) * 0.008:.2f}")
    save("contorno", "".join(_svg.to_text(ch) for ch in con), vb)
    save("contraste", inner, vb, bg=a.fondo_malo)
    tiles = "".join(f"<div><img src='{n}.png' style='width:260px;display:block'><div style='font:13px sans-serif;padding:6px 0 0'>{n}</div></div>" for n in made)
    (out / "_h.html").write_text(f"<html><body style='margin:0;padding:10px;display:grid;grid-template-columns:repeat(4,260px);gap:12px;background:#eee'>{tiles}</body></html>", encoding="utf-8")
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page(viewport={"width": 1110, "height": 300})
        pg.goto((out / "_h.html").resolve().as_uri()); pg.screenshot(path=str(out / "hoja_incorrectos.png"), full_page=True); b.close()
    (out / "_h.html").unlink()
    print("Generados:", ", ".join(m + ".png" for m in made), "·", out / "hoja_incorrectos.png")


if __name__ == "__main__":
    main()
