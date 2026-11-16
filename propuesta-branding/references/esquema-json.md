# Esquema del JSON de contenido

`scripts/build_slides.py` lee este JSON. Ejemplo completo: `references/ejemplo-vecindia.json`.

Rutas de imágenes: absolutas o relativas a la carpeta del JSON. Cualquier lista de
imágenes vacía → se dibujan recuadros-placeholder con el texto descriptivo.
En los textos, `\n` hace salto de línea y `**texto**` pone negrita.

```jsonc
{
  "marca": "string",                       // nombre de la marca
  "disenador": { "nombre": "string", "rol": "Designer" },
  "color_acento": "#FDD23C",               // opcional: amarillo principal de la plantilla
  "color_azul": "#2F5BFF",                 // opcional: azul vibrante secundario
  "color_verde": "#1FC86A",                // opcional: verde secundario
  "fecha": "Octubre 2026",                 // portada (propiedad "Fecha")
  "contacto": "hola@estudio.com",          // opcional, lámina "Gracias"
  "quienes_somos": "string",
  "mision": "string",
  "vision": "string",
  "valores": [ { "nombre": "string", "descripcion": "string" } ],
  "reason_why": "string",
  "personificacion": "string",
  "personalidad": { "intro": "string", "rasgos": [ { "nombre": "string", "descripcion": "string" } ] },
  "brand_mantra": "string",
  "tono_de_voz": {
    "intro": "string",
    "dimensiones": [ { "nombre": "string", "descripcion": "string" } ],
    "ejemplos": [ { "situacion": "string", "dice": "string", "evita": "string" } ]
  },
  "posicionamiento": "string",
  "benchmark": {
    "subtitulo": "string",
    "marcas": [ { "nombre": "string", "motivo": "string" } ],
    "referentes_visuales": ["string"],     // nombres para la grilla si no hay imágenes
    "imagenes": ["ruta/logo1.png"]         // opcional
  },
  "moodboard": {
    "texto": "string",
    "descripcion_imagenes": ["string"],    // hasta 8, se usan si no hay imágenes
    "imagenes": ["ruta/img.jpg"],          // opcional (ideal 6)
    "paleta": [ { "nombre": "string", "hex": "#RRGGBB" } ]   // hasta 8; más de 5 se reparten en 2 filas
  },
  "type_board": {
    "texto": "string",
    "fuentes": [ { "nombre": "Google Font", "rol": "Titulares",   // ideal 6
                   "etiqueta": "texto del pie (opcional)",
                   "muestra": "Aa",                    // opcional: texto grande de la tarjeta
                   "imagen": "ruta/muestra.png" } ],    // opcional: para fuentes que Slides no tiene
                                                        // (p. ej. la del logo): la tarjeta muestra la imagen
    "imagenes": ["ruta/specimen.png"]      // opcional; reemplaza las tarjetas de muestra
  },
  "concepto": {
    "nombre": "string",
    "texto": "string",
    "imagen": "ruta/img.jpg",              // opcional; si es horizontal (p. ej. el sistema de logos)
                                           // va a lo ancho bajo el texto, sin recortar
    "descripcion_imagen": "string"
  }
}
```

Las láminas sin contenido se omiten (salvo portada, divisor y "Gracias").
El script mide cada texto y reduce el tamaño para que entre (Google Slides no lo
hace solo), pero respeta las extensiones de `contenido.md`: si se reduce
demasiado se ve mal. En `type_board.fuentes` usa nombres exactos de Google Fonts
para que Slides las muestre.
