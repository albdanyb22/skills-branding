# Skills de branding

Tres skills para Claude que cubren el flujo de una identidad de marca, desde el brief hasta el manual.

| Skill | Qué hace | Entrega |
|---|---|---|
| [`propuesta-branding`](propuesta-branding/) | Entrevista con el brief de marca (27 preguntas en 5 bloques), desarrolla la estrategia y arma la propuesta. | Presentación de Google Slides (.pptx editable) |
| [`brand-board`](brand-board/) | Muestra la marca aplicada: tablero principal más afiches, una pieza informativa y posts, cada uno con un solo color protagonista. | Diseño editable |
| [`manual-de-marca`](manual-de-marca/) | Documenta la identidad ya aprobada: versiones del logo, retícula, área de protección, mínimos, color CMYK/Pantone, tipografía y licencias. | Deck de Slides y .zip del logo |

## Orden de uso

1. **propuesta-branding**: la estrategia (quiénes somos, valores, tono, concepto…).
2. **brand-board**: la marca aplicada a piezas reales.
3. **manual-de-marca**: las normas de uso. Necesita el logo en SVG y la propuesta de branding.

## Estructura de cada skill

```
<skill>/
├── SKILL.md       # cuándo usarla, pasos, reglas y ejemplos
├── references/    # guías que el agente abre solo cuando las necesita
├── scripts/       # Python (Pillow, numpy, scipy, Playwright/Chromium)
└── assets/        # plantillas y fuentes
```

## Instalación

Copia la carpeta de la skill a tu carpeta de skills (por ejemplo `~/.claude/skills/`) o súbela como skill en Claude.

## Notas

- Las fuentes Inter e Inter Tight se incluyen bajo la licencia SIL Open Font License (ver `propuesta-branding/assets/fonts/`).
- El ejemplo `ejemplo-vecindia.json` es de una marca ficticia.
