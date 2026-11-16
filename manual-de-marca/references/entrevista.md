# Entrevista del manual de marca

Seis bloques, en este orden (cada uno depende del anterior). Una pregunta a la
vez, cada una con tu recomendación. Salta lo que ya responde la presentación de
branding o el SVG, y confírmalo de paso. Entre corchetes: la recomendación por
defecto si la persona no tiene preferencia o no está para responder.

## Bloque 1 — Alcance (decide los módulos)

Pregunta de apertura, para encuadrar: ¿quién va a usar este manual en el día a
día? (el propio cliente / su agencia / proveedores, imprentas, franquicias). Ya
orienta varios módulos.

Luego, una por una, las preguntas que activan módulos (detalle en `modulos.md`):

1. ¿La marca tiene o tendrá sub-marcas, líneas de producto, sedes o áreas con identidad propia? → **M1 Arquitectura de marca**. [no, salvo que el PPT lo mencione]
2. ¿Va a aparecer junto a socios, sponsors, aliados o clientes de forma habitual (eventos, proyectos conjuntos, convenios)? → **M2 Logos compuestos**. El cobranding básico va siempre en el núcleo; este módulo es para cuando es frecuente y necesita reglas de jerarquía, divisor y designación. [no]
3. ¿Se va a reproducir en merch, uniformes, señalética, vehículos, empaques o materiales especiales (bordado, grabado, serigrafía, vinil, repujado)? → **M3 Reproducción especial**. [sí si el rubro es restaurante, retail, construcción, eventos o educación]
4. ¿Comunica en más de un idioma? → **M4 Idiomas**. [no]
5. ¿Terceros (agencias, franquiciados, proveedores, equipo interno) van a producir piezas sin que tú las revises? → **M5 Uso por terceros**: retícula de diagramación, plantillas, proceso de aprobación, checklist, FAQ y glosario. [sí si la respuesta de apertura no fue "solo el cliente"]
6. ¿Tiene slogan o línea de campaña fija que acompañe al logo? → **M6 Lock-ups con slogan**. [sí si el PPT trae brand mantra o tagline de campaña distinto del tagline del logo]

Cierra el bloque con el resumen: "Núcleo + M3 + M5 → unas 34 páginas".

## Bloque 2 — Logo y versiones

Ya tienes los grupos confirmados (Fase 1).

0. ¿La identidad es **dinámica**? Es decir, ¿una parte del logo cambia de color (o de forma) según la sub-marca, el edificio, la sede o la campaña? Si el PPT lo dice, confírmalo. En ese caso los grupos del SVG se definen por **regla de color** (lo que cambia / lo que es fijo / lo que acompaña al que cambia), no por isotipo/logotipo, y el manual necesita una página de sistema ("una comunidad, un color") y reglas de asignación (quién elige el color, que vecinos no se repitan, quién lleva el registro). [preguntar siempre que la paleta tenga 4+ colores de igual peso]
1. ¿Qué versiones existen ya como SVG? (horizontal, vertical, isotipo, sin tagline, avatar). Pide los que tenga. [usar los suyos; derivar solo lo que falta]
2. ¿Qué versiones necesita el manual? Propón según el logo: si es horizontal, recomienda vertical + isotipo + avatar; si el tagline es pequeño, una versión sin tagline para tamaños chicos.
3. ¿Cuál es la versión principal (la que se prioriza)? [la que la persona entregó como logo]
4. El concepto: ¿qué significa cada pieza del logo? Si el PPT lo trae (sección concepto), confírmalo; si no, pregúntalo: la página "Concepto" no se inventa.
5. ¿Hay video o animación del concepto para enlazar? (tus manuales anteriores lo enlazan). [no]

Las variantes de color y las recomposiciones se aprueban en la Fase 3 de SKILL.md, no aquí.

## Bloque 3 — Color

