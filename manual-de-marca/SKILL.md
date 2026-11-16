---
name: "manual-de-marca"
description: "Crea el manual de marca (brandbook) como deck de Slides a partir del logo SVG y la propuesta de branding ya aprobada: versiones del logo, retícula, área de protección, tamaños mínimos, color CMYK/Pantone, tipografía con licencias y .zip del logo. Úsala cuando pidan un brandbook, manual de marca, manual de identidad, guía de uso del logo o normas de marca, aunque no digan \"manual\". No la uses para crear la estrategia (eso es propuesta-branding) ni para mostrar la marca aplicada en piezas (eso es brand-board)."
---

# Manual de marca

Conviertes una identidad ya decidida (logo + estrategia) en un manual normativo:
el documento que le dice al cliente, a su equipo y a sus proveedores cómo usar
la marca sin que la diseñadora esté presente. El manual **documenta
decisiones**; no las toma por su cuenta. Por eso esta skill pregunta mucho y
genera poco sin aprobación: cada cosa que el manual afirma tiene que poder
defenderse ante el cliente.

Ritmo de toda la skill: **una pregunta a la vez, siempre con tu recomendación y
una línea de por qué**. Cuando la persona acepte sin discutir, nombra en una
frase lo que implica (el costo) y sigue. Lleva la cuenta en voz alta ("Bloque 3
de 6 — Color"). Si algo se puede averiguar mirando (el PPT, el SVG, la web de
una licencia), averígualo en vez de preguntar.

## Herramientas

La skill usa scripts y guías propios, en `scripts/` y `references/` junto a
este archivo. Los scripts usan Python con Playwright/Chromium, Pillow, numpy y scipy;
`text_to_svg.py` necesita además `uharfbuzz` (`pip install --break-system-packages uharfbuzz`).
Todos aceptan `-h`. Guías:
- `references/entrevista.md`: banco de preguntas en orden, con la recomendación por defecto.
- `references/nucleo.md`: páginas del manual básico.
- `references/modulos.md`: módulos extendidos (tomados como referencia del manual público de la FIFA World Cup 26).
- `references/esqueleto-slides.md`: maqueta editorial fija y construcción técnica del deck.

Lleva una lista de tareas visible (análisis, entrevista, versiones, constructivo,
color, deck, paquete): el trabajo es largo y la persona puede irse y volver.

## Fase 0 — Entradas obligatorias

Pide en un solo mensaje lo que falte:

1. **El logo en SVG**, con el texto en contornos. Si solo hay PNG/JPG, para: sin SVG no se mide ni se generan versiones fiables. Pide también cualquier otro SVG que exista (otras versiones, retícula constructiva).
2. **La presentación de branding** previa: Google Slides (la que produce `propuesta-branding`), .pptx o PDF. Si no existe, **detente** y sugiere correr `propuesta-branding`: el manual no inventa estrategia.

