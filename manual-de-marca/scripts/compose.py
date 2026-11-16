#!/usr/bin/env python3
"""
Recompone el logo (horizontal <-> vertical, isotipo solo, sin tagline, avatar)
SIN redibujar: cada grupo se copia tal cual y solo se reubica, escala o separa.
Úsalo únicamente después de que la persona dijo que no tiene ese SVG, y muestra
la vista previa para que la apruebe antes de usarla en el manual.

    python compose.py logo.svg spec.json salida/nombre

spec.json (ejemplos):
  {"grupos": {"isotipo": [0, 1, 2], "logotipo": "resto"},
   "layout": "vertical", "orden": ["isotipo", "logotipo"],
   "modulo": 12.5, "separacion": 2, "alinear": "centro",
   "escala": {"logotipo": 1.0}}

  {"grupos": {...}, "layout": "horizontal", "orden": ["isotipo", "logotipo"],
   "modulo": 12.5, "separacion": 1.5, "alinear": "centro"}

  {"grupos": {...}, "layout": "solo", "orden": ["isotipo"]}          # isotipo solo / sin tagline

  {"grupos": {...}, "layout": "avatar", "orden": ["isotipo"],
   "margen": 0.2, "fondo": "#172AF0"}                                   # recorte circular

- modulo: la unidad del plano constructivo, en unidades del viewBox original.
- separacion: espacio entre grupos, en módulos (si no hay módulo, en % del alto mayor).
- alinear: centro | inicio | fin | base (eje transversal). "base" (solo horizontal)
  alinea las líneas base de las letras: pasa "base": {"grupo": y_linea_base} con la
  y de la línea base de cada grupo en el SVG original (el pie de una letra sin
  descendente: n, m, l…, que svg_inspect muestra como y + alto).
- escala: factor por grupo respecto a su tamaño original (por defecto 1).
- externos: {"slogan": "slogan.svg"} suma piezas de otros SVG (por ejemplo, un
  texto en contornos de text_to_svg.py) que se usan como un grupo más en "orden".
- ancho: {"slogan": "logo"} iguala el ancho de una pieza al de otro grupo (o a un
  número de unidades); útil para lock-ups con slogan o nombre de edificio.
- avatar: margen = fracción del diámetro que queda libre a cada lado del grupo;
  genera además <nombre>_circulo.png para comprobar el recorte.

Salida: <nombre>.svg y <nombre>_preview.png.
"""
import argparse
import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import _svg  # noqa: E402


