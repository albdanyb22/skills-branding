# Disposición del lienzo

Tamaños fijos (px): tablero 1920×1200 · afiche e informativa 720×1018 (proporción A) ·
post 864×1080 (4:5). Separación: 80 px entre artboards de una fila; cada fila
lleva un título (`notes`, `kind: "title1"`) unos 260-300 px por encima.

`project/canvas.json` de referencia: ajusta nombres, títulos y cantidad de piezas.
Pon `createdOnFiles.at` con la hora actual. `x` avanza: ancho + 80.

```json
{"v":3,"createdOnFiles":{"v":1,"at":"<AHORA RFC 3339>"},"title":"<Marca> — Brand board","launch":{"view":"canvas"},"pages":[],
"boards":{
"Main.dc.html":{"x":0,"y":0,"w":1920,"h":1200,"title":"Brand board"},
"Afiche-<Color1>.dc.html":{"x":0,"y":1560,"w":720,"h":1018,"title":"Afiche · <Color1>"},
"Afiche-<Color2>.dc.html":{"x":800,"y":1560,"w":720,"h":1018,"title":"Afiche · <Color2>"},
"Afiche-<Color3>.dc.html":{"x":1600,"y":1560,"w":720,"h":1018,"title":"Afiche · <Color3>"},
"Informativo-<Color4>.dc.html":{"x":2400,"y":1560,"w":720,"h":1018,"title":"<Tipo de pieza> · <Color4>"},
"Post-<Color4>.dc.html":{"x":0,"y":2920,"w":864,"h":1080,"title":"Post · <Color4>"},
"Post-<Color5>.dc.html":{"x":944,"y":2920,"w":864,"h":1080,"title":"Post · <Color5>"},
"Post-<Color6>.dc.html":{"x":1888,"y":2920,"w":864,"h":1080,"title":"Post · <Color6>"}
},
"order":["Main.dc.html","Afiche-<Color1>.dc.html","Afiche-<Color2>.dc.html","Afiche-<Color3>.dc.html","Informativo-<Color4>.dc.html","Post-<Color4>.dc.html","Post-<Color5>.dc.html","Post-<Color6>.dc.html"],
"notes":{
"t1":{"x":0,"y":-300,"text":"<Marca> — Brand board","kind":"title1","maxW":1920},
"t2":{"x":0,"y":1260,"text":"Afiches y piezas · un color por pieza","kind":"title1","maxW":3120},
"t3":{"x":0,"y":2620,"text":"Redes sociales","kind":"title1","maxW":2752}
},
"designSystems":[]}
```

Nombres de archivo sin tildes ni espacios (`Post-Ambar.dc.html`); los títulos sí
pueden llevarlos.

## Tokens de color de las plantillas

- `[[TINTA]]`: el negro de la marca (o `#1D1D1B`). `[[NEUTRO]]`: un crema o gris cálido
  claro que acompañe la paleta (p. ej. `#F4EFE6`). `[[GRIS]]`: texto secundario sobre
  blanco con contraste ≥ 4.5:1 (p. ej. `#5E5A54`). `[[BORDE]]`: un tono más oscuro del neutro.
- `[[TEXTO_SOBRE_COLOR]]`: tinta o `#FFFFFF`, según `palette_check.py`; el logo de esa
  pieza es la versión correspondiente (`logo-tinta.svg` / `logo-blanco.svg`).
- `[[LINEA_RETICULA]]`: `rgba(<tinta>, 0.09)` sobre fondos claros, `rgba(255,255,255,0.10)`
  sobre oscuros.
- `[[COLOR_LEGIBLE_SOBRE_BLANCO]]`: el color de la pieza si llega a 4.5:1 sobre blanco;
  si no (amarillos, verdes claros), la tinta.
