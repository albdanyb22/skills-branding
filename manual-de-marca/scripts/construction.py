#!/usr/bin/env python3
"""
Plano constructivo y área de protección. Úsalo SOLO si la persona no tiene
retícula propia (primero se le pide su SVG de retícula).

1) Candidatos a módulo (unidad de medida tomada del propio logo):
     python construction.py candidatos logo.svg salida/ [--grupos grupos.json]
   Mide: el elemento más pequeño (punto o trazo), el grosor típico del trazo y
   la altura típica de las letras del logotipo. Genera salida/candidato_<n>.png
   con la retícula de cada candidato sobre el logo, para mostrarlos y elegir.

2) Plano y área de protección con el módulo elegido:
     python construction.py plano logo.svg salida/nombre --modulo 12.5 --proteccion 2 \
         [--color-reticula "#9AA0A6"] [--marcar 5]
   Genera nombre_plano.svg/.png (retícula + medidas en módulos) y
   nombre_proteccion.svg/.png (área de protección con las X). --marcar resalta
   la forma de la que sale el módulo (índice de svg_inspect).
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import _svg  # noqa: E402


def logo_inner(path):
    root = _svg.parse(path)
    return "".join(_svg.to_text(ch) for ch in root)


def stroke_thickness(path, total):
    """Grosor típico del trazo (mediana de la cresta de la transformada de distancia)."""
    import numpy as np
    from PIL import Image
    from scipy import ndimage
    root = _svg.parse(path); _svg.set_viewbox(root, total, 0.02)
    tmp = Path(path).with_suffix(".tmp_mask.png")
    W = 3000
    _svg.render_png(_svg.to_text(root), tmp, W)
    a = np.array(Image.open(tmp).convert("RGBA"))[..., 3] > 128
    tmp.unlink()
    d = ndimage.distance_transform_edt(a)
    ridge = (d == ndimage.maximum_filter(d, size=3)) & (d > 1.5)
    if not ridge.any():
        return None
    px_per_unit = W / (total[2] * 1.04)
    return float(np.median(d[ridge]) * 2 / px_per_unit)


def grid_svg(total, mod, prot, inner, color, mark_box=None, labels=True):
    x, y, w, h = total
    P = prot * mod
    X0, Y0, X1, Y1 = x - P - mod * 1.8, y - P - mod, x + w + P + mod, y + h + P + mod
    sw = max(w, h) / 900
    lines = []
    k = 0
    gx = x - P
    while gx <= x + w + P + 1e-6:
        lines.append(f'<line x1="{gx:.3f}" y1="{y - P:.3f}" x2="{gx:.3f}" y2="{y + h + P:.3f}"/>'); gx += mod; k += 1
    gy = y - P
    while gy <= y + h + P + 1e-6:
        lines.append(f'<line x1="{x - P:.3f}" y1="{gy:.3f}" x2="{x + w + P:.3f}" y2="{gy:.3f}"/>'); gy += mod
    g = f'<g stroke="{color}" stroke-width="{sw:.3f}" opacity="0.55">{"".join(lines)}</g>'
    box = (f'<rect x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" fill="none" stroke="#E5484D" stroke-width="{sw * 1.6:.3f}"/>'
           f'<rect x="{x - P:.3f}" y="{y - P:.3f}" width="{w + 2 * P:.3f}" height="{h + 2 * P:.3f}" fill="none" '
           f'stroke="#E5484D" stroke-width="{sw * 1.6:.3f}" stroke-dasharray="{sw * 8:.3f} {sw * 6:.3f}"/>')
    mk = ""
    if mark_box:
        bx, by, bw, bh = mark_box
        mk = f'<rect x="{bx:.3f}" y="{by:.3f}" width="{bw:.3f}" height="{bh:.3f}" fill="#E5484D" fill-opacity="0.25" stroke="#E5484D" stroke-width="{sw * 2:.3f}"/>'
    txt = ""
    if labels:
        fs = mod * 0.9 if mod * 0.9 > h / 30 else h / 30
        txt = (f'<g font-family="sans-serif" font-size="{fs:.3f}" fill="#E5484D" text-anchor="middle">'
               f'<text x="{x + w / 2:.3f}" y="{y + h + P + mod * 0.85:.3f}">{w / mod:.1f} módulos</text>'
               f'<text x="{x - P - mod * 0.35:.3f}" y="{y + h / 2:.3f}" transform="rotate(-90 {x - P - mod * 0.35:.3f} {y + h / 2:.3f})">{h / mod:.1f} módulos</text></g>')
    vb = f"{X0:.3f} {Y0:.3f} {X1 - X0:.3f} {Y1 - Y0 + mod * 0.6:.3f}"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="{vb}">'
            f'<rect x="{X0:.3f}" y="{Y0:.3f}" width="{X1 - X0:.3f}" height="{Y1 - Y0 + mod:.3f}" fill="#FFFFFF"/>{g}{inner}{box}{mk}{txt}</svg>')


def protection_svg(total, mod, prot, inner):
    x, y, w, h = total
    P = prot * mod
    sw = max(w, h) / 700
    pad = mod * 0.8
    X0, Y0 = x - P - pad, y - P - pad
    xs = []
    fs = P * 0.55
    for cx, cy in [(x - P / 2, y + h / 2), (x + w + P / 2, y + h / 2), (x + w / 2, y - P / 2), (x + w / 2, y + h + P / 2)]:
        xs.append(f'<text x="{cx:.3f}" y="{cy:.3f}" font-size="{fs:.3f}" text-anchor="middle" dominant-baseline="central" '
                  f'font-family="sans-serif" font-weight="700" fill="#E5484D">X</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'viewBox="{X0:.3f} {Y0:.3f} {w + 2 * (P + pad):.3f} {h + 2 * (P + pad):.3f}">'
            f'<rect x="{x - P:.3f}" y="{y - P:.3f}" width="{w + 2 * P:.3f}" height="{h + 2 * P:.3f}" fill="#E5484D" fill-opacity="0.08" '
            f'stroke="#E5484D" stroke-width="{sw:.3f}" stroke-dasharray="{sw * 6:.3f} {sw * 4:.3f}"/>{inner}{"".join(xs)}</svg>')


def candidatos(a):
    out = Path(a.salida); out.mkdir(parents=True, exist_ok=True)
    shapes, total = _svg.measure(Path(a.svg).read_text(encoding="utf-8"))
    groups = _svg.parse_groups(_svg.load_json(a.grupos), len(shapes)) if a.grupos else {}
    x, y, w, h = total
    cands = []
    real = [(i, s["bbox"]) for i, s in enumerate(shapes) if min(s["bbox"][2], s["bbox"][3]) > h * 0.01]
    i_min, b_min = min(real, key=lambda t: max(t[1][2], t[1][3]))
    cands.append(("elemento más pequeño (forma %d)" % i_min, max(b_min[2], b_min[3]), b_min))
    letters = groups.get("logotipo")
    pool = [shapes[i]["bbox"] for i in letters] if letters else [b for _, b in real]
    hs = sorted(b[3] for b in pool)
    med = hs[len(hs) // 2]
    ref = min(pool, key=lambda b: abs(b[3] - med))
    cands.append(("altura típica de letra" if letters else "altura típica de forma", med, ref))
    t = stroke_thickness(a.svg, total)
    if t:
        cands.append(("grosor del trazo", t, None))
    inner = logo_inner(a.svg)
    print(f"Logo: {w:.1f} × {h:.1f} unidades")
    for n, (name, mod, mbox) in enumerate(cands, 1):
        svg = grid_svg(total, mod, 0, inner, "#4363D8", mark_box=mbox)
        _svg.render_png(svg, out / f"candidato_{n}.png", 1400, bg="#FFFFFF")
        print(f"{n}. {name}: módulo = {mod:.2f} u → logo de {w / mod:.1f} × {h / mod:.1f} módulos · {out / f'candidato_{n}.png'}")


def plano(a):
    out = Path(a.salida); out.parent.mkdir(parents=True, exist_ok=True)
    shapes, total = _svg.measure(Path(a.svg).read_text(encoding="utf-8"))
    inner = logo_inner(a.svg)
    mb = shapes[a.marcar]["bbox"] if a.marcar is not None else None
    s1 = grid_svg(total, a.modulo, a.proteccion, inner, a.color_reticula, mark_box=mb)
    Path(f"{out}_plano.svg").write_text(s1, encoding="utf-8")
    _svg.render_png(s1, f"{out}_plano.png", 1800, bg="#FFFFFF")
    s2 = protection_svg(total, a.modulo, a.proteccion, inner)
    Path(f"{out}_proteccion.svg").write_text(s2, encoding="utf-8")
    _svg.render_png(s2, f"{out}_proteccion.png", 1800, bg="#FFFFFF")
    x, y, w, h = total
    print(f"Logo = {w / a.modulo:.1f} × {h / a.modulo:.1f} módulos; protección = {a.proteccion} módulos por lado")
    print(f"{out}_plano.png · {out}_proteccion.png")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("candidatos"); c.add_argument("svg"); c.add_argument("salida"); c.add_argument("--grupos")
    p = sub.add_parser("plano"); p.add_argument("svg"); p.add_argument("salida")
    p.add_argument("--modulo", type=float, required=True); p.add_argument("--proteccion", type=float, default=1)
    p.add_argument("--color-reticula", default="#9AA0A6"); p.add_argument("--marcar", type=int)
    a = ap.parse_args()
    {"candidatos": candidatos, "plano": plano}[a.cmd](a)


if __name__ == "__main__":
    main()
