#!/usr/bin/env python3
"""
Analiza el logo SVG antes de proponer cualquier versión.

    python svg_inspect.py logo.svg salida/

Genera:
  salida/inspeccion.png  el logo con cada forma numerada y pintada de un color distinto
  salida/original.png    el logo tal cual, a 1000 px
  salida/formas.json     por forma: índice, bbox (en unidades del viewBox), fill, stroke
Imprime: número de formas, colores únicos (con cuántas formas usa cada uno),
proporción ancho/alto, y alertas (degradados, trazos sin expandir, texto vivo,
imágenes incrustadas). Con esto propones los grupos isotipo / logotipo / tagline
y se los confirmas a la persona antes de seguir.
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import _svg  # noqa: E402

HUES = ["#E6194B", "#3CB44B", "#4363D8", "#F58231", "#911EB4", "#42D4F4", "#F032E6",
        "#9A6324", "#469990", "#800000", "#808000", "#000075"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("svg")
    ap.add_argument("salida")
    a = ap.parse_args()
    out = Path(a.salida); out.mkdir(parents=True, exist_ok=True)
    raw = Path(a.svg).read_text(encoding="utf-8")
    shapes, total = _svg.measure(raw)
    x, y, w, h = total

    # alertas
    alerts = []
    if "<image" in raw:
        alerts.append("Tiene imágenes incrustadas (<image>): esas partes no se pueden recolorear.")
    if "Gradient" in raw:
        alerts.append("Tiene degradados: las variantes de un color los reemplazan por color plano; confirma con la persona.")
    if any(s["tag"] == "text" for s in shapes):
        alerts.append("Tiene texto vivo (<text>): pide el SVG con el texto convertido a contornos, o la tipografía puede cambiar.")
    if any(s["stroke"] not in ("none", "", None) and s["fill"] in ("none", "rgba(0, 0, 0, 0)") for s in shapes):
        alerts.append("Tiene trazos sin expandir: al escalar, su grosor no cambia igual que el resto; mejor expandirlos en Illustrator.")

    fills = Counter(_svg.rgb_to_hex(s["fill"]) for s in shapes)
    data = [{"idx": i, "bbox": [round(v, 2) for v in s["bbox"]], "fill": _svg.rgb_to_hex(s["fill"]),
             "stroke": _svg.rgb_to_hex(s["stroke"]), "tag": s["tag"]} for i, s in enumerate(shapes)]
    (out / "formas.json").write_text(json.dumps({"bbox_total": [round(v, 2) for v in total], "formas": data},
                                                indent=1, ensure_ascii=False), encoding="utf-8")

    # imagen original
    root = _svg.parse(a.svg)
    _svg.set_viewbox(root, total, 0.04)
    _svg.render_png(_svg.to_text(root), out / "original.png", 1000, bg="#FFFFFF")

    # imagen numerada
    root = _svg.parse(a.svg)
    for el in root.iter():
        el.attrib.pop("class", None)
    for i, el in enumerate(_svg.leaf_shapes(root)):
        el.attrib.pop("style", None)
        el.set("fill", HUES[i % len(HUES)])
    _svg.set_viewbox(root, total, 0.06)
    fs = max(w, h) * 0.035
    placed, labels = [], ""
    for i, s in enumerate(shapes):
        cx, cy = s["bbox"][0] + s["bbox"][2] / 2, s["bbox"][1] + s["bbox"][3] / 2
        while any(abs(cx - px) < fs * 1.2 and abs(cy - py) < fs for px, py in placed):
            cy += fs * 1.05  # etiquetas que caen en el mismo sitio se apilan
        placed.append((cx, cy))
        labels += (f"<text x='{cx:.2f}' y='{cy:.2f}' font-size='{fs:.2f}' "
                   f"text-anchor='middle' dominant-baseline='middle' font-family='sans-serif' font-weight='700' "
                   f"fill='#000' stroke='#fff' stroke-width='{fs * 0.18:.2f}' paint-order='stroke'>{i}</text>")
    _svg.render_png(_svg.to_text(root).replace("</svg>", labels + "</svg>"), out / "inspeccion.png", 1400, bg="#FFFFFF")

    print(f"{len(shapes)} formas · proporción ancho/alto {w / h:.3f} · viewBox útil {x:.1f} {y:.1f} {w:.1f} {h:.1f}")
    print("Colores:", ", ".join(f"{c} ×{n}" for c, n in fills.most_common()))
    print("idx  tag      x        y        ancho    alto     fill")
    for d in data:
        bx = d["bbox"]
        print(f"{d['idx']:<4} {d['tag']:<8} {bx[0]:<8.1f} {bx[1]:<8.1f} {bx[2]:<8.1f} {bx[3]:<8.1f} {d['fill']}")
    for al in alerts:
        print("ALERTA:", al)
    print(f"Imágenes: {out / 'inspeccion.png'} · {out / 'original.png'}")


if __name__ == "__main__":
    main()
