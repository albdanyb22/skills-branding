#!/usr/bin/env python3
"""
Calcula el tamaño mínimo de una versión del logo a partir de su detalle más
fino (trazo o contraforma más delgados), y genera la prueba visual.

    python min_size.py version.svg salida/nombre [--grupos grupos.json] [--mm 0.1] [--px 1]
                       [--letra-mm 2] [--letra-px 14]

Dos reglas; manda la más exigente:
  1. el detalle más fino (trazo o contraforma) no baja de --mm en impresión
     (0,1 mm) ni de --px en pantalla (1 px);
  2. si --grupos trae "logotipo" o "tagline", la altura de sus letras no baja de
     --letra-mm (2 mm) ni de --letra-px (14 px): sin esto, un logo de trazos
     gruesos daría mínimos en los que el nombre ya no se lee.
Detecta también ranuras abiertas (la cruz entre los pétalos de un símbolo, el
espacio entre letras). Si esas ranuras son más finas que el resto, da DOS umbrales:
  [completo]  todo se lee, también las ranuras
  [legible]   el nombre y las formas se leen, pero las ranuras pueden cerrarse
Por cada uno genera nombre_min_<umbral>.png (tamaño real) y _zoom.png (6×, sin
suavizar). Muéstralos y deja que la persona elija el mínimo oficial: con un símbolo
pequeño dentro del logo, lo habitual es el [legible], con el símbolo aparte y en
grande en los formatos chicos.
"""
import argparse
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import _svg  # noqa: E402


