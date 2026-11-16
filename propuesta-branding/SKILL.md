---
name: "propuesta-branding"
description: "Entrevista a la persona con el brief de marca (27 preguntas en 5 bloques + preguntas complementarias), desarrolla la estrategia de marca y entrega una presentación de Google Slides \"Propuesta de branding\" con estructura fija (quiénes somos, misión, visión, valores, reason why, personificación, personalidad, brand mantra, tono de voz, posicionamiento, benchmark, moodboard, type board y concepto). Úsala siempre que pidan crear un branding, una propuesta de branding, identidad de marca, estrategia de marca o \"llenar el brief\" de un cliente, aunque no digan \"propuesta\", \"slides\" ni \"presentación\", y también cuando adjunten un brief de marca (.docx/.pdf) para convertirlo en propuesta. No la uses para el manual de marca o brandbook (eso es manual-de-marca), para mostrar la marca aplicada en piezas (eso es brand-board), ni para diseñar solo un logo, un post o editar una presentación existente."
---

# Propuesta de branding

Conviertes un brief de marca en una propuesta de branding estratégica, lista para
presentar al cliente, como presentación de Google Slides 16:9 (totalmente
editable) con estética tipo Notion: fondo blanco, mucho
aire, tipografía grotesk (Inter Tight en titulares, Inter en texto), breadcrumbs,
propiedades, callouts, citas y vistas de galería. Color: amarillo como acento
principal, con azul vibrante y verde como secundarios (se alternan por página).

El trabajo tiene cuatro fases. La entrevista es la parte más valiosa: la calidad
de la propuesta depende de lo que se saque del cliente, y los briefs suelen venir
con respuestas cortas o evasivas.

## Fase 1 — Brief

Lee `references/brief.md` antes de la primera pregunta.

**Si adjuntaron un brief lleno** (docx, pdf, texto): extráelo (para .docx,
`pandoc archivo.docx -t markdown`), mapea cada respuesta a su número y pasa
directo a la fase 2 mostrando un resumen corto de lo que ya está cubierto.

**Si no hay brief**, entrevista siguiendo los 5 bloques en orden
(MARCA → CLIENTES → COMPETENCIA → PROYECTO → NOTAS):

- Un bloque a la vez, anunciando dónde están ("Bloque 2 de 5 — Clientes").
  Dentro del bloque puedes agrupar 2-4 preguntas cortas y relacionadas en un
  mismo mensaje; las preguntas de fondo (propuesta de valor, diferenciador,
  qué debe transmitir el logo) van solas, porque son las que la gente responde
  a la ligera si van en lista.
- Mantén la numeración original (1-27) para que la persona reconozca su brief.
- Si la persona ya respondió algo antes en la conversación, no lo repitas:
  confírmalo de paso.
- Si la persona pide ir rápido, acepta respuestas en bloque.

## Fase 2 — Completar huecos

Con el brief respondido, revisa qué falta para llenar cada lámina
(`references/contenido.md` dice de dónde sale cada una) y:

1. **Repregunta las respuestas débiles** — fuera de tema, genéricas,
   contradictorias o "no sé". Ver criterios en `references/brief.md` §3.
   Repregunta con una propuesta concreta para que reaccionen ("Propongo X, ¿va?").
2. **Haz las preguntas complementarias** (§2 de `brief.md`) que sigan abiertas.
   Las más importantes son las pruebas para el Reason Why (C, D), la
   personificación (E) y los colores prohibidos (J). Pide que adjunten imágenes
   o logos de referencia si los tienen (K).

Estilo grill-me: cada pregunta lleva tu recomendación y su porqué en una línea;
si la persona acepta sin discutir, nombra en una frase lo que implica y sigue.
Si se cansa ("lo que tú veas"), ofrece cerrar con tus recomendaciones como
valores por defecto y marcarlas como supuestos.

## Fase 3 — Estrategia (borrador para aprobar)

Lee `references/contenido.md` y redacta el contenido de las 14 láminas de texto.
Muéstralo en el chat como borrador compacto, lámina por lámina, antes de generar
la presentación. Destaca los 3-4 puntos que más merecen revisión (mantra, concepto,
personificación, paleta) y señala cualquier supuesto que hiciste.

Hazlo así porque regenerar la presentación es barato pero el cliente final verá estos
textos: es mejor que la persona los corrija en texto plano.

Aplica las correcciones. Si no hay respuesta (sesión desatendida), sigue con tu
borrador y deja los supuestos anotados en el mensaje final.

## Fase 4 — Google Slides

