#!/usr/bin/env python3
"""
Sistema de color del manual: valida valores, deriva conversiones, escalas
50–950 y la matriz de contraste. Todo sale de UN valor fuente por color (HEX),
así los valores nunca se contradicen entre sí.

    python color_system.py colores.json salida/

colores.json:
{
  "tinta": "#1D1D1B",                          # opcional, texto oscuro de la marca
  "colores": [
    {"nombre": "Azul Profundo", "hex": "#172AF0", "rol": "principal", "uso": 50,
     "rgb": [23, 42, 240],          # opcional: lo que diga el material de origen, para validarlo
     "cmyk": [90, 82, 0, 0],        # opcional: si lo dio la imprenta, se respeta
     "pantone": "2728 C"}           # opcional: si no viene, queda "pendiente de validar"
  ]
}

Salida:
  salida/sistema_color.json   valores finales por color (+ escala) y pares de contraste
  salida/informe_color.md     inconsistencias encontradas y matriz de contraste legible
Imprime un resumen con cada ALERTA. Muéstraselas a la persona antes de diseñar.

CMYK: si hay un perfil ICC CMYK en el sistema (busca FOGRA39 de TeX Live, o pásalo
con --perfil), convierte con él y avisa de los colores fuera de gama (cómo se verán
impresos). Sin perfil, usa la fórmula directa y lo marca como aproximado.
Pantone/TCX de referencia: corre antes pantone_ref.py y copia sus resultados en
"pantone"/"tcx" de colores.json.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import _svg  # noqa: E402

STEPS = {50: .975, 100: .945, 200: .895, 300: .82, 400: .725, 500: .635, 600: .55, 700: .475, 800: .405, 900: .345, 950: .26}


def hex2rgb(h):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        raise ValueError(f"HEX inválido: #{h}")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def rgb2hex(rgb):
    return "#" + "".join(f"{max(0, min(255, round(v))):02X}" for v in rgb)


def lin(c):
    c /= 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def delin(c):
    v = 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055
    return v * 255


def lum(rgb):
    r, g, b = (lin(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def to_oklch(rgb):
    import math
    r, g, b = (lin(v) for v in rgb)
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    L = 0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s
    A = 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s
    B = 0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s
    return L, math.hypot(A, B), math.atan2(B, A)


def from_oklch(L, C, H):
    import math
    A, B = C * math.cos(H), C * math.sin(H)
    l = (L + 0.3963377774 * A + 0.2158037573 * B) ** 3
    m = (L - 0.1055613458 * A - 0.0638541728 * B) ** 3
    s = (L - 0.0894841775 * A - 1.2914855480 * B) ** 3
    r = 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    b = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    return [r, g, b]


def in_gamut(lrgb):
    return all(-1e-4 <= v <= 1 + 1e-4 for v in lrgb)


def scale(hexc):
    rgb = hex2rgb(hexc)
    L0, C0, H = to_oklch(rgb)
    anchor = min(STEPS, key=lambda k: abs(STEPS[k] - L0))
    out = {}
    for k, L in STEPS.items():
        if k == anchor:
            out[k] = hexc.upper(); continue
        # menos croma en los extremos claros/oscuros, como hacen las escalas de UI
        f = 1 - abs(L - L0) / max(L0, 1 - L0, 1e-6) * 0.55
        C = C0 * max(f, 0.08)
        while C > 0 and not in_gamut(from_oklch(L, C, H)):
            C -= 0.002
        out[k] = rgb2hex([delin(max(0, min(1, v))) for v in from_oklch(L, max(C, 0), H)])
    return out, anchor


ICC_CANDIDATOS = [
    "/usr/share/texlive/texmf-dist/tex/generic/colorprofiles/FOGRA39L_coated.icc",
    "/usr/share/color/icc/FOGRA39L_coated.icc", "/usr/share/color/icc/ghostscript/default_cmyk.icc",
]


def buscar_perfil(ruta=None):
    from pathlib import Path as P
    for c in ([ruta] if ruta else []) + ICC_CANDIDATOS:
        if c and P(c).exists():
            return c
    import glob
    hits = glob.glob("/usr/share/**/*FOGRA39*.icc", recursive=True)
    return hits[0] if hits else None


def cmyk_icc(rgb, perfil):
    """CMYK con perfil de imprenta (relativo colorimétrico + compensación de punto negro)."""
    from PIL import Image, ImageCms
    t = ImageCms.buildTransform(ImageCms.createProfile("sRGB"), ImageCms.getOpenProfile(perfil), "RGB", "CMYK",
                                renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC,
                                flags=ImageCms.Flags.BLACKPOINTCOMPENSATION)
    back = ImageCms.buildTransform(ImageCms.getOpenProfile(perfil), ImageCms.createProfile("sRGB"), "CMYK", "RGB",
                                   renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC)
    c = ImageCms.applyTransform(Image.new("RGB", (1, 1), tuple(rgb)), t).getpixel((0, 0))
    r = ImageCms.applyTransform(Image.new("CMYK", (1, 1), c), back).getpixel((0, 0))
    return [round(v / 255 * 100) for v in c], list(r)


def cmyk_aprox(rgb):
    r, g, b = (v / 255 for v in rgb)
    k = 1 - max(r, g, b)
    if k >= 1:
        return [0, 0, 0, 100]
    return [round((1 - v - k) / (1 - k) * 100) for v in (r, g, b)] + [round(k * 100)]


def level(r):
    return "AAA" if r >= 7 else "AA" if r >= 4.5 else "AA grande" if r >= 3 else "no apto"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("colores"); ap.add_argument("salida")
    ap.add_argument("--perfil", help="perfil ICC CMYK (por defecto busca FOGRA39 en el sistema)")
    a = ap.parse_args()
    perfil = buscar_perfil(a.perfil)
    if not perfil:
        print("AVISO: no encontré un perfil ICC CMYK; el CMYK sale de la fórmula directa (menos fiable).")
    spec = _svg.load_json(a.colores)
    out = Path(a.salida); out.mkdir(parents=True, exist_ok=True)
    alerts, final = [], []
    for c in spec["colores"]:
        hexc = "#" + c["hex"].strip().lstrip("#").upper()
        rgb = hex2rgb(hexc)
        if c.get("rgb"):
            diff = max(abs(x - y) for x, y in zip(rgb, c["rgb"]))
            if diff > 3:
                alerts.append(f"{c['nombre']}: el RGB de origen {c['rgb']} no corresponde al HEX {hexc} "
                              f"({rgb2hex(c['rgb'])} es otro color). Se usa el HEX como fuente; confirma cuál es el correcto.")
        impreso = None
        if perfil:
            cm_a, impreso = cmyk_icc(rgb, perfil)
            if max(abs(x - y) for x, y in zip(rgb, impreso)) > 40:
                alerts.append(f"{c['nombre']}: fuera de gama CMYK; impreso se verá como {rgb2hex(impreso)} en vez de {hexc}. "
                              "Para piezas donde importe (stickers, señalética), recomienda Pantone directo.")
        else:
            cm_a = cmyk_aprox(rgb)
        if c.get("cmyk"):
            cmyk, cm_src = c["cmyk"], "origen"
            if max(abs(x - y) for x, y in zip(cmyk, cm_a)) > 25:
                alerts.append(f"{c['nombre']}: el CMYK de origen {cmyk} se aleja mucho de la conversión directa {cm_a}. "
                              "Si viene de la imprenta o de un perfil (FOGRA, GRACoL) se mantiene; si no, revisarlo.")
        else:
            cmyk, cm_src = cm_a, ("perfil " + Path(perfil).stem + ": validar con la imprenta") if perfil else "aproximado: validar con el perfil de la imprenta"
        pantone = c.get("pantone") or "pendiente: validar con guía Pantone física"
        sc, anchor = scale(hexc)
        final.append({"nombre": c["nombre"], "rol": c.get("rol", ""), "uso": c.get("uso"),
                      "hex": hexc, "rgb": rgb, "cmyk": cmyk, "cmyk_fuente": cm_src, "pantone": pantone,
                      "escala": sc, "paso_base": anchor, "impreso_aprox": rgb2hex(impreso) if impreso else None,
                      "tcx": c.get("tcx")})
    usos = [f["uso"] for f in final if f["uso"] is not None]
    if usos and abs(sum(usos) - 100) > 0.5:
        alerts.append(f"Los porcentajes de uso suman {sum(usos)} %, no 100 %.")
    tinta = "#" + spec.get("tinta", "#1A1A1A").lstrip("#").upper()
    pool = [(f["nombre"], f["hex"]) for f in final] + [("Blanco", "#FFFFFF"), ("Tinta", tinta)]
    pairs = []
    for fn, fh in pool:
        for tn, th in pool:
            if fn == tn:
                continue
            r = contrast(hex2rgb(fh), hex2rgb(th))
            pairs.append({"fondo": fn, "texto": tn, "ratio": round(r, 2), "nivel": level(r)})
    (out / "sistema_color.json").write_text(json.dumps({"tinta": tinta, "colores": final, "contraste": pairs},
                                                       indent=1, ensure_ascii=False), encoding="utf-8")
    names = [n for n, _ in pool]
    md = ["# Informe de color", "", "## Alertas", ""] + ([f"- {x}" for x in alerts] or ["- Sin inconsistencias."])
    md += ["", "## Valores finales", "", "| Color | HEX | RGB | CMYK | Pantone |", "|---|---|---|---|---|"]
    md += [f"| {f['nombre']} | {f['hex']} | {'/'.join(map(str, f['rgb']))} | {'/'.join(map(str, f['cmyk']))} ({f['cmyk_fuente']}) | {f['pantone']} |" for f in final]
    md += ["", "## Contraste (filas = fondo, columnas = texto)", "", "| fondo \\ texto | " + " | ".join(names) + " |",
           "|---" * (len(names) + 1) + "|"]
    for fn in names:
        row = [next((f"{p['ratio']} {p['nivel']}" for p in pairs if p["fondo"] == fn and p["texto"] == tn), "—") for tn in names]
        md.append(f"| {fn} | " + " | ".join(row) + " |")
    (out / "informe_color.md").write_text("\n".join(md), encoding="utf-8")
    for x in alerts:
        print("ALERTA:", x)
    ok = [p for p in pairs if p["nivel"] in ("AA", "AAA")]
    print(f"{len(final)} colores · {len(ok)} pares aptos para texto normal · {out / 'informe_color.md'}")


if __name__ == "__main__":
    main()