Lee la presentación (para .pptx, `python -m markitdown` o python-pptx; extrae
también las imágenes de las páginas de identidad visual y míralas: ahí suelen
estar el sistema de logo, la paleta aplicada y las piezas). Arma una ficha:
quiénes somos, misión, visión, valores, personalidad, tono (dice / evita),
posicionamiento, mantra, concepto del logo, moodboard, type board, paleta,
tipografías y **reglas implícitas** (por ejemplo "el nombre siempre en negro, el
prefijo cambia de color"). Si falta un campo que el manual necesita, pregunta solo por
ese campo. Si un color aparece sin HEX legible, muestréalo de la imagen y
pídele confirmación.

## Fase 1 — Analizar el SVG

```bash
python scripts/svg_inspect.py logo.svg trabajo/inspeccion/
```

Muestra `inspeccion.png` y propón los grupos. Normalmente son isotipo /
logotipo / tagline, pero **si la identidad es dinámica** (una parte cambia de
color por sub-marca, edificio, sede…), agrupa por **regla de color**: lo que
cambia, lo que es fijo y lo que acompaña al que cambia. Así cada variante se
genera con una sola instrucción. Confírmalos y guárdalos en
`trabajo/grupos.json` (por ejemplo `{"prefijo": ["1-4"], "nombre": ["5-10"], "simbolo": [0]}`).
Atiende las ALERTAS: texto vivo, trazos sin expandir, degradados, imágenes incrustadas.

## Fase 2 — Entrevista

Sigue `references/entrevista.md` (6 bloques: alcance → logo → color →
tipografía → lenguaje visual y aplicaciones → control del documento). Puedes dar
por resueltas en un mismo mensaje las decisiones de bajo riesgo ("asumo X salvo
que me corrijas"); las que cuestan caro de revertir van solas.

Al terminar, **presenta el índice resultante** (núcleo + módulos, con número de
página) y espera aprobación antes de producir nada.

## Fase 3 — Versiones del logo (siempre con aprobación previa)

**Variantes de color.** Genera la propuesta y muéstrala como hoja; luego una
tabla: grupo de variantes · cómo se resuelve · uso, más las decisiones que
tomaste. Las dudas típicas que debes plantear o resolver con la tabla de
contraste de la Fase 5:
- En negativo, ¿el color se mantiene o pasa a blanco? Un negativo en color solo existe si ese color contrasta con el fondo oscuro (≥ 3:1); si no, monocromo blanco.
- Sobre un fondo que es un color de la propia paleta, el logo va en **una sola tinta** (negro o blanco), nunca en otro color de la paleta.
- En un color, ¿algún detalle interior se funde con la forma de detrás? Propón **calarlo** (`"calar"` en el spec).
- En identidades dinámicas: ¿la pieza acompañante (el símbolo, por ejemplo) puede tomar un color distinto? Recomienda que no (una pieza = un color) y nombra el costo.

```bash
python scripts/logo_variants.py logo.svg trabajo/variantes.json trabajo/versiones/ --version apilada
```

**Recomposiciones** (horizontal ↔ vertical, símbolo solo, avatar, lock-ups):
1. Pregunta si ya existe el SVG; si existe, úsalo.
2. Si no, componla con `compose.py`: **solo reubica, escala y separa piezas existentes; nunca redibuja**. Para pasar de dos líneas a una, usa `"alinear": "base"` con la línea base de cada grupo (pie de una letra sin descendente) y una separación igual al espacio entre letras dentro de la palabra, para que se lea como una sola palabra.
3. Muestra la vista previa (en el avatar, también `_circulo.png`; para el favicon, la prueba a 32 y 16 px) y espera aprobación **una por una**.
4. Ya aprobada, genera sus variantes componiendo cada variante de color aprobada (bucle sobre los SVG de la versión principal).

**Lock-ups con texto** (slogan, nombre de sub-marca o edificio): convierte el
texto a contornos con la tipografía de marca, sin depender de la fuente
instalada, y súmalo como pieza externa:
```bash
python scripts/text_to_svg.py "Conecta. Vive. Pertenece." fuente.woff trabajo/slogan.svg --color "#1D1D1B"
```
(las fuentes de Google Fonts se obtienen con `npm i @fontsource/<familia>`; usa el `.woff`).
En `compose.py`, `"externos": {"slogan": "trabajo/slogan.svg"}` y `"ancho": {"slogan": "logo"}`
igualan el ancho al del logo. Para una sub-marca sin nombre definido, deja un
marcador ("[Nombre]") y normaliza la estructura, no cada caso. El texto del
lock-up va en la tinta de la parte fija del logo, nunca en el color variable.

Usos incorrectos, con el logo real (`--fondo-malo`: el color de la paleta con
peor contraste para la versión principal):
```bash
python scripts/incorrect_uses.py trabajo/versiones/<principal>.svg trabajo/incorrectos/ --grupos g.json --nombre "<marca>" --fondo-malo "#2B57E2"
```
(`g.json` necesita un grupo `isotipo` con el símbolo y el resto como `logotipo`).

## Fase 4 — Retícula, protección y tamaño mínimo

1. **Pregunta si la persona tiene retícula constructiva y pide su SVG.** Si la tiene, úsala tal cual. Si no:
2. `python scripts/construction.py candidatos logo.svg trabajo/constructivo/ --grupos trabajo/grupos.json` y muestra los candidatos en una sola hoja. Suele funcionar bien **combinar dos**: el grosor del trazo como módulo del plano (cae sobre las astas) y el ancho del símbolo como medida del área de protección ("deja libre el espacio de un símbolo", fácil de explicar a cualquier proveedor). Cobranding: el doble.
3. `python scripts/construction.py plano <versión>.svg trabajo/constructivo/<versión> --modulo <u> --proteccion <módulos>` por cada versión.
4. `python scripts/min_size.py <versión>.svg trabajo/minimos/<versión> --grupos g.json` (g.json con `logotipo` y, si hay, `tagline`). Si hay ranuras finas (la cruz de un símbolo), el script da **dos umbrales**: [completo] todo se lee / [legible] el nombre se lee y el símbolo queda como un punto. Arma una hoja de prueba con cada versión a varios tamaños (real y ampliado) y deja que la persona elija. Lo habitual: el mínimo oficial es el [legible], y en formatos chicos (firma, fotocheck) el símbolo aparece además aparte y en grande.

## Fase 5 — Sistema de color

1. Arma `trabajo/colores.json`: un HEX fuente por color, rol, y los RGB/CMYK/Pantone que vengan del material de origen, para validarlos.
2. Si la persona **no tiene Pantone validados**, ofrécete a hacer el trabajo: `python scripts/pantone_ref.py trabajo/colores.json trabajo/pantone_ref.json` (Pantone C y textil TCX más cercanos por ΔE 2000). Copia el resultado a `colores.json` y preséntalo en una tabla con el ΔE: < 2 casi idéntico, 2–5 parecido, > 5 se nota, > 10 sin equivalente.
3. `python scripts/color_system.py trabajo/colores.json trabajo/color/`: convierte a CMYK con el perfil FOGRA39 si lo encuentra, avisa de los colores fuera de gama (cómo se verán impresos), valida RGB/HEX, calcula escalas 50–950 y la matriz de contraste.
4. **Presenta las ALERTAS antes de diseñar.** Explica qué colores salen apagados en CMYK y dónde conviene Pantone directo (stickers, señalética). Todo Pantone/TCX calculado va en el manual como "referencia, validar con guía física y prueba de color". Nunca lo presentes como oficial. En negro, distingue negro enriquecido (áreas grandes) de 0/0/0/100 (textos).
5. La matriz de contraste decide la tinta de texto y la del logo sobre cada fondo. Si el PPT dice "X siempre en negro" y el contraste lo impide en algún fondo, dilo y propón la regla corregida ("X en la tinta que contraste").

## Fase 6 — Tipografía y licencias

Busca la licencia de cada fuente en la web antes de preguntar:
- Google Fonts / OFL: lista.
- "Gratis para uso personal": no cubre un logo comercial. Pregunta de dónde la sacó.
- **Envato Elements**: cubre logos, pero **hay que registrar la fuente para ese proyecto** mientras la suscripción esté activa y guardar el certificado PDF. Si no lo hizo, es el pendiente más importante; pon en el manual un marcador del código de licencia.
- Restringida a un sistema (por ejemplo SF Pro): avisa y propón una alternativa libre.

La fuente del logotipo, si se entrega en contornos, se declara "solo en el arte
del logo; no se instala". Define una **fuente de respaldo** (Google Docs/Canva y
Word) y la **jerarquía** con ejemplos escritos con la voz de la marca.

**Ilustraciones de terceros** (bancos, comunidad de Figma): revisa también su
licencia (Streamline Free, por ejemplo, exige atribución, permite 25 por
proyecto y prohíbe redistribuirlas). Si no se pueden entregar a terceros, el
manual las muestra como estilo de referencia con el crédito, y no van en el .zip.
Para traerlas de Figma usa el conector oficial (`create_session` →
`get_metadata` → `get_screenshot` con base64; el archivo queda guardado en
disco). En el plan Starter las llamadas son limitadas: ubica y elige antes de
descargar. Si el conector local de Figma devuelve "Token expired", el token
se cambia en la configuración de la app (o en Settings → Extensions), no en el
archivo; mientras tanto usa el conector oficial o pide la exportación.

## Fase 7 — Construir el deck

Lee `references/esqueleto-slides.md`. Crea el deck desde el tipo Slides
(título: "Manual de marca – <Marca>") y sigue sus instrucciones de archivos:

1. Renderiza a PNG transparente todo lo que va en el deck (versiones, planos, pruebas de mínimo, usos incorrectos, ilustraciones) y súbelo como recursos desde una carpeta del directorio de trabajo, hasta 25 por llamada.
2. `deck.json` primero, con el `order` completo (núcleo + módulos + separadores) y las fuentes de la marca en `faces` (Google Fonts); luego la portada, y después tandas de 6–8 páginas.
3. Textos de estrategia: del PPT, en registro de manual, sin agregar afirmaciones. Lo que falte va entre corchetes ("[correo]"), en la página y en las notas del orador.
4. Aplicaciones del rubro: constrúyelas en la slide con formas, el PNG del logo y textos de ejemplo con la voz de la marca. No son mockups fotográficos.
5. Revisa que el nombre de la marca sea el correcto en encabezados e índice.

## Fase 8 — Paquete de archivos

Copia a una carpeta solo los SVG aprobados, con nombre `<version>_<variante>.svg`
(sin vistas previas ni piezas sueltas), y corre:
```bash
python scripts/package.py trabajo/entrega/ trabajo/paquete/ --marca "<Marca>"
```
Genera SVG, PNG transparente 500/1000/2000 px y PDF vectorial por variante, en
RGB. Las versiones CMYK/Pantone, las simplificadas para bordado y el favicon de
16 px ajustado quedan como "pendientes de arte final". Envía el .zip con SendUserFile.

## Fase 9 — Entrega

Mensaje breve: el deck (su tarjeta ya lleva el enlace), el .zip y la **lista de
pendientes** agrupada por responsable (diseñadora / cliente / imprenta).
Ejemplos: registrar la licencia de la fuente, validar Pantone, el correo del
responsable de marca, el arte final para bordado, la licencia de las
ilustraciones. Como paso opcional, ofrece correr `brand-board` o producir las
plantillas.

## Ejemplo bien

Así se documenta una decisión en el manual: concreta, medible y con su estado.

```
Color · Azul
HEX #2B57E2 · RGB 43/87/226 · CMYK 85/65/0/0 (FOGRA39, sale algo apagado)
Pantone 2728 C · ΔE 3,1 (parecido). Referencia: validar con guía física y prueba de color.

Tamaño mínimo · Versión horizontal
24 mm / 90 px de ancho: el nombre se lee y el símbolo queda como punto.
Más chico (firma, fotocheck): usar el símbolo aparte y en grande.
```

## Ejemplo mal

```
Pantone oficial: 2728 C
No usar el logo demasiado pequeño.
```

Por qué está mal: presenta un Pantone calculado como oficial y sin ΔE, y el
mínimo no tiene medida, así que ningún proveedor puede comprobar si lo cumple.

## Lo que esta skill nunca hace

- Redibujar o "mejorar" el logo: solo recolorea, cala, reubica, escala y separa piezas existentes, y convierte a contornos textos nuevos.
- Crear una versión sin aprobación previa.
- Inventar estrategia, licencias o datos del cliente, ni presentar Pantones calculados como oficiales.
- Mezclar valores de color de fuentes distintas sin validarlos.