La presentación se construye como .pptx con formas, textos y tablas nativas
(nada rasterizado) pensada para convertirse a Google Slides: usa fuentes de
Google (Inter Tight, Inter y las del type board por nombre) y evita efectos que
Slides descarta (sombras, autoajuste de texto). Luego se sube a Drive y Drive la
convierte.

1. Escribe el JSON según `references/esquema-json.md` (ejemplo completo en
   `references/ejemplo-vecindia.json`). Si adjuntaron imágenes, cópialas junto
   al JSON y referéncialas en `benchmark.imagenes`, `moodboard.imagenes`,
   `type_board.imagenes` o `concepto.imagen`.
2. Genera:
   ```bash
   python <skill>/scripts/build_slides.py contenido.json "Propuesta de branding - <Marca>.pptx"
   ```
   Google Slides no reduce el texto para que quepa, así que el script mide cada
   texto con las fuentes reales (`assets/fonts/*.ttf`) y elige el tamaño. Si
   imprime `[aviso] el texto no entra`, recorta ese texto y vuelve a generar.
3. **Revisa antes de entregar.** Convierte a PDF solo para mirar
   (`soffice --headless --convert-to pdf`; en la sesión de Claude usa el
   wrapper `scripts/office/soffice.py` de la skill pptx) y `pdftoppm -r 50 -png`.
   Busca textos que se monten, letra demasiado chica y láminas vacías. Para
   que la vista previa use las fuentes correctas, copia antes
   `assets/fonts/*.ttf` a `~/.fonts` y corre `fc-cache -f`. Las fuentes del type
   board solo se verán bien en Google Slides; en la vista previa local es normal
   que salgan con una fuente de reemplazo.
4. **Pásala a Google Slides:**
   - **Con conexión a Google Drive disponible**: lee la skill `google-workspace`
     (sección de Slides, ruta "designed deck") y sube el .pptx con Drive
     `create_file` convirtiéndolo a `application/vnd.google-apps.presentation`,
     con el nombre "Propuesta de branding — <Marca>". Después exporta el
     resultado a PDF y revisa que la conversión no haya movido nada. Entrega el
     enlace a la presentación.
   - **Sin conexión a Drive**: entrega el .pptx y explica en una línea cómo
     abrirlo como Google Slides (Drive → Nuevo → Subir archivo → abrir con
     Google Slides; o en Slides: Archivo → Importar diapositivas). Menciona que,
     con Google Drive conectado, la próxima vez se crea directo en su Drive.
5. En una o dos líneas, di qué quedó como placeholder (imágenes del moodboard,
   logos del benchmark, imagen del concepto) para que la diseñadora las
   reemplace directamente en Slides — desde aquí no se pueden descargar
   imágenes de internet. Ofrece el JSON por si quiere regenerar tras editar.

## Ejemplo bien

Cada texto se puede rastrear a una respuesta del brief y solo sirve para esta marca.

```
Brand Mantra: Comunidad que se vive   (4 palabras · brief 7 y 24)
Valor — Cercanía: Conocemos a cada vecino por su nombre y diseñamos los
espacios comunes para que esos encuentros pasen solos.   (24 palabras · brief 6)
```

## Ejemplo mal

```
Brand Mantra: Calidad, innovación y confianza
Valor — Excelencia: Nos esforzamos cada día por dar lo mejor a nuestros clientes.
```

Por qué está mal: es genérico (sirve para cualquier marca), no sale de ninguna
respuesta del brief y el mantra es una lista de atributos, no una idea.

## Notas

- La plantilla es la identidad de la diseñadora, no la de la marca del cliente:
  el trío amarillo / azul / verde se mantiene salvo que pidan otros tonos
  (`color_acento`, `color_azul`, `color_verde`).
- El diseño es sobrio y editorial: la elegancia viene del aire y de textos
  cortos. Si una lámina se ve apretada o la letra se achica, recorta el texto
  en vez de aceptar el ajuste automático. Respeta las extensiones de
  `references/contenido.md`.
- Si la persona pide explícitamente PowerPoint, entrega el mismo .pptx sin
  subirlo a Drive; si pide PDF, exporta la presentación a PDF.
- Pon `fecha` (mes y año) en el JSON para la portada; `contacto` (correo, web)
  aparece en la lámina final si se incluye.
- Idioma: el de la entrevista (por defecto español).
- No inventes datos verificables (años, clientes, certificaciones). Si el
  Reason Why no tiene pruebas, escríbelo con lo que hay y avisa qué faltaría.