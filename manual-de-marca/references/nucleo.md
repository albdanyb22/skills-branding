# Núcleo: el manual básico

Va siempre, en este orden. Es la estructura de manuales de marca reales hechos para clientes, más seis piezas que un manual profesional no
puede omitir (marcadas ★). Unas 26 páginas + aplicaciones. Si una página no
aplica (por ejemplo, el logo no tiene tagline), se omite y se ajusta el índice.

| # | Página | Contenido | Fuente |
|---|---|---|---|
| 1 | Portada | Logo principal grande, "Manual de marca", nombre de la marca, versión y año. Fondo del color principal o neutro según contraste. | — |
| 2 | Índice | Secciones con número de página. | índice aprobado |
| 3 | ★ Control del documento | Versión, fecha, responsable de marca y contacto, historial de cambios (vacío en v1.0), cómo usar el manual. | Bloque 6 |
| 4 | ¿Quiénes somos? | Quiénes somos, misión y visión. Texto breve. | PPT |
| 5 | Introducción | "Nuestro logo, isotipo, logotipo, tipografía y colores son los componentes principales de la identidad visual básica de <Marca>. Su uso consistente hará que la marca sea visible y memorable. Una marca es tan fuerte como las personas que la usan. Las siguientes páginas sirven como guía para saber cómo utilizar los principales activos de nuestra marca." | plantilla |
| 6 | Concepto | Cada pieza del logo y lo que significa (2–4 piezas, con el fragmento del logo resaltado). Enlace a video si existe. | PPT / Bloque 2 |
| 7 | Composición | Isotipo + logotipo (+ tagline) = logo, con cada parte rotulada. | grupos |
| 8 | Plano constructivo | Una página por versión principal (horizontal, vertical). "Un módulo equivale a …" explicado con el elemento del logo del que sale. | construction.py |
| 9 | Área de protección | El logo con su área y las X; regla en módulos; nota de que con otras marcas se usa más espacio. | construction.py |
| 10 | Tamaño mínimo | Por versión: impresión (cm) y pantalla (px), con el logo a ese tamaño. Qué versión usar por debajo. Si el símbolo pierde su detalle antes que el nombre, dilo y pide mostrarlo aparte en los formatos chicos. | min_size.py |
| 11 | Versiones | Las recomposiciones aprobadas (horizontal, vertical, isotipo, sin tagline) y cuándo usar cada una; la principal destacada. | Fase 3 |
| 12 | Variantes de color | Positivo, negativo, monocromo, grises, calados… por versión, cada una sobre su fondo y con su uso. | logo_variants.py |
| 12b | Sistema de color del logo (identidad dinámica) | Si la identidad es dinámica, una página con todas las variantes del sistema (por ejemplo, 6 colores sobre claro y sus negativos sobre negro) y la regla de qué cambia y qué es fijo; más una página de asignación en el módulo M1. | logo_variants.py |
| 13 | ★ Logo sobre fondos de color | Qué variante va sobre cada color de la paleta (de la matriz de contraste), y fondos prohibidos. | color_system.py |
| 14 | ★ Logo sobre fotografía | Foto clara → variante oscura; foto oscura → negativo; foto cargada → placa o franja de color. Ejemplos con fondos neutros si no hay fotos propias. | Bloque 5 |
| 15 | ★ Logo en digital pequeño | Avatar circular (con el recorte real), favicon (16/32 px) e ícono de app (con su retícula de margen). | compose.py avatar |
| 16 | Cobranding | Logo junto a otra marca: misma altura visual, divisor opcional, separación en módulos (normalmente el doble del área de protección), jerarquía compartida. | módulo |
| 17 | Usos incorrectos | 8 errores con el logo real y una X: deformar, rotar, cambiar colores, cambiar tipografía, alterar elementos del isotipo, cambiar proporciones entre partes, añadir efectos (sombra, contorno), fondo sin contraste. Generados con los SVG reales. | logo_variants / transformaciones |
| 18 | Paleta de color | Colores con nombre y significado, y la barra de % de uso. | PPT + colores.json |
| 19 | Valores de color | Por color: HEX, RGB, CMYK (y si es aproximado), Pantone (o pendiente). Escalas 50–950 si se aprobaron. | sistema_color.json |
| 20 | ★ Contraste y accesibilidad | Pares texto/fondo aptos (AA/AAA), pares solo para titulares grandes, y los prohibidos. | sistema_color.json |
| 21 | Tipografía | Fuente del logotipo (solo para el logo) y fuente de comunicación, con specimen. ★ Fuente de respaldo y licencia de cada una. | Bloque 4 |
| 22 | ★ Jerarquía tipográfica | Titular, subtítulo, cuerpo, destacado, nota: fuente, peso, tamaño de referencia, interlineado; ejemplo compuesto. | Bloque 4 |
| 23 | Elementos gráficos | Patrones, formas, texturas o ilustraciones y sus reglas (no recargar, equilibrio contorno/relleno). | Bloque 5 |
| 24 | Fotografía | Estilo, temas, encuadre, color; qué se evita. | PPT moodboard / Bloque 5 |
| 25 | Tono de voz | Dimensiones del tono y tabla "lo que <Marca> dice / lo que evita". | PPT |
| 26 | Posicionamiento | La frase de posicionamiento. | PPT |
| 27 | Aplicaciones básicas | Tarjeta de presentación, hoja membretada, firma de correo, avatar y post de redes: cada una con la versión de logo usada, márgenes en módulos y colores. 2–3 páginas. | deck |
| 28 | Aplicaciones del rubro | 2–4 piezas elegidas en el Bloque 5, con las mismas anotaciones. Una página por pieza. | deck |
| 29 | ★ Entregables | Árbol de carpetas del .zip, nomenclatura de archivos, qué formato usar para qué (SVG web, PNG redes/Office, PDF imprenta), y la nota de arte final CMYK pendiente. | entregables.json |
| 30 | Contraportada | Logo, contacto del responsable de marca, crédito si se pidió. | Bloque 6 |

## Cómo escribir el texto

- Registro normativo y breve: 2–4 frases por página, en primera persona plural de la marca, como en tus manuales ("Porque somos lo que ven de nosotros, cuidamos que nuestra imagen sea la misma en todas partes").
- Cada regla con su porqué en una frase: el cliente las cumple mejor si las entiende.
- Medidas siempre en módulos para la construcción, en cm y px para tamaños.
- Corrige erratas al adaptar textos de la presentación (ocaciones → ocasiones, minímo → mínimo).

## Regla de fondos que suele faltar

Sobre un fondo de color de la propia paleta, el logo va en **una sola tinta** (negro o blanco, la que dé contraste), nunca en otro color de la paleta: así cada pieza lleva un solo color protagonista. Sobre negro, el negativo con color solo si ese color contrasta ≥ 3:1 con el negro; si no (azules oscuros, por ejemplo), monocromo blanco.
