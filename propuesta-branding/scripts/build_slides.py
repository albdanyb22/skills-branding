#!/usr/bin/env python3
"""
Genera la "Propuesta de branding" como presentación .pptx lista para Google Slides.

Uso:
    python build_slides.py contenido.json salida.pptx

- Todo es editable: cuadros de texto, formas y tablas nativas (nada rasterizado).
- Fuentes: Inter Tight (titulares) e Inter (texto). Son Google Fonts, así que
  Google Slides las muestra sin instalar nada. Las fuentes del type board
  también se escriben por nombre: si son Google Fonts, Slides las renderiza.
- Google Slides NO reduce el texto para que quepa: este script mide cada texto
  con las fuentes reales (assets/fonts/*.ttf) y elige el tamaño que entra.
- Estética tipo Notion: blanco, aire, breadcrumbs, callouts, citas y galerías.
  Amarillo principal; azul vibrante y verde como secundarios.

El JSON sigue references/esquema-json.md. Las imágenes son opcionales: sin
ellas se dibujan tarjetas-placeholder con la descripción de lo que va ahí.
"""
import argparse
import json
import re
import sys
from pathlib import Path

from PIL import Image, ImageFont
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN, MSO_AUTO_SIZE
from pptx.oxml.ns import qn
from pptx.util import Emu, Pt
from lxml import etree

SKILL_DIR = Path(__file__).resolve().parent.parent
FONTS = SKILL_DIR / "assets" / "fonts"

W, H = 1280, 720  # px de diseño (96 dpi) -> 13.333 x 7.5 in
LH = 1.21  # altura natural de línea de Inter/Inter Tight (ascender+descender); Slides multiplica sobre esto

# ------------------------------------------------------------------ colores
INK, TEXT, MUTED, FAINT = "191919", "37352F", "787774", "A5A29C"
LINE, BG2, WHITE = "EDEDEB", "F7F6F3", "FFFFFF"
HEAD, BODY = "Inter Tight", "Inter"


def hx(c):
    return c.lstrip("#").upper()


def mix(c, pct, base="FFFFFF"):
    """pct% de c sobre base (como color-mix)."""
    c, base = hx(c), hx(base)
    out = ""
    for i in (0, 2, 4):
        a, b = int(c[i:i + 2], 16), int(base[i:i + 2], 16)
        out += f"{round(a * pct / 100 + b * (100 - pct) / 100):02X}"
    return out


def E(px):
    return Emu(int(round(px * 9525)))


# ------------------------------------------------------------------ medición
_font_cache = {}


def _font(family, bold, size):
    if family == HEAD:
        f = "inter-tight-700.ttf" if bold else "inter-tight-500.ttf"
    else:
        f = "inter-600.ttf" if bold else "inter-400.ttf"
    key = (f, round(size * 4))
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(str(FONTS / f), max(1, round(size)))
    return _font_cache[key]


def strip_md(s):
    return re.sub(r"\*\*(.+?)\*\*", r"\1", str(s or ""))


def wrap(text, family, bold, size, width, track=0):
    """track = espaciado entre letras en em (negativo en titulares)."""
    f = _font(family, bold, size)
    L = lambda t: f.getlength(t) + track * size * len(t)
    lines = []
    for para in strip_md(text).split("\n"):
        words, cur = para.split(" "), ""
        for w in words:
            t = (cur + " " + w).strip()
            if L(t) <= width * 0.95 or not cur:  # 5% de margen: Slides mide distinto
                cur = t
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
    return lines


def text_h(text, family, bold, size, width, ls, track=0):
    return len(wrap(text, family, bold, size, width, track)) * size * ls


def fit(text, family, bold, size, width, height, ls, min_size=10, track=0):
    while size > min_size and text_h(text, family, bold, size, width, ls, track) > height:
        size -= 0.5
    if text_h(text, family, bold, size, width, ls, track) > height:
        print(f"[aviso] el texto no entra ni a {min_size}px; recórtalo: «{strip_md(text)[:50]}…»", file=sys.stderr)
    return size


# ------------------------------------------------------------------ primitivas
def _nostyle(shape):
    st = shape._element.find(qn("p:style"))
    if st is not None:
        shape._element.remove(st)