def group_svg(root_src, keep, box, x, y, s):
    """<svg> anidado con todo el documento original pero solo las formas `keep`."""
    root = copy.deepcopy(root_src)
    if keep is not None:
        leaves = _svg.leaf_shapes(root)
        parents = {c: p for p in root.iter() for c in p}
        for i, el in enumerate(leaves):
            if i not in keep:
                parents[el].remove(el)
    bx, by, bw, bh = box
    inner = "".join(_svg.to_text(ch) for ch in root)
    return (f'<svg x="{x:.3f}" y="{y:.3f}" width="{bw * s:.3f}" height="{bh * s:.3f}" '
            f'viewBox="{bx:.3f} {by:.3f} {bw:.3f} {bh:.3f}" overflow="visible">{inner}</svg>')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("svg"); ap.add_argument("spec"); ap.add_argument("salida")
    a = ap.parse_args()
    spec = _svg.load_json(a.spec)
    out = Path(a.salida); out.parent.mkdir(parents=True, exist_ok=True)
    raw = Path(a.svg).read_text(encoding="utf-8")
    shapes, _ = _svg.measure(raw)
    groups = _svg.parse_groups(spec["grupos"], len(shapes))
    root = _svg.parse(a.svg)
    order = spec["orden"]
    esc = spec.get("escala", {})
    ext = spec.get("externos", {})
    anchos = spec.get("ancho", {})
    items = []
    for g in order:
        if g in ext:  # pieza de otro SVG (slogan, nombre de edificio): se usa entera, con su viewBox
            eroot = _svg.parse(ext[g])
            box = [float(v) for v in eroot.get("viewBox").split()]
            items.append({"g": g, "idx": None, "root": eroot, "box": box, "s": float(esc.get(g, 1.0))})
        else:
            idx = groups[g]
            box = _svg.union([shapes[i]["bbox"] for i in idx if shapes[i]["bbox"][2] or shapes[i]["bbox"][3]])
            items.append({"g": g, "idx": idx, "root": root, "box": box, "s": float(esc.get(g, 1.0))})
    for it in items:  # "ancho": {"slogan": "logo"} iguala el ancho al de otro grupo, o a un número de unidades
        if it["g"] in anchos:
            target = anchos[it["g"]]
            tw = next(o["box"][2] * o["s"] for o in items if o["g"] == target) if isinstance(target, str) else float(target)
            it["s"] = tw / it["box"][2]
    layout = spec.get("layout", "vertical")
    maxh = max(it["box"][3] * it["s"] for it in items)
    unit = spec.get("modulo") or maxh / 100 * 10
    gap = float(spec.get("separacion", 1)) * unit
    align = spec.get("alinear", "centro")
    parts = []

    def cross(total, size):
        return {"inicio": 0, "fin": total - size}.get(align, (total - size) / 2)

    if layout == "vertical":
        W = max(it["box"][2] * it["s"] for it in items)
        y = 0
        for it in items:
            w, h = it["box"][2] * it["s"], it["box"][3] * it["s"]
            parts.append(group_svg(it["root"], it["idx"], it["box"], cross(W, w), y, it["s"])); y += h + gap
        W, H = W, y - gap
    elif layout == "horizontal" and align == "base":
        bases = spec["base"]
        above = max((bases[it["g"]] - it["box"][1]) * it["s"] for it in items)   # parte sobre la línea base
        below = max((it["box"][1] + it["box"][3] - bases[it["g"]]) * it["s"] for it in items)
        H = above + below
        x = 0
        for it in items:
            w = it["box"][2] * it["s"]
            y = above - (bases[it["g"]] - it["box"][1]) * it["s"]
            parts.append(group_svg(it["root"], it["idx"], it["box"], x, y, it["s"])); x += w + gap
        W = x - gap
    elif layout == "horizontal":
        H = max(it["box"][3] * it["s"] for it in items)
        x = 0
        for it in items:
            w, h = it["box"][2] * it["s"], it["box"][3] * it["s"]
            parts.append(group_svg(it["root"], it["idx"], it["box"], x, cross(H, h), it["s"])); x += w + gap
        W, H = x - gap, H
    elif layout in ("solo", "avatar"):
        it = items[0]
        w, h = it["box"][2] * it["s"], it["box"][3] * it["s"]
        if layout == "solo":
            W, H = w, h
            parts.append(group_svg(it["root"], it["idx"], it["box"], 0, 0, it["s"]))
        else:
            m = float(spec.get("margen", 0.2))
            D = max(w, h) / (1 - 2 * m)
            W = H = D
            bg = spec.get("fondo")
            if bg:
                parts.append(f'<rect x="0" y="0" width="{D:.3f}" height="{D:.3f}" fill="{bg}"/>')
            parts.append(group_svg(it["root"], it["idx"], it["box"], (D - w) / 2, (D - h) / 2, it["s"]))
    else:
        raise SystemExit(f"layout desconocido: {layout}")

    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
           f'viewBox="0 0 {W:.3f} {H:.3f}">{"".join(parts)}</svg>')
    Path(f"{out}.svg").write_text(svg, encoding="utf-8")
    pad = max(W, H) * 0.12
    prev = svg.replace(f'viewBox="0 0 {W:.3f} {H:.3f}"', f'viewBox="{-pad:.3f} {-pad:.3f} {W + 2 * pad:.3f} {H + 2 * pad:.3f}"', 1)
    _svg.render_png(prev, f"{out}_preview.png", 900, bg="#FFFFFF")
    if layout == "avatar":
        circ = svg.replace("<svg ", '<svg style="border-radius:50%;overflow:hidden" ', 1)
        html_bg = "#E9E9E9"
        _svg.render_png(circ, f"{out}_circulo.png", 400, bg=html_bg)
    print(f"{out}.svg · proporción {W / H:.3f} · vista previa {out}_preview.png")


if __name__ == "__main__":
    main()
