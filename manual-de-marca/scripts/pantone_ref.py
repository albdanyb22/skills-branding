#!/usr/bin/env python3
"""
Pantone de referencia (Solid Coated y textil TCX) más cercano a cada color, por
diferencia perceptual ΔE 2000. Úsalo solo cuando la persona NO tiene Pantone
validados: el resultado es una REFERENCIA DE PARTIDA, nunca un valor oficial.

    python pantone_ref.py colores.json salida.json [--cache DIR]

colores.json: el mismo de color_system.py ({"colores": [{"nombre","hex"}, ...]}).
Las listas salen de los paquetes públicos de npm "pantone-colors" (PMS, ~900
colores) y "nearest-pantone" (TCX, ~2.200); se instalan con npm en --cache la
primera vez. Sus HEX son aproximados y la lista PMS no tiene todos los colores
modernos: por eso cada resultado lleva su ΔE.
  ΔE < 2: casi idéntico · 2–5: parecido · > 5: se nota · > 10: no hay equivalente cercano.
"""
import argparse
import json
import math
import re
import subprocess
from pathlib import Path


def lab(h):
    h = h.lstrip("#"); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [v / 12.92 if v <= 0.04045 else ((v + .055) / 1.055) ** 2.4 for v in c]
    X = (c[0] * .4124 + c[1] * .3576 + c[2] * .1805) / .95047; Y = c[0] * .2126 + c[1] * .7152 + c[2] * .0722
    Z = (c[0] * .0193 + c[1] * .1192 + c[2] * .9505) / 1.08883
    f = lambda t: t ** (1 / 3) if t > .008856 else 7.787 * t + 16 / 116
    return 116 * f(Y) - 16, 500 * (f(X) - f(Y)), 200 * (f(Y) - f(Z))


def de2000(a, b):
    L1, a1, b1 = a; L2, a2, b2 = b
    C1 = math.hypot(a1, b1); C2 = math.hypot(a2, b2); Cb = (C1 + C2) / 2
    G = .5 * (1 - math.sqrt(Cb ** 7 / (Cb ** 7 + 25 ** 7)))
    a1p, a2p = a1 * (1 + G), a2 * (1 + G); C1p, C2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h1 = math.degrees(math.atan2(b1, a1p)) % 360; h2 = math.degrees(math.atan2(b2, a2p)) % 360
    dL = L2 - L1; dC = C2p - C1p; dh = h2 - h1
    if C1p * C2p == 0: dh = 0
    elif dh > 180: dh -= 360
    elif dh < -180: dh += 360
    dH = 2 * math.sqrt(C1p * C2p) * math.sin(math.radians(dh / 2))
    Lb = (L1 + L2) / 2; Cbp = (C1p + C2p) / 2
    if C1p * C2p == 0: hb = h1 + h2
    elif abs(h1 - h2) <= 180: hb = (h1 + h2) / 2
    else: hb = (h1 + h2 + 360) / 2 if h1 + h2 < 360 else (h1 + h2 - 360) / 2
    T = 1 - .17 * math.cos(math.radians(hb - 30)) + .24 * math.cos(math.radians(2 * hb)) + .32 * math.cos(math.radians(3 * hb + 6)) - .2 * math.cos(math.radians(4 * hb - 63))
    dt = 30 * math.exp(-((hb - 275) / 25) ** 2); RC = 2 * math.sqrt(Cbp ** 7 / (Cbp ** 7 + 25 ** 7))
    SL = 1 + .015 * (Lb - 50) ** 2 / math.sqrt(20 + (Lb - 50) ** 2); SC = 1 + .045 * Cbp; SH = 1 + .015 * Cbp * T
    RT = -math.sin(math.radians(2 * dt)) * RC
    return math.sqrt((dL / SL) ** 2 + (dC / SC) ** 2 + (dH / SH) ** 2 + RT * (dC / SC) * (dH / SH))


def datasets(cache):
    cache = Path(cache); nm = cache / "node_modules"
    if not (nm / "pantone-colors").exists() or not (nm / "nearest-pantone").exists():
        cache.mkdir(parents=True, exist_ok=True)
        subprocess.run(["npm", "init", "-y"], cwd=cache, capture_output=True)
        subprocess.run(["npm", "i", "pantone-colors", "nearest-pantone"], cwd=cache, check=True, capture_output=True)
    pms_js = (nm / "pantone-colors" / "index.js").read_text()
    pms = json.loads(re.search(r"exports\.default\s*=\s*(\{.*?\})", pms_js, re.S).group(1))
    src = (nm / "nearest-pantone" / "index.js").read_text()
    tcx = [{"code": a, "name": b, "hex": c} for a, b, c in
           re.findall(r'pantone\s*:\s*"([^"]+)",\s*name:\s*"([^"]+)",\s*hex:\s*"(#[0-9a-fA-F]{6})"', src)]
    return pms, tcx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("colores"); ap.add_argument("salida")
    ap.add_argument("--cache", default=str(Path.home() / ".cache" / "pantone-ref"))
    a = ap.parse_args()
    pms, tcx = datasets(a.cache)
    out = {}
    for c in json.loads(Path(a.colores).read_text(encoding="utf-8"))["colores"]:
        L = lab(c["hex"])
        p = sorted((de2000(L, lab(v)), k) for k, v in pms.items())[:2]
        t = min((de2000(L, lab(x["hex"])), x["code"], x["name"]) for x in tcx)
        out[c["nombre"]] = {"pms": f"{p[0][1]} C", "pms_de": round(p[0][0], 1), "pms_alt": f"{p[1][1]} C",
                            "tcx": f"{t[1]} TCX", "tcx_nombre": t[2], "tcx_de": round(t[0], 1)}
        nota = "  ← sin equivalente cercano" if p[0][0] > 10 else ""
        print(f"{c['nombre']:<12} PMS {p[0][1]} C (ΔE {p[0][0]:.1f}) · alt {p[1][1]} C · TCX {t[1]} (ΔE {t[0]:.1f}){nota}")
    Path(a.salida).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("Referencias aproximadas: el manual debe decir 'validar con guía física y prueba de color'.")


if __name__ == "__main__":
    main()
