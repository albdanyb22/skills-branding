# Esqueleto editorial del manual (deck de Slides)

La maqueta es fija en todas las marcas, para que los manuales se reconozcan como
de la misma diseñadora; lo que cambia es la ropa (colores, tipografías,
elementos gráficos de la marca). Sale de manuales de marca reales hechos para clientes.

Las instrucciones del tipo Slides mandan sobre el formato técnico (lienzo de
1920×1080, estilos en línea, tamaños mínimos, cómo subir imágenes, cómo se
envían los archivos). Este documento solo define la maqueta.

## Ropa de la marca

- **Colores**: fondo claro = neutro claro de la marca (o un blanco cálido, no `#FFFFFF` puro); texto = tinta de la marca; separadores = color principal a sangre; acentos = color secundario. Usa solo pares aptos de la matriz de contraste.
- **Tipografías**: titulares con la fuente de comunicación; si no está en Google Fonts ni se puede subir, usa la fuente de respaldo definida en el manual (eso también demuestra la regla). Nunca la fuente del logotipo para textos.
- **Elementos gráficos**: los aprobados (patrón, forma del isotipo) solo en portada, separadores y contraportada; las páginas normativas quedan limpias para que el gráfico se lea.

## Reglas comunes a todas las páginas normativas

- Encabezado corrido arriba a la izquierda, 24 px, color secundario de texto: `Logo <Marca>, Guía de uso <año>`. Número de página arriba a la derecha, mismo estilo (o abajo a la derecha si la página es muy densa).
- Título de la página arriba a la izquierda (56–64 px), debajo del encabezado; subtítulo opcional en el color de acento (por ejemplo "Versión horizontal").
- Columna de texto a la izquierda, unos 560 px de ancho, 26–28 px, 2–4 frases.
- El gráfico ocupa el resto (unos 1000 px de ancho) y es el protagonista. Fondos de los gráficos: el que exige la variante (negativo sobre su color, etc.).
- Notas de medida ("Un módulo equivale al alto de la letra V", "Impresión: 3,3 cm · Pantalla: 127 px") en 24 px junto al gráfico que describen.
- Mismo esqueleto en todas las páginas de un mismo tipo: el título nunca salta de sitio.

## Tipos de página

1. **Portada** — fondo color principal (o neutro si el logo no contrasta), logo principal grande centrado-izquierda, "Manual de marca" y "<Marca> · v1.0 · <mes año>" abajo a la izquierda. Elemento gráfico de la marca a sangre si existe.
2. **Índice** — dos columnas de secciones con su número, en el estilo "04. ¿Quiénes somos?" de tus manuales.
3. **Separador de sección** — color principal a sangre, número y nombre de la sección grandes, elemento gráfico.
4. **Texto + gráfico** (la mayoría: concepto, composición, plano, protección, tamaño mínimo, fotografía) — columna de texto a la izquierda, imagen a la derecha.
5. **Cuadrícula de versiones** — 2×3 o 3×2 tarjetas, cada una con su fondo y una etiqueta de 24 px debajo ("Versión negativo · Para fondos oscuros"). Sirve para variantes de color, usos incorrectos (con su X) y logo sobre fondos.
6. **Color** — bandas o tarjetas por color con nombre, significado y valores (HEX / RGB / CMYK / Pantone), la barra de % de uso a lo ancho debajo; las escalas 50–950 en una página aparte como filas de muestras con su HEX.
7. **Tabla** — contraste y jerarquía tipográfica: tabla con la primera fila de encabezado; en jerarquía, cada fila escrita en su propio estilo.
8. **Specimen tipográfico** — "Ag" grande con la fuente, nombre, uso, licencia, alfabeto y números.
9. **Tono de voz** — dimensiones en tarjetas y tabla de dos columnas "Lo que <Marca> dice / Lo que evita".
10. **Frase** — posicionamiento: la frase sola, grande, sobre el color principal o neutro.
11. **Aplicación** — la pieza a la derecha (o a sangre) y, a la izquierda, las reglas: versión de logo usada, márgenes en módulos, colores, tipografía. Las piezas (tarjeta, membrete, post, carta, uniforme…) se construyen en la propia slide con formas, el logo y los textos, en planos simples: no fingen ser fotografías.
12. **Entregables** — árbol de carpetas en una tarjeta y tabla "formato · para qué".
13. **Contraportada** — como la portada, con el contacto del responsable de marca (y el crédito, si se pidió).

## Imágenes

- Sube como recursos del deck los PNG que generaron los scripts (`*_preview.png`, `*_plano.png`, `*_proteccion.png`, `hoja_*.png` o las piezas sueltas) o los SVG si las reglas de imágenes del tipo los aceptan sin rasterizar mal. Para el logo en portada y aplicaciones usa el SVG aprobado de la variante correcta.
- Para el tamaño mínimo, muestra la imagen a tamaño real junto a la ampliada.
- Nunca dibujes el logo con formas del deck: siempre la imagen del archivo aprobado.

## Notas del orador

Pon en las notas de cada página lo que la persona tiene que revisar o completar
("Pantone pendiente de validar", "confirmar correo del responsable"), para que
no quede escondido en el mensaje del chat.

## Construcción técnica (lo que funcionó)

- **Encabezado corrido** como dos `<p>` pinned a `top:64px` (izquierda: "Logo <Marca>, Guía de uso <año>"; derecha: número), y la sección con `padding:176px 128px 128px` para que el título nunca choque con él.
- **Separadores**: color a sangre, número de sección (44 px) y nombre (160 px, peso 800) abajo a la izquierda, y el símbolo grande arriba a la derecha en la tinta que contraste. Alterna los colores de la paleta por sección.
- **Imágenes**: renderiza cada versión a PNG transparente (logos a 1000–1400 px de ancho, símbolos a 500 px) y súbelas como recursos del deck **desde una carpeta del directorio de trabajo**, hasta 25 por llamada (los archivos fuera de él suben de a uno). Anota cada `/_blob/<id>`: lo usarás en `src`.
- **Tamaño de las imágenes en la slide**: fija `width` y `height` con la proporción real del PNG y `object-fit:contain`.
- **Escalas de color**: una grilla `150px repeat(11, 1fr)` de `<p>` con `background`, el HEX dentro y la tinta de texto calculada por contraste; marca en negrita el paso que es el color de marca.
- **Aplicaciones**: constrúyelas con `div` (tarjeta, A4, post, fotocheck) y el PNG del logo; para prendas, una silueta simple en `<svg>` y el logo pinned encima. Sin mockups fotográficos.
- **Pendientes** en las notas del orador (`<aside>`) de cada página, además de la lista final.
- Publica en tandas de 6–8 páginas por llamada; el índice (`deck.json`) va primero, completo, con todo el `order`.
