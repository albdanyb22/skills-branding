---
name: brand-board
description: 'Crea el brand board de una marca como diseño editable: un tablero principal (logotipo, paleta, sistema de logo, ilustración, símbolo, tipografía, voz y regla de color) más piezas de aplicación en tamaño real (afiches, una pieza informativa del rubro y posts para redes), cada una con un solo color protagonista. Usa el logo SVG, la paleta, las tipografías y las ilustraciones del usuario. Úsala siempre que pidan un brand board, tablero de marca, hoja de identidad, "mostrar la marca aplicada", mockups o piezas de ejemplo de una identidad, o aplicar un logo y paleta a afiches y posts, aunque no digan "brand board". No la uses para la estrategia o propuesta de marca en texto (eso es propuesta-branding), para el manual de marca o brandbook con normas de uso (eso es manual-de-marca), ni para diseñar el logo desde cero.'
---

# Brand board

Conviertes los elementos de una identidad (logo, paleta, tipografía,
ilustraciones, voz) en un brand board que muestra la marca viva: un tablero
principal y, al lado, piezas reales en las que se ve cómo se aplica.

La idea rectora es **mucho color, pero no todos a la vez**: el tablero muestra
la paleta completa, pero cada pieza usa **un color protagonista + tinta +
neutro**, y como mucho un acento pequeño. El conjunto se ve variado y
alegre; cada pieza por separado se ve limpia y reconocible. Si la marca tiene
pocos colores, la misma regla aplica alternando fondos de color, de neutro y
de tinta.

## 1 · Reúne lo necesario

Antes de preguntar, mira lo que ya está en la conversación o en archivos
adjuntos: una propuesta de branding (por ejemplo, la de la skill
propuesta-branding) ya trae paleta, tipografías, tono, mantra y frases; un logo
adjunto ya está resuelto. Pide en **un solo mensaje** solo lo que falte, con
tu recomendación en cada punto:

1. **Logo en SVG** (y el símbolo suelto, si existe). Si solo hay PNG o JPG,
   sirve, pero sin variantes de color: avisa que con SVG se pueden generar.
2. **Paleta** con hex. Si solo hay una imagen del logo, extrae los colores
   (muestrea los píxeles saturados por zona) y confírmalos.
3. **Tipografías:** la del logo y una pareja de Google Fonts para titulares y
   textos. Si la del logo no está en Google Fonts, propón una parecida para el
   día a día y presenta la del logo con la imagen del propio logo.
4. **Ilustraciones** (opcionales, pero cambian mucho el resultado):
   - Un **.zip** con una selección: lo más práctico. Si la librería es enorme,
     pide que exporten solo una carpeta o tema, o recibe el zip completo y
     filtra tú (paso 2).
   - Si están en **Figma**: hay un conector de Figma para Claude. Si no está
     activo, sugiere activarlo y pedir el enlace del frame; mientras tanto, el
     zip sirve igual.
   - Sin ilustraciones: las piezas se resuelven con el símbolo, formas planas
     del color y tipografía grande. Dilo y sigue.
5. **Rubro y mensajes:** a qué se dedica la marca (define la pieza
   informativa: comunicado, menú, horario, ficha, invitación…), su frase o
   tagline y 3-4 temas de los que habla (pilares).

Si la persona no está o no responde, decide con lo que hay y anota los
supuestos en el mensaje final.

## 2 · Prepara los recursos

Los scripts están en `scripts/` (Python; usan Pillow, numpy, scipy y
Playwright/Chromium).

**Paleta.** Guarda `paleta.json` (`[{"nombre","hex"}]`) y corre
`python scripts/palette_check.py paleta.json`. Te dice, para cada color, si el
texto y el logo van en tinta o en blanco, con su contraste. Respétalo: es lo
que mantiene legibles las piezas.

**Logo.**
1. `python scripts/logo_variants.py inspect logo.svg <dir>` y mira
   `<dir>/inspeccion.png`: cada forma del logo aparece numerada.
2. Decide qué formas cambian de color. En un logo dinámico es la parte
   variable (una palabra, el símbolo); en un logo de un solo color, todas (sin
   `--acento`).
3. `python scripts/logo_variants.py build logo.svg paleta.json <dir> --acento 0,1,2`
   genera `logo-<color>.svg` por color, más `logo-tinta.svg` y `logo-blanco.svg`.
   Haz lo mismo con el símbolo (`--prefijo simbolo`, sin `--acento`).

**Ilustraciones.**
1. `python scripts/illustrations.py sheet archivo.zip [otro.zip] <dir> --filtro "palabras,clave"`
   arma hojas de contactos numeradas (`hoja-N.png`). El filtro busca en los
   nombres de archivo: úsalo con palabras del rubro y de los pilares (en el
   idioma de los archivos). Mira las hojas y elige 8-12 que cuenten la vida
   de la marca, variadas en escena y en peso visual.