def finest_fraction(path, total, W=4000):
    import numpy as np
    from PIL import Image
    from scipy import ndimage
    root = _svg.parse(path); _svg.set_viewbox(root, total, 0.0)
    tmp = Path(str(path) + ".tmp_mask.png")
    _svg.render_png(_svg.to_text(root), tmp, W)
    img = np.array(Image.open(tmp).convert("RGBA"))
    tmp.unlink()
    # Segmenta por color (no solo por silueta): un punto azul sobre un círculo
    # amarillo es un detalle que también tiene que leerse.
    opaque = img[..., 3] > 128
    rgb = img[..., :3].astype(int)
    cols = np.unique(rgb[opaque].reshape(-1, 3) // 8 * 8, axis=0, return_counts=True)
    keep = []                                                # colores reales, no bordes suavizados
    for c, n in sorted(zip(cols[0], cols[1]), key=lambda t: -t[1]):
        if n > opaque.sum() * 0.002 and all(((c - k) ** 2).sum() > 40 ** 2 for k in keep):
            keep.append(c)
    keep = np.array(keep)
    dist = ((rgb[..., None, :] - keep[None, None, :, :]) ** 2).sum(-1)
    label = np.where(opaque, dist.argmin(-1), -1)
    min_area = img.shape[0] * img.shape[1] * 2e-5
    res = []
    for v in list(range(len(keep))) + [-1]:
        mask = label == v
        lab, n = ndimage.label(mask)
        if v == -1:  # contraformas: huecos interiores, no el fondo que toca el borde
            edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])))
        for k, sl in enumerate(ndimage.find_objects(lab), 1):
            if sl is None or (v == -1 and k in edge):
                continue
            sl = tuple(slice(max(0, a.start - 2), a.stop + 2) for a in sl)   # recorte: mucho más rápido
            comp = lab[sl] == k
            if comp.sum() < min_area:
                continue
            d = ndimage.distance_transform_edt(np.pad(comp, 1))
            dmax = d.max()
            # cresta (eje medio) sin las ramitas que van a las esquinas: solo donde
            # el grosor es al menos un 25 % del máximo de esa forma
            ridge = (d == ndimage.maximum_filter(d, size=3)) & (d > max(1.5, dmax * 0.25))
            if ridge.any():
                res.append((float(np.percentile(d[ridge], 10)) * 2, "contraforma" if v == -1 else "trazo/forma"))
    # Ranuras abiertas: espacios que no son huecos cerrados pero se cierran al
    # reducir (la cruz entre los pétalos de un símbolo, el espacio entre dos letras).
    # Se buscan dentro de la envolvente convexa de cada grupo de formas cercanas.
    from PIL import ImageDraw
    from scipy.spatial import ConvexHull
    near = ndimage.binary_dilation(opaque, iterations=max(2, int(W * 0.006)))
    lab, n = ndimage.label(near)
    for k, sl in enumerate(ndimage.find_objects(lab), 1):
        if sl is None:
            continue
        oy, ox = sl[0].start, sl[1].start
        ys, xs = np.nonzero((lab[sl] == k) & opaque[sl])
        if len(xs) < 50:
            continue
        pts = np.column_stack([xs, ys])
        try:
            hull = ConvexHull(pts)
        except Exception:
            continue
        hm = Image.new("L", (sl[1].stop - ox, sl[0].stop - oy), 0)
        ImageDraw.Draw(hm).polygon([tuple(p) for p in pts[hull.vertices]], fill=1)
        notch = (np.array(hm) > 0) & ~opaque[sl]
        nl, nn = ndimage.label(notch)
        hull_area = (np.array(hm) > 0).sum()
        for j, sj in enumerate(ndimage.find_objects(nl), 1):
            if sj is None:
                continue
            comp = nl[sj] == j
            if comp.sum() < max(min_area, hull_area * 0.01):   # ignora muescas diminutas de diseño
                continue
            d = ndimage.distance_transform_edt(np.pad(comp, 1))
            ridge = (d == ndimage.maximum_filter(d, size=3)) & (d > max(1.5, d.max() * 0.25))
            if ridge.any():
                res.append((float(np.percentile(d[ridge], 50)) * 2, "ranura o espacio entre formas"))
    t, name = min(res)
    sin_ranura = [r for r in res if not r[1].startswith("ranura")]
    t2, name2 = min(sin_ranura) if sin_ranura else (t, name)
    return (t / W, name), (t2 / W, name2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("svg"); ap.add_argument("salida")
    ap.add_argument("--mm", type=float, default=0.1)
    ap.add_argument("--px", type=float, default=1.0)
    ap.add_argument("--grupos")
    ap.add_argument("--letra-mm", type=float, default=2.0)
    ap.add_argument("--letra-px", type=float, default=14.0)
    a = ap.parse_args()
    out = Path(a.salida); out.parent.mkdir(parents=True, exist_ok=True)
    shapes, total = _svg.measure(Path(a.svg).read_text(encoding="utf-8"))
    completo, legible = finest_fraction(a.svg, total)
    fl = None
    if a.grupos:
        groups = _svg.parse_groups(_svg.load_json(a.grupos), len(shapes))
        hs = []
        for g in ("logotipo", "tagline"):
            if g in groups and groups[g]:
                alt = sorted(shapes[i]["bbox"][3] for i in groups[g])
                hs.append(alt[len(alt) // 2] / total[2])   # altura típica de letra / ancho del logo
        fl = min(hs) if hs else None

    def umbral(f, kind):
        mm_w, px_w, regla = a.mm / f, a.px / f, f"detalle más fino ({kind}, {f * 100:.2f}% del ancho)"
        if fl:
            if a.letra_mm / fl > mm_w:
                mm_w, regla = a.letra_mm / fl, f"altura de letra ({fl * 100:.1f}% del ancho)"
            px_w = max(px_w, a.letra_px / fl)
        return math.ceil(mm_w) / 10, int(math.ceil(px_w)), regla   # cm al milímetro, px enteros

    from PIL import Image
    root = _svg.parse(a.svg); _svg.set_viewbox(root, total, 0.0)
    text = _svg.to_text(root)
    resultados = [("todo se lee (también ranuras y espacios finos)", "completo", *umbral(*completo))]
    if legible[0] != completo[0]:
        resultados.append(("el nombre y las formas se leen; las ranuras finas pueden cerrarse",
                           "legible", *umbral(*legible)))
    for titulo, suf, cm, px, regla in resultados:
        _svg.render_png(text, f"{out}_min_{suf}.png", px, bg="#FFFFFF")
        im = Image.open(f"{out}_min_{suf}.png")
        im.resize((im.width * 6, im.height * 6), Image.NEAREST).save(f"{out}_min_{suf}_zoom.png")
        print(f"[{suf}] {titulo}")
        print(f"   impresión {cm:.1f} cm · pantalla {px} px de ancho · manda: {regla}")
        print(f"   prueba: {out}_min_{suf}.png · {out}_min_{suf}_zoom.png")
    if len(resultados) > 1:
        print("Hay dos umbrales: muestra ambas pruebas y deja que la persona elija cuál es el mínimo oficial.")


if __name__ == "__main__":
    main()
