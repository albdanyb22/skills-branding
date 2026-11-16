#!/usr/bin/env python3
"""
Arma el paquete de entregables del logo: un .zip con carpeta por versión y
subcarpeta por variante de color; cada archivo en SVG, PNG transparente
(500, 1000 y 2000 px de ancho) y PDF vectorial. Todo en RGB.

    python package.py carpeta_svgs/ salida/ --marca "Mi Marca" [--anchos 500,1000,2000]

carpeta_svgs/ contiene los SVG aprobados con nombre <version>_<variante>.svg
(por ejemplo horizontal_positivo.svg, isotipo_negativo.svg), que es como los
dejan logo_variants.py y compose.py.

Nomenclatura: <marca>_logo_<version>_<variante>_rgb[_<ancho>px].<ext>
Genera también salida/entregables.json (lista de archivos para la página
"Entregables" del manual) y salida/<marca>_logos.zip.
"""
import argparse
import json
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import _svg  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("svgs"); ap.add_argument("salida")
    ap.add_argument("--marca", required=True)
    ap.add_argument("--anchos", default="500,1000,2000")
    a = ap.parse_args()
    marca = _svg.slugify(a.marca).replace("-", "")
    anchos = [int(x) for x in a.anchos.split(",")]
    out = Path(a.salida); base = out / marca; base.mkdir(parents=True, exist_ok=True)
    index = []
    for f in sorted(Path(a.svgs).glob("*.svg")):
        if "_" not in f.stem:
            print("Omitido (nombre sin <version>_<variante>):", f.name); continue
        version, variante = f.stem.split("_", 1)
        d = base / version / variante; d.mkdir(parents=True, exist_ok=True)
        stem = f"{marca}_logo_{version}_{variante}_rgb"
        text = f.read_text(encoding="utf-8")
        if 'viewBox="' not in text:
            root = _svg.parse(f); _, tot = _svg.measure(text); _svg.set_viewbox(root, tot); text = _svg.to_text(root)
        (d / f"{stem}.svg").write_text(text, encoding="utf-8")
        files = [f"{stem}.svg"]
        for w in anchos:
            _svg.render_png(text, d / f"{stem}_{w}px.png", w)
            files.append(f"{stem}_{w}px.png")
        _svg.render_pdf(text, d / f"{stem}.pdf")
        files.append(f"{stem}.pdf")
        index.append({"version": version, "variante": variante, "carpeta": f"{marca}/{version}/{variante}", "archivos": files})
    (out / "entregables.json").write_text(json.dumps({"marca": a.marca, "nota": "Archivos en RGB. CMYK y Pantone: pendientes de arte final.",
                                                      "versiones": index}, indent=1, ensure_ascii=False), encoding="utf-8")
    z = out / f"{marca}_logos.zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in base.rglob("*"):
            if p.is_file():
                zf.write(p, p.relative_to(out))
    n = sum(len(i["archivos"]) for i in index)
    print(f"{len(index)} versiones/variantes · {n} archivos · {z}")


if __name__ == "__main__":
    main()