def rect(sl, x, y, w, h, fill=None, radius=0, line=None, shape=None):
    kind = shape or (MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE)
    s = sl.shapes.add_shape(kind, E(x), E(y), E(w), E(h))
    _nostyle(s)
    if radius and kind == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = min(0.5, radius / min(w, h))
    if kind == MSO_SHAPE.ROUND_2_SAME_RECTANGLE:
        s.adjustments[0] = min(0.5, radius / min(w, h))
        s.adjustments[1] = 0
    if fill:
        s.fill.solid()
        s.fill.fore_color.rgb = RGBColor.from_string(hx(fill))
    else:
        s.fill.background()
    if line:
        s.line.color.rgb = RGBColor.from_string(hx(line))
        s.line.width = E(1)
    else:
        s.line.fill.background()
    s.text_frame.text = ""
    return s


def oval(sl, x, y, d, fill):
    return rect(sl, x, y, d, d, fill, shape=MSO_SHAPE.OVAL)


def text(sl, x, y, w, h, content, family=BODY, size=16, color=TEXT, bold=False, ls=1.5,
         align="l", anchor="t", spacing=None, bold_color=INK, runs=None):
    """Cuadro de texto. `content` admite \\n y **negrita**. `runs` = [(texto, color, bold)] en una línea."""
    tb = sl.shapes.add_textbox(E(x), E(y), E(w), E(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.NONE
    for m in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(tf, m, 0)
    tf.vertical_anchor = {"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE, "b": MSO_ANCHOR.BOTTOM}[anchor]
    paras = [[(t, color, bold)] for t in [None]] if runs else None
    if runs:
        paras = [runs]
    else:
        paras = []
        for line in str(content or "").split("\n"):
            parts = re.split(r"(\*\*.+?\*\*)", line)
            paras.append([(p[2:-2], bold_color, True) if p.startswith("**") else (p, color, bold)
                          for p in parts if p])
    for i, pr in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT}[align]
        p.line_spacing = ls / LH
        for t, col, b in pr or [("", color, bold)]:
            r = p.add_run()
            r.text = t
            f = r.font
            f.name = family
            f.size = Pt(size * 0.75)
            f.bold = b
            f.color.rgb = RGBColor.from_string(hx(col))
            if spacing is not None:
                r._r.get_or_add_rPr().set("spc", str(int(spacing * 75)))  # px -> centésimas de pt
    return tb


def picture(sl, path, x, y, w, h):
    """Imagen recortada para cubrir el recuadro (object-fit: cover)."""
    iw, ih = Image.open(path).size
    pic = sl.shapes.add_picture(str(path), E(x), E(y), E(w), E(h))
    box, img = w / h, iw / ih
    if img > box:
        c = (1 - box / img) / 2
        pic.crop_left = pic.crop_right = c
    else:
        c = (1 - img / box) / 2
        pic.crop_top = pic.crop_bottom = c
    return pic


def picture_contain(sl, path, x, y, w, h):
    iw, ih = Image.open(path).size
    s = min(w / iw, h / ih)
    nw, nh = iw * s, ih * s
    return sl.shapes.add_picture(str(path), E(x + (w - nw) / 2), E(y + (h - nh) / 2), E(nw), E(nh))


def placeholder(sl, x, y, w, h, caption, radius=10):
    rect(sl, x, y, w, h, BG2, radius=radius)
    cap = f"Imagen · {caption}" if caption else "Imagen"
    pad = 14
    size = fit(cap, BODY, False, 12, w - 2 * pad, h - 2 * pad, 1.4, 8)
    text(sl, x + pad, y + pad, w - 2 * pad, h - 2 * pad, cap, size=size, color=MUTED, ls=1.4, align="c", anchor="m")


def resolve(path, base):
    if not path:
        return None
    p = Path(path)
    if not p.is_absolute():
        p = (base / p).resolve()
    if not p.exists():
        print(f"[aviso] imagen no encontrada: {p}", file=sys.stderr)
        return None
    return p


# ------------------------------------------------------------------ deck
class Deck:
    def __init__(self, d, base):
        self.d, self.base = d, base
        self.marca = d.get("marca", "")
        self.Y = hx(d.get("color_acento") or "FDD23C")
        self.B = hx(d.get("color_azul") or "2F5BFF")
        self.G = hx(d.get("color_verde") or "1FC86A")
        self.Ysoft, self.Bsoft, self.Gsoft = mix(self.Y, 30), mix(self.B, 14), mix(self.G, 18)
        self.Ywash = mix(self.Y, 12)
        self.prs = Presentation()
        self.prs.slide_width, self.prs.slide_height = E(W), E(H)
        self.blank = self.prs.slide_layouts[6]
        self.slides = []  # (slide, is_page)
        self.k = 0        # rotación de color en páginas estándar
        self.sec = 0      # número de sección

    # paleta de la página actual
    def pal(self):
        return [(self.Y, INK, self.Ysoft), (self.B, WHITE, self.Bsoft), (self.G, INK, self.Gsoft)][self.k % 3]

    def new(self, page=True, crumb=""):
        sl = self.prs.slides.add_slide(self.blank)
        self.slides.append((sl, page, crumb))
        if page:
            self.k += 1
        return sl

    def page(self, crumb):
        sl = self.new(True, crumb)
        c, _, _ = self.pal_for(len([s for s in self.slides if s[1]]) - 1)
        # breadcrumb
        rect(sl, 40, 18, 16, 16, c, radius=4)
        runs = [(self.marca, MUTED, False), ("  /  ", FAINT, False), ("Propuesta de branding", MUTED, False),
                ("  /  ", FAINT, False), (crumb, TEXT, True)]
        text(sl, 64, 17, 900, 20, None, size=13, runs=runs, ls=1.2)
        rect(sl, 0, 52, W, 1, LINE)
        return sl

    def pal_for(self, i):
        return [(self.Y, INK, self.Ysoft), (self.B, WHITE, self.Bsoft), (self.G, INK, self.Gsoft)][i % 3]

    def cur(self):
        return self.pal_for(len([s for s in self.slides if s[1]]) - 1)

    def head(self, sl, title, label=None, x=120, y=108, width=1040, size=50):
        c, ink, _ = self.cur()
        self.sec += 1
        rect(sl, x, y, 46, 46, c, radius=10)
        text(sl, x, y, 46, 46, f"{self.sec:02d}", family=HEAD, size=17, color=ink, bold=True, align="c", anchor="m", ls=1)
        y += 46 + 22
        if label:
            lh = text_h(label, BODY, False, 13, width, 1.35)
            text(sl, x, y, width, lh + 2, label, size=13, color=MUTED, ls=1.35)
            y += lh + 8
        size = fit(title, HEAD, True, size, width, size * 1.05 * 2, 1.05, 28, track=-0.03)
        h = text_h(title, HEAD, True, size, width, 1.05, track=-0.03)
        text(sl, x, y, width, h + 6, title, family=HEAD, size=size, color=INK, bold=True, ls=1.05,
             spacing=-size * 0.03)
        return y + h

    def lead(self, sl, content, y, x=120, width=980, bottom=664, size=25, ls=1.55, color=TEXT):
        size = fit(content, BODY, False, size, width, bottom - y, ls, 13)
        text(sl, x, y, width, bottom - y, content, size=size, color=color, ls=ls)

    def callout(self, sl, content, y, x=120, width=980):
        c, _, _ = self.cur()
        h = text_h(content, BODY, False, 15, width - 72, 1.55) + 32
        rect(sl, x, y, width, h, BG2, radius=8)
        oval(sl, x + 20, y + 18, 18, c)
        text(sl, x + 52, y + 16, width - 72, h - 32, content, size=15, color=MUTED, ls=1.55)
        return y + h

    def quote(self, sl, content, y, x=120, width=980, bottom=664):
        c, _, _ = self.cur()
        size = fit(content, HEAD, False, 34, width - 34, bottom - y, 1.32, 18, track=-0.015)
        h = text_h(content, HEAD, False, size, width - 34, 1.32, track=-0.015)
        rect(sl, x, y, 4, h + 8, c)
        text(sl, x + 34, y + 4, width - 34, h + 10, content, family=HEAD, size=size, color=INK, ls=1.32,
             spacing=-size * 0.015)

    def cards(self, sl, items, y, x=120, width=1040, bottom=664):
        cols = [(self.Y, INK), (self.B, WHITE), (self.G, INK)]
        n = max(1, len(items))
        gap = 18
        cw = (width - gap * (n - 1)) / n
        inner = cw - 44
        # tamaño común que entre en todas
        title_s, desc_s = 22, 15
        while True:
            need = max(22 + 14 + text_h(it.get("nombre"), HEAD, True, title_s, inner, 1.2) + 10 +
                       text_h(it.get("descripcion"), BODY, False, desc_s, inner, 1.6) + 46 for it in items)
            if need <= bottom - y or desc_s <= 11:
                break
            desc_s -= 0.5
            title_s = max(16, title_s - 0.25)
        ch = need
        for i, it in enumerate(items):
            cx = x + i * (cw + gap)
            col, ink = cols[i % 3]
            rect(sl, cx, y, cw, ch, WHITE, radius=10, line=LINE)
            rect(sl, cx + 22, y, 40, 4, col)
            rect(sl, cx + 22, y + 22, 30, 22, col if i % 3 else self.Ysoft, radius=4)
            text(sl, cx + 22, y + 22, 30, 22, f"{i + 1:02d}", size=12, color=ink if i % 3 else INK, align="c", anchor="m", ls=1)
            ty = y + 22 + 22 + 14
            th = text_h(it.get("nombre"), HEAD, True, title_s, inner, 1.2)
            text(sl, cx + 22, ty, inner, th + 4, it.get("nombre"), family=HEAD, size=title_s, color=INK, bold=True, ls=1.2)
            ty += th + 10
            text(sl, cx + 22, ty, inner, ch - (ty - y) - 18, it.get("descripcion"), size=desc_s, ls=1.6)

    # ---------------------------------------------------------- portadas
    def cover_like(self, band, deco, icon, title, title_size=72):
        sl = self.new(page=False)
        rect(sl, 0, 0, W, 250, band)
        # composición geométrica
        x = W - 120
        for kind, col in reversed(deco):
            if kind == "sq":
                x -= 120
                rect(sl, x, 100, 120, 150, col, radius=22, shape=MSO_SHAPE.ROUND_2_SAME_RECTANGLE)
            else:
                x -= 120
                oval(sl, x, 100, 120, col)
            x += 18
        rect(sl, 120, 196, 108, 108, WHITE, radius=22, line=LINE)
        text(sl, 120, 196, 108, 108, icon, family=HEAD, size=48, color=INK, bold=True, align="c", anchor="m", ls=1)
        size = fit(title, HEAD, True, title_size, 1040, title_size * 1.05, 1.02, 40, track=-0.033)
        text(sl, 120, 338, 1040, size * 1.15, title, family=HEAD, size=size, color=INK, bold=True, ls=1.0,
             spacing=-size * 0.033)
        return sl, 338 + size * 1.15 + 26


def build(d, base):
    k = Deck(d, base)
    marca = k.marca
    dis = d.get("disenador") or {}
    initial = (marca or "B")[:1].upper()

    # 1. Portada
    sl, y = k.cover_like(k.Y, [("sq", k.B), ("ci", k.G)], initial, "Propuesta de branding")
    props = [("Marca", marca),
             ("Diseño", " · ".join(x for x in [dis.get("nombre"), dis.get("rol", "Designer")] if x)),
             ("Fecha", d.get("fecha", ""))]
    for kk, v in props:
        if v:
            text(sl, 120, y, 150, 22, kk, size=16, color=MUTED, ls=1.2)
            text(sl, 270, y, 700, 22, v, size=16, color=INK, ls=1.2)
            y += 32
    text(sl, 120, y, 150, 22, "Estado", size=16, color=MUTED, ls=1.2)
    rect(sl, 270, y - 2, 92, 26, k.Ysoft, radius=6)
    text(sl, 270, y - 2, 92, 26, "Propuesta", size=14, color=INK, bold=True, align="c", anchor="m", ls=1)

    # 2. Quiénes somos
    if d.get("quienes_somos"):
        sl = k.page("Quiénes somos")
        y = k.head(sl, "Quiénes somos")
        k.lead(sl, d["quienes_somos"], y + 30)

    # 3-4. Misión / Visión
    for key, title in (("mision", "Misión"), ("vision", "Visión")):
        if d.get(key):
            sl = k.page(title)
            y = k.head(sl, title)
            k.quote(sl, d[key], y + 34)

    # Valores
    vals = d.get("valores", [])
    sec_val = k.sec + 1
    for i, v in enumerate(vals):
        sl = k.page("Valores")
        k.sec = sec_val - 1
        y = k.head(sl, v.get("nombre"), f"Valores · {i + 1:02d} / {len(vals):02d}", width=700, size=64)
        k.lead(sl, v.get("descripcion"), y + 30, width=700)
        c, _, soft = k.cur()
        tx, ty = 910, 176
        rect(sl, tx, ty, 1, 40 + 38 * len(vals), LINE)
        text(sl, tx + 28, ty, 220, 16, "VALORES", size=12, color=FAINT, ls=1.2, spacing=1)
        for j, x in enumerate(vals):
            ry = ty + 28 + j * 38
            if j == i:
                rect(sl, tx + 18, ry, 232, 34, soft, radius=6)
            text(sl, tx + 28, ry, 220, 34, None, anchor="m", ls=1, size=16,
                 runs=[(f"{j + 1:02d}   ", INK if j == i else FAINT, False),
                       (x.get("nombre", ""), INK if j == i else MUTED, j == i)])

    # Reason why
    if d.get("reason_why"):
        sl = k.page("Reason Why")
        y = k.head(sl, "Reason Why")
        y = k.callout(sl, "Es la razón que da una marca para que el consumidor se crea lo que ésta le dice.", y + 26)
        k.lead(sl, d["reason_why"], y + 26)

    # Personificación
    if d.get("personificacion"):
        sl = k.page("Personificación")
        y = k.head(sl, "Personificación de la marca")
        k.lead(sl, d["personificacion"], y + 30)

    # Personalidad
    p = d.get("personalidad") or {}
    if p:
        sl = k.page("Personalidad")
        y = k.head(sl, "Personalidad de la marca")
        ih = text_h(p.get("intro"), BODY, False, 18, 1000, 1.6)
        text(sl, 120, y + 18, 1000, ih + 4, p.get("intro"), size=18, color=MUTED, ls=1.6)
        k.cards(sl, p.get("rasgos", []), y + 18 + ih + 30)

    # Brand mantra
    if d.get("brand_mantra"):
        sl = k.page("Brand Mantra")
        y = k.head(sl, "Brand Mantra")
        y = k.callout(sl, "Es la idea interna de marca capaz de sintetizar la razón de ser de su existencia, que refleja "
                          "nuestra esencia, nuestras intenciones y nuestra forma de entender el entorno.", y + 26)
        mantra = str(d["brand_mantra"]).strip().strip('"“”')
        size = fit(mantra, HEAD, True, 64, 1040, 664 - y - 64, 1.2, 32, track=-0.03)
        lines = wrap(mantra, HEAD, True, size, 1040, track=-0.03)
        f = _font(HEAD, True, size)
        ly = y + 64
        for ln in lines:  # resaltado tipo Notion, una barra por línea
            lw = f.getlength(ln) - 0.03 * size * len(ln)
            rect(sl, 112, ly + size * 0.1, lw + 18, size * 1.08, k.Ysoft, radius=6)
            ly += size * 1.2
        text(sl, 120, y + 64, 1080, size * 1.2 * len(lines) + 10, "\n".join(lines), family=HEAD, size=size,
             color=INK, bold=True, ls=1.2, spacing=-size * 0.03)

    # Tono de voz
    t = d.get("tono_de_voz") or {}
    if t:
        q = f"¿Cómo habla {marca}?"
        sl = k.page("Tono de voz")
        y = k.head(sl, "Tono de voz", q)
        ih = text_h(t.get("intro"), BODY, False, 18, 1000, 1.6)
        text(sl, 120, y + 18, 1000, ih + 4, t.get("intro"), size=18, color=MUTED, ls=1.6)
        k.cards(sl, t.get("dimensiones", []), y + 18 + ih + 30)
        ej = t.get("ejemplos", [])
        if ej:
            sl = k.page("Tono de voz")
            k.sec -= 1
            y = k.head(sl, "Guía de estilo", f"Tono de voz · {q}") + 30
            widths = [230, 405, 405]
            rows = [["Situación", f"DICE   Lo que {marca} dice", f"EVITA   Lo que {marca} evita"]] + \
                   [[e.get("situacion", ""), "“" + str(e.get("dice", "")).strip('"“”') + "”",
                     "“" + str(e.get("evita", "")).strip('"“”') + "”"] for e in ej]
            fs = 16
            while True:
                hs = [max(text_h(r[c], BODY, False, fs, widths[c] - 32, 1.5) for c in range(3)) + 30 for r in rows[1:]]
                if sum(hs) + 40 <= 664 - y or fs <= 11:
                    break
                fs -= 0.5
            tbl = sl.shapes.add_table(len(rows), 3, E(120), E(y), E(sum(widths)), E(40 + sum(hs))).table
            tbl_el = tbl._tbl
            tbl_el.tblPr.set("firstRow", "0")
            tbl_el.tblPr.set("bandRow", "0")
            sid = tbl_el.tblPr.find(qn("a:tableStyleId"))
            if sid is None:
                sid = etree.SubElement(tbl_el.tblPr, qn("a:tableStyleId"))
            sid.text = "{2D5ABB26-0587-4C30-8999-92F81FD0307C}"  # sin estilo, sin grilla
            for c, w in enumerate(widths):
                tbl.columns[c].width = E(w)
            tbl.rows[0].height = E(40)
            for r_i, h in enumerate(hs, 1):
                tbl.rows[r_i].height = E(h)
            for r_i, row in enumerate(rows):
                for c_i, val in enumerate(row):
                    cell = tbl.cell(r_i, c_i)
                    cell.fill.solid()
                    cell.fill.fore_color.rgb = RGBColor.from_string(WHITE)
                    cell.margin_left = cell.margin_right = E(16)
                    cell.margin_top = E(12 if r_i else 10)
                    cell.margin_bottom = E(10)
                    _cell_borders(cell, bottom=True, top=(r_i == 0), left=(c_i > 0))
                    tf = cell.text_frame
                    tf.word_wrap = True
                    par = tf.paragraphs[0]
                    par.line_spacing = 1.5 / LH
                    if r_i == 0 and c_i > 0:
                        tag, rest = val.split("   ", 1)
                        _run(par, tag + "  ", BODY, 11, k.G if c_i == 1 else FAINT, True)
                        _run(par, rest, BODY, 14, MUTED, False)
                    elif r_i == 0:
                        _run(par, val, BODY, 14, MUTED, False)
                    else:
                        _run(par, val, BODY, fs, MUTED if c_i != 1 else INK, c_i == 0 and False)

    # Posicionamiento
    if d.get("posicionamiento"):
        sl = k.page("Posicionamiento")
        y = k.head(sl, "Posicionamiento")
        k.quote(sl, d["posicionamiento"], y + 34)

    # Divisor
    sl, y = k.cover_like(k.B, [("ci", k.Y), ("sq", k.G)], "→", "Sobre la identidad visual")
    x = 120
    for lab in ("Benchmark", "Moodboard", "Type board", "Concepto"):
        w = _font(BODY, False, 15).getlength(lab) + 26
        rect(sl, x, y, w, 30, BG2, radius=6)
        text(sl, x, y, w, 30, lab, size=15, align="c", anchor="m", ls=1)
        x += w + 8

    VX, VY, VW = 72, 96, 360           # columna de texto en páginas visuales
    GX, GY, GW, GH = 480, 96, 752, 580  # galería

    def vhead(sl, title, label):
        return k.head(sl, title, label, x=VX, y=VY, width=VW, size=44)

    # Benchmark
    b = d.get("benchmark") or {}
    if b:
        sl = k.page("Benchmark")
        y = vhead(sl, "Benchmark", b.get("subtitulo"))
        y += 22
        marcas = b.get("marcas", [])
        bs = 15
        while bs > 11 and sum(text_h(m.get("motivo"), BODY, False, bs, VW, 1.55) + 50 for m in marcas) > 676 - y:
            bs -= 0.5
        for m in marcas:
            rect(sl, VX, y, VW, 1, LINE)
            text(sl, VX, y + 12, VW, 22, m.get("nombre"), family=HEAD, size=17, color=INK, bold=True, ls=1.2)
            hh = text_h(m.get("motivo"), BODY, False, bs, VW, 1.55)
            text(sl, VX, y + 38, VW, hh + 4, m.get("motivo"), size=bs, ls=1.55)
            y += hh + 50
        imgs = [r for r in (resolve(i, base) for i in b.get("imagenes", [])) if r]
        names = b.get("referentes_visuales") or [m.get("nombre") for m in marcas]
        items = imgs if imgs else names
        gallery(sl, k, items[:9], bool(imgs), kind="logo")

    # Moodboard
    m = d.get("moodboard") or {}
    if m:
        sl = k.page("Moodboard")
        y = vhead(sl, "Moodboard", "Guía visual para comunicar conceptos estéticos") + 22
        pal = m.get("paleta", [])
        pcols = len(pal) if len(pal) <= 5 else 4
        prow = (len(pal) + pcols - 1) // pcols if pal else 0
        pal_h = prow * 96 if pal else 0
        s = fit(m.get("texto"), BODY, False, 16, VW, 676 - y - pal_h - 20, 1.65, 11)
        th = text_h(m.get("texto"), BODY, False, s, VW, 1.65)
        text(sl, VX, y, VW, th + 4, m.get("texto"), size=s, ls=1.65)
        y += th + 22
        if pal:
            sw = (VW - 8 * (pcols - 1)) / pcols
            for i, c in enumerate(pal[:8]):
                sx = VX + (i % pcols) * (sw + 8)
                sy = y + (i // pcols) * 96
                rect(sl, sx, sy, sw, 52, hx(c.get("hex", "#CCCCCC")), radius=8, line=LINE)
                text(sl, sx, sy + 58, sw, 16, c.get("nombre", ""), size=12, color=INK, bold=True, ls=1.2)
                text(sl, sx, sy + 74, sw, 14, c.get("hex", ""), size=11, color=MUTED, ls=1.2)
        imgs = [r for r in (resolve(i, base) for i in m.get("imagenes", [])) if r]
        caps = m.get("descripcion_imagenes", [])
        n = 6
        cw = (GW - 3 * 12) / 4
        rh = (GH - 12) / 2
        spans = [2, 1, 1, 1, 1, 2]
        pos, cx, cy = [], 0, 0
        for sp in spans:
            if cx + sp > 4:
                cx, cy = 0, cy + 1
            pos.append((GX + cx * (cw + 12), GY + cy * (rh + 12), sp * cw + (sp - 1) * 12, rh))
            cx += sp
        for i, (px_, py_, pw, ph) in enumerate(pos[:n]):
            if i < len(imgs):
                picture(sl, imgs[i], px_, py_, pw, ph)
            elif not imgs and i < len(caps):
                placeholder(sl, px_, py_, pw, ph, caps[i])
            elif not imgs:
                placeholder(sl, px_, py_, pw, ph, "")

    # Type board
    tb = d.get("type_board") or {}
    if tb:
        sl = k.page("Type board")
        y = vhead(sl, "Type board", "Guía tipográfica de la marca") + 22
        s = fit(tb.get("texto"), BODY, False, 16, VW, 676 - y, 1.65, 11)
        text(sl, VX, y, VW, 676 - y, tb.get("texto"), size=s, ls=1.65)
        imgs = [r for r in (resolve(i, base) for i in tb.get("imagenes", [])) if r]
        if imgs:
            gallery(sl, k, imgs[:6], True, kind="spec")
        else:
            fonts = tb.get("fuentes", [])[:6]
            cols, rows_ = 3, max(1, (len(fonts) + 2) // 3)
            cw = (GW - 2 * 14) / cols
            chh = (GH - (rows_ - 1) * 14) / rows_
            bgs = [(k.Ywash, INK, MUTED), (k.B, WHITE, "C9D5FF"), (k.Gsoft, INK, MUTED)]
            for i, f in enumerate(fonts):
                fx = GX + (i % cols) * (cw + 14)
                fy = GY + (i // cols) * (chh + 14)
                bg, ink, sub = bgs[i % 3]
                rect(sl, fx, fy, cw, chh, WHITE, radius=10, line=LINE)
                rect(sl, fx, fy, cw, chh - 36, bg, radius=10, shape=MSO_SHAPE.ROUND_2_SAME_RECTANGLE)
                name = f.get("nombre", "")
                mid = fy + (chh - 36) / 2
                fimg = resolve(f.get("imagen"), base)
                if fimg:  # fuente que Slides no tiene (p. ej. la del logo): muestra como imagen
                    rect(sl, fx + 1, fy + 1, cw - 2, chh - 38, WHITE, radius=10, shape=MSO_SHAPE.ROUND_2_SAME_RECTANGLE)
                    picture_contain(sl, fimg, fx + 18, fy + 18, cw - 36, chh - 72)
                else:
                    text(sl, fx + 20, mid - 50, cw - 40, 70, f.get("muestra", "Aa"), family=name, size=62, color=ink, ls=1)
                    text(sl, fx + 20, mid + 26, cw - 40, 20, "ABCDEFG abcdefg 0123", family=name, size=13, color=sub, ls=1.2)
                text(sl, fx + 12, fy + chh - 36, cw - 24, 36, None, anchor="m", ls=1, size=13,
                     runs=[(f.get("etiqueta", name), INK, True), ("   " + f.get("rol", ""), MUTED, False)])

    # Concepto
    c = d.get("concepto") or {}
    if c:
        sl = k.page("Concepto")
        img = resolve(c.get("imagen"), base)
        landscape = img is not None and Image.open(img).size[0] / Image.open(img).size[1] > 1.3
        if landscape:  # imagen horizontal (p. ej. un sistema de logos): texto arriba, imagen abajo a lo ancho
            y = k.head(sl, c.get("nombre"), "Sobre el concepto", size=56)
            ty = y + 24
            s_ = fit(c.get("texto"), BODY, False, 19, 1040, 170, 1.55, 13)
            th = text_h(c.get("texto"), BODY, False, s_, 1040, 1.55)
            text(sl, 120, ty, 1040, th + 4, c.get("texto"), size=s_, ls=1.55)
            iy = ty + th + 24
            rect(sl, 120, iy, 1040, 680 - iy, WHITE, radius=10, line=LINE)
            picture_contain(sl, img, 140, iy + 16, 1000, 680 - iy - 32)
        else:
            y = k.head(sl, c.get("nombre"), "Sobre el concepto", width=556, size=56)
            k.lead(sl, c.get("texto"), y + 30, width=556, size=21)
        if landscape:
            pass
        elif img:
            picture(sl, img, 740, 108, 420, 556)
        else:
            placeholder(sl, 740, 108, 420, 556, c.get("descripcion_imagen", "Imagen de referencia del concepto"))

    # Gracias
    sl, y = k.cover_like(k.G, [("ci", k.B), ("sq", k.Y)], initial, "Gracias", 96)
    contact = " · ".join(x for x in [dis.get("nombre"), dis.get("rol"), d.get("contacto")] if x)
    text(sl, 120, y - 6, 1040, 26, contact, size=18, color=MUTED, ls=1.2)

    # números de página
    total = len(k.slides)
    for n, (sl, is_page, _) in enumerate(k.slides, 1):
        if is_page:
            text(sl, 1040, 17, 200, 20, f"{n:02d} / {total:02d}", size=13, color=FAINT, align="r", ls=1.2)
    return k.prs


def gallery(sl, k, items, are_images, kind="logo"):
    GX, GY, GW, GH = 480, 96, 752, 580
    cols = 3
    rows_ = max(1, (len(items) + cols - 1) // cols)
    gap = 14
    cw = (GW - gap * (cols - 1)) / cols
    ch = (GH - gap * (rows_ - 1)) / rows_
    for i, it in enumerate(items):
        x = GX + (i % cols) * (cw + gap)
        y = GY + (i // cols) * (ch + gap)
        rect(sl, x, y, cw, ch, WHITE, radius=10, line=LINE)
        if are_images:
            picture_contain(sl, it, x + 18, y + 18, cw - 36, ch - 36)
        else:
            rect(sl, x + 1, y + 1, cw - 2, ch - 37, BG2, radius=10, shape=MSO_SHAPE.ROUND_2_SAME_RECTANGLE)
            text(sl, x, y, cw, ch - 36, "Logo", size=12, color=FAINT, align="c", anchor="m", ls=1)
            rect(sl, x, y + ch - 36, cw, 1, LINE)
            text(sl, x + 12, y + ch - 36, cw - 24, 36, it, size=13, color=INK, bold=True, anchor="m", ls=1)


def _run(par, t, family, size, color, bold):
    r = par.add_run()
    r.text = t
    r.font.name, r.font.size, r.font.bold = family, Pt(size * 0.75), bold
    r.font.color.rgb = RGBColor.from_string(hx(color))


def _cell_borders(cell, top=False, bottom=False, left=False, right=False):
    tcPr = cell._tc.get_or_add_tcPr()
    for tag, on in (("a:lnL", left), ("a:lnR", right), ("a:lnT", top), ("a:lnB", bottom)):
        ln = etree.SubElement(tcPr, qn(tag), w=str(9525) if on else "0")
        if on:
            sf = etree.SubElement(ln, qn("a:solidFill"))
            etree.SubElement(sf, qn("a:srgbClr"), val=LINE)
        else:
            etree.SubElement(ln, qn("a:noFill"))
    # el orden del esquema exige que los bordes vayan antes del relleno
    fill = tcPr.find(qn("a:solidFill"))
    if fill is not None:
        tcPr.remove(fill)
        tcPr.append(fill)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("contenido")
    ap.add_argument("salida")
    a = ap.parse_args()
    src = Path(a.contenido).resolve()
    d = json.loads(src.read_text(encoding="utf-8"))
    prs = build(d, src.parent)
    prs.save(a.salida)
    print(f"Presentación generada: {a.salida}")


if __name__ == "__main__":
    main()