1. Paleta: confirma colores, nombre de cada uno y su significado (del PPT). ¿Cuál es el principal, cuáles secundarios, cuáles neutros?
2. Fuente de verdad: ¿de dónde salen los valores? (archivo del logo, PPT, imprenta). Pide los HEX y, si existen, CMYK y Pantone. [HEX del SVG como fuente]
3. ¿La imprenta del cliente ya validó CMYK o Pantone? Si no, **ofrece hacer el trabajo** con lo que hay: CMYK con perfil de imprenta (FOGRA39, `color_system.py` lo usa solo) y Pantone / TCX de referencia por ΔE 2000 (`pantone_ref.py`). Preséntalo en una tabla con el ΔE y explica qué colores salen apagados en CMYK (fuera de gama) y cuáles no tienen equivalente. El manual los marca siempre como "referencia, validar con guía física y prueba de color". Nunca los presentes como oficiales.
4. % de uso de cada color en las comunicaciones. [principal 50–60 %, neutros 25–30 %, acentos 10–15 %]
5. ¿Escalas 50–950? Recomiéndalas si la marca tiene producto digital o web; si no, basta con 2–3 tonos por color. [escala completa solo con producto digital]

## Bloque 4 — Tipografía

1. ¿Cuál es la tipografía del logotipo (y del tagline)? Si no se sabe, lo dice el archivo o la persona; no la adivines por la forma.
2. ¿Qué tipografía se usa para comunicación (titulares y textos)? [la del type board del PPT]
3. Licencia de cada una (ver Fase 6 de SKILL.md). Búscala en la web antes de preguntar: muchas fuentes "gratis" son solo para uso personal. Si viene de Envato Elements, la licencia cubre logos pero **hay que registrar la fuente para ese proyecto** mientras la suscripción esté activa y guardar el certificado PDF: pregunta si ya lo hizo. Si hay una restringida, propón alternativa.
4. ¿Qué fuente de respaldo usa el cliente cuando no tiene la de marca? [una de Google Fonts parecida y disponible en Docs y Canva; o Arial si trabaja en Word sin instalar nada]

## Bloque 5 — Lenguaje visual y aplicaciones

1. Elementos gráficos: ¿hay patrones, formas, texturas o ilustraciones derivadas del logo? Pide los archivos. Si no hay, ¿se derivan del isotipo? (propón 2–3 y muéstralos antes de usarlos). [derivar del isotipo, con aprobación]
   - **Si las ilustraciones son de un banco o de la comunidad de Figma, revisa su licencia** antes de normarlas (por ejemplo, Streamline Free exige atribución, permite 25 ilustraciones por proyecto y prohíbe redistribuirlas como recurso). Si la licencia no permite entregarlas a terceros, el manual las presenta como estilo de referencia, con el crédito, y no van en el .zip.
   - Si están en Figma: usa el conector oficial de Figma (create_session → get_metadata para ubicarlas → get_screenshot con base64 para traerlas). En el plan Starter las llamadas son limitadas: elige primero, trae solo las que van al manual. Las capturas de nodos rasterizados salen a ~400 px; para alta resolución pide la exportación en SVG.
   - Presenta las candidatas sobre los colores de la marca para elegir, y descarta las que no encajan con el rubro (por ejemplo, bebidas alcohólicas para una administradora).
2. Fotografía: estilo, temas y lo que se evita. Parte del moodboard del PPT. ¿Hay fotos propias para ilustrar? Si no, la página describe el estilo sin imágenes de banco que parezcan propias del cliente.
3. Logo sobre fotografía: ¿la marca usa mucho foto en redes? Define qué versión va sobre foto clara, oscura y cargada (con placa o franja de color). [placa del color principal en fotos cargadas]
4. Aplicaciones del rubro: a partir del PPT, propón 2–4 piezas propias del rubro (restaurante: carta, empaque, delantal; constructora: casco, vehículo, valla; consultora: propuesta, presentación; educación: certificado, credencial) y deja que elija. Las básicas (tarjeta, hoja membretada, firma de correo, avatar, post) van siempre.

## Bloque 6 — Control del documento

1. Versión y fecha del manual. [v1.0, mes y año actuales]
2. Responsable de marca del lado del cliente (nombre o cargo y correo) a quien consultar dudas o pedir aprobación. [marcador entre corchetes si no lo tiene]
3. ¿Crédito del estudio/diseñadora en la contraportada? [sin crédito, salvo que lo pida]
4. Idioma del manual. [español]
