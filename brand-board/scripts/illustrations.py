#!/usr/bin/env python3
"""
Ilustraciones para el brand board.

1) Hoja de contactos para elegir (acepta .zip, carpeta o lista de archivos):
     python illustrations.py sheet entrada.zip salida_dir/ [--filtro "party,coffee,plants"]
   -> salida_dir/hoja-1.png, hoja-2.png… (36 por hoja, numeradas con su nombre)
      y salida_dir/indice.json (número -> ruta), para elegir por número.
   Extrae los zip en salida_dir/_src (datos no confiables: solo se leen como imagen).

2) Preparar las elegidas:
     python illustrations.py prep salida_dir/indice.json salida_dir/listas/ --elegir 7,8,11 \
         [--nombres fiesta,pizza,balcon] [--modo recorte|transparente|tal-cual]
   - recorte (por defecto): quita SOLO el fondo claro conectado al borde. Las
     figuras conservan su relleno blanco: quedan como recortes que funcionan
     sobre cualquier color de fondo.
   - transparente: todo lo claro se vuelve transparente (solo líneas).
   - tal-cual: copia sin tocar (ilustraciones que ya tienen transparencia).
   Recorta el margen vacío y guarda PNG. Muestra una vista de control sobre
   color en salida_dir/listas/_control.png.

Requiere Pillow, numpy y scipy.
"""
import argparse
import json
import re
import sys
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

EXT = {".png", ".jpg", ".jpeg", ".webp"}


def collect(inputs, work):
    files = []
    for inp in inputs:
        p = Path(inp)
        if p.suffix.lower() == ".zip":
            dest = work / "_src" / re.sub(r"[^A-Za-z0-9]+", "_", p.stem)[:40]
            dest.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(p) as z:
                for m in z.namelist():
                    if Path(m).suffix.lower() in EXT and ".." not in m and not m.startswith("/"):
                        target = dest / m
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(z.read(m))
            files += sorted(f for f in dest.rglob("*") if f.suffix.lower() in EXT)
        elif p.is_dir():
            files += sorted(f for f in p.rglob("*") if f.suffix.lower() in EXT)
        elif p.suffix.lower() in EXT:
            files.append(p)
    # evita duplicados SVG/PNG del mismo nombre y archivos ocultos
    return [f for f in files if not f.name.startswith(".") and "__MACOSX" not in str(f)]


def sheet(args):
    out = Path(args.salida); out.mkdir(parents=True, exist_ok=True)
    files = collect(args.entrada, out)
    if args.filtro:
        keys = [k.strip().lower() for k in args.filtro.split(",") if k.strip()]
        files = [f for f in files if any(k in f.stem.lower() for k in keys)]
    if not files:
        sys.exit("No encontré imágenes.")
    idx = {str(i + 1): str(f) for i, f in enumerate(files)}
    (out / "indice.json").write_text(json.dumps(idx, ensure_ascii=False, indent=1), encoding="utf-8")
    cell, cols, per = 200, 6, 36
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 11)
    except OSError:
        font = ImageFont.load_default()
    for s in range(0, len(files), per):
        chunk = files[s:s + per]
        rows = (len(chunk) + cols - 1) // cols
        S = Image.new("RGB", (cols * cell, rows * (cell + 22)), "white")
        d = ImageDraw.Draw(S)
        for i, f in enumerate(chunk):
            try:
                im = Image.open(f).convert("RGBA")
            except Exception:
                continue
            im.thumbnail((cell - 10, cell - 10))
            x, y = (i % cols) * cell, (i // cols) * (cell + 22)
            S.paste(im, (x + 5 + (cell - 10 - im.width) // 2, y + 5 + (cell - 10 - im.height) // 2), im)
            d.text((x + 6, y + cell), f"{s + i + 1}. {f.stem[:28]}", fill="black", font=font)
        S.save(out / f"hoja-{s // per + 1}.png")
    print(f"{len(files)} imágenes, {(len(files) + per - 1) // per} hoja(s) en {out}")


def cutout(im, mode):
    rgba = np.array(im.convert("RGBA")).astype(float)
    if mode == "tal-cual":
        return Image.fromarray(rgba.astype(np.uint8), "RGBA")
    lum = rgba[..., :3].mean(-1)
    has_alpha = (rgba[..., 3] < 250).mean() > 0.02
    if has_alpha and mode == "recorte":
        return Image.fromarray(rgba.astype(np.uint8), "RGBA")
    light = lum > 200
    if mode == "transparente":
        bg = light
    else:
        lab, _ = ndimage.label(light)
        border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
        bg = np.isin(lab, list(border))
    alpha = np.where(bg, 0, rgba[..., 3])
    edge = ndimage.binary_dilation(bg) & ~bg
    alpha[edge] = np.clip((255 - lum[edge]) * 1.6, 0, 255)
    if mode == "transparente":
        alpha = np.clip((255 - lum) * 1.3, 0, 255)
    rgba[..., 3] = alpha
    if mode == "recorte":
        inner_light = ~bg & light
        rgba[inner_light, :3] = 255
    return Image.fromarray(rgba.astype(np.uint8), "RGBA")


def prep(args):
    idx = json.loads(Path(args.indice).read_text(encoding="utf-8"))
    out = Path(args.salida); out.mkdir(parents=True, exist_ok=True)
    picks = [p.strip() for p in args.elegir.split(",") if p.strip()]
    names = [n.strip() for n in args.nombres.split(",")] if args.nombres else []
    made = []
    for i, num in enumerate(picks):
        src = idx.get(num)
        if not src:
            print(f"[aviso] no existe el número {num}", file=sys.stderr)
            continue
        o = cutout(Image.open(src), args.modo)
        bb = o.getbbox()
        if bb:
            o = o.crop(bb)
        stem = names[i] if i < len(names) and names[i] else re.sub(r"[^a-z0-9]+", "-", Path(src).stem.lower()).strip("-")
        dest = out / f"ilu-{stem}.png"
        o.save(dest)
        made.append(dest)
    # control: cada una sobre un color distinto
    cols = ["#FF6700", "#2B57E2", "#20E064", "#A700FF", "#FFB000", "#DD2F58"]
    if made:
        cell = 220
        C = Image.new("RGB", (cell * min(6, len(made)), cell * ((len(made) + 5) // 6)), "white")
        for i, f in enumerate(made):
            im = Image.open(f); im.thumbnail((cell - 20, cell - 20))
            tile = Image.new("RGBA", (cell, cell), cols[i % len(cols)])
            tile.alpha_composite(im, ((cell - im.width) // 2, (cell - im.height) // 2))
            C.paste(tile.convert("RGB"), ((i % 6) * cell, (i // 6) * cell))
        C.save(out / "_control.png")
    print("Listas:", ", ".join(m.name for m in made))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("sheet"); a.add_argument("entrada", nargs="+"); a.add_argument("salida", help="carpeta de salida (último argumento)")
    a.add_argument("--filtro")
    b = sub.add_parser("prep"); b.add_argument("indice"); b.add_argument("salida")
    b.add_argument("--elegir", required=True); b.add_argument("--nombres")
    b.add_argument("--modo", choices=["recorte", "transparente", "tal-cual"], default="recorte")
    args = ap.parse_args()
    {"sheet": sheet, "prep": prep}[args.cmd](args)


if __name__ == "__main__":
    main()