2. `python scripts/illustrations.py prep <dir>/indice.json <dir>/listas --elegir 3,7,12 --nombres fiesta,cafe,balcon`
   - `--modo recorte` (por defecto) quita solo el fondo blanco exterior: las
     figuras conservan su relleno y funcionan sobre cualquier color.
   - `transparente`: deja solo las líneas.
   - `tal-cual`: para ilustraciones que ya traen fondo transparente.
   Revisa `_control.png` (cada una sobre un color) antes de seguir.
3. Recuerda a la persona revisar la licencia de uso comercial si las
   ilustraciones vienen de un pack gratuito.

## 3 · Planifica color y mensajes

Arma una tabla breve y muéstrala solo si la persona está presente y es útil
(si no, aplícala directamente):

| Pieza | Color | Texto/logo | Ilustración | Mensaje |
|---|---|---|---|---|

- Reparte los colores para que **cada color de la paleta protagonice al menos
  una pieza** y ninguno se repita hasta haberlos usado todos. Con 6 colores:
  3 afiches + 1 informativa + 3 posts dejan uno repetido en el tablero; está
  bien.
- La pieza informativa va sobre el neutro, con el color solo en franja,
  etiqueta y línea: muestra la versión sobria de la marca.
- Mensajes: titulares cortos (afiche ≤ ~45 caracteres, post ≤ ~40), en la
  voz de la marca, uno por pilar. Nada de datos inventados: nombres, fechas,
  precios y contactos van como `[EN MAYÚSCULAS]`.

## 4 · Construye el lienzo

El brand board es un diseño: créalo con el tipo **Design** de Artifact
(`quickstart` con intent `design`, luego crear desde ese tipo con título
"<Marca> — Brand board") y sigue las instrucciones que te devuelve el tipo:
cómo se escriben `project/canvas.json` y cada artboard, cómo se suben los
recursos y el orden de publicación.

- **Sube los recursos** (logos, símbolos, ilustraciones) como assets y usa
  las URL `/_blob/…` que devuelve.
- **Disposición del lienzo:** `references/lienzo.md` trae el `canvas.json` de
  referencia (tablero arriba, afiches + informativa en la segunda fila, posts
  en la tercera, con un título por fila).
- **Artboards:** parte de las plantillas de `assets/plantillas/`:
  - `Main.dc.html`: el tablero;
  - `Afiche.dc.html`;
  - `Informativo.dc.html`;
  - `Post.dc.html`, una por pieza.

  Lee cada plantilla, reemplaza todos los `[[TOKENS]]` y quita el comentario
  de instrucciones antes de escribir el archivo final. Mantén la estructura:
  tamaños, retícula, jerarquía y la regla de un color por pieza. Ajusta lo
  que la marca pida (radios más rectos para una marca seria, retícula fuera
  si no encaja, frase o pastilla en el post).
- **Sin tipo Design disponible:** construye una sola página HTML con el
  tablero y las piezas en filas, y publícala como artifact.

## Reglas

Se pueden comprobar pieza por pieza:

- Cada pieza tiene **un** color protagonista, más tinta y neutro. Como mucho, un acento pequeño.
- Cada color de la paleta protagoniza al menos una pieza.
- El texto y el logo van en la tinta que dice `palette_check.py` para ese fondo (≥ 4,5:1 para texto; entre 3:1 y 4,5:1, solo titulares grandes).
- Sobre un fondo de color de la paleta, el logo va en una sola tinta (negro o blanco), nunca en otro color de la paleta.
- Titulares: afiche ≤ ~45 caracteres, post ≤ ~40.
- Ningún dato inventado: nombres, fechas, precios y contactos van como `[EN MAYÚSCULAS]`.

## Ejemplo bien

```
Post 2 · fondo Mostaza · texto y logo en tinta (contraste 9,8:1)
Ilustración: balcón · Pilar: comunidad
Titular: "Tu edificio también tiene vecinos"   (33 caracteres)
CTA: [FECHA] · [LUGAR]
```

## Ejemplo mal

```
Post 2 · fondo Mostaza con franja Azul y logo en Coral
Titular: "Gran fiesta vecinal este sábado 14 a las 6 pm en el lobby, ¡no faltes!"
```

Por qué está mal: mezcla tres colores de la paleta en una pieza, pone el logo
en otro color sobre un fondo de color, el titular pasa los 40 caracteres y
la fecha, la hora y el lugar son inventados.

## 5 · Entrega

En pocas líneas:
- qué hay en el lienzo (tablero + qué piezas, con su color);
- cómo aplicaste la regla de color (qué fondos llevan logo en tinta y cuáles
  en blanco);
- qué quedó por completar (`[DATOS]`, imágenes faltantes);
- el aviso de licencia de las ilustraciones, si aplica.

No describas pieza por pieza lo que la persona puede ver en el lienzo.
