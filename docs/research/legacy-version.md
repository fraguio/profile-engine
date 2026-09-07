# Caracterización de la primera versión

## Respuesta

En el snapshot investigado, `profile-engine-v0` es una CLI Python y un workflow de GitHub Actions que convierten una fuente JSON Resume a un YAML específico de RenderCV 2.8, copian overrides de plantillas junto al YAML, invocan RenderCV como subproceso para producir HTML y publican en GitHub Pages todo el directorio de salida. El recorrido extremo a extremo existe y está desplegado, pero sus contratos no son uniformes: `validate`, `convert` y `html` aceptan conjuntos distintos de entradas válidas; el mapeo representa solo una parte de JSON Resume y descarta el resto; el paquete depende del checkout y del directorio de trabajo para validar; y la publicación expone también el YAML transformado con datos del perfil. [S1] [S3] [S4] [S5] [S8] [S18] [S19]

Estos hechos sirven para delimitar decisiones de la reconstrucción, no para resolverlas por imitación. La nueva versión no requiere compatibilidad con ningún comando, YAML, layout, módulo, tecnología ni automatización descritos aquí.

## Alcance y barrera anticontaminación

- **Objeto observado:** rama `main` de `fraguio/profile-engine-v0` en el commit `d6cb420cb86eac69b3b2a3bd3d6cccf903f71b6b`, que era su `HEAD` el 7 de septiembre de 2026. [S1]
- **Fuentes primarias:** código, tests, schemas, documentación, historial, ejecuciones de GitHub Actions y despliegue de GitHub Pages del repositorio heredado. Se consultaron los commits upstream declarados por sus contratos cuando fue necesario. [S20] [S21]
- **Hecho observado:** comportamiento que puede leerse directamente en código o artefactos, o que consta en una ejecución.
- **Decisión heredada:** intención declarada en la documentación o elección materializada por v0. No es una recomendación para la reconstrucción.
- **Riesgo:** consecuencia posible sustentada por hechos, no una afirmación de que ya se haya producido un incidente.
- **Niebla:** dato que las fuentes de v0 no permiten resolver.

No se infiere como requisito ninguna separación de módulos, interfaz CLI, convención de archivos, stack Python, schema copiado, versión de RenderCV, plantilla, locale ni mecanismo de GitHub observados. Tampoco se toma la documentación heredada como prueba suficiente cuando contradice el código o los artefactos desplegados.

## Hechos observados

### Recorrido funcional

El flujo completo implementado es:

```text
JSON Resume en fichero
  -> validación Draft 7 contra un schema local
  -> mapeo parcial a un documento RenderCV
  -> YAML y overrides de plantillas en disco
  -> `rendercv render` como subproceso
  -> Markdown temporal
  -> HTML en disco
  -> artefacto de GitHub Pages
  -> despliegue público
```

La CLI pública se llama `profilectl`; el paquete declara la versión `0.1.0` y requiere Python 3.12 o posterior. [S2] [S7]

| Comando | Entrada observada | Salida y efectos observados | Validación |
|---|---|---|---|
| `validate` | Fichero, posicional o `-i/--input`; no `stdin` | `OK` en `stdout` al tener éxito | JSON parseable y schema JSON Resume local |
| `convert` | Fichero, `-i -` o `stdin` implícito si no es TTY | YAML en `stdout` por defecto o fichero con `-o`; si escribe fichero, copia directorios de plantillas a su lado | Raíz JSON objeto y reglas propias del mapeo, pero no ejecuta el schema JSON Resume |
| `render-html` | Fichero YAML, posicional o `-i`; no `stdin` | HTML en fichero, por defecto `output/index.html`; copia plantillas junto al YAML; crea y elimina un Markdown temporal | Rechaza por extensión `.json`; delega el contenido a RenderCV |
| `html` | Fichero JSON Resume; no `stdin` | YAML intermedio, plantillas y HTML; defaults `output/rendercv_CV.yaml` y `output/index.html` | Ejecuta `validate`, luego `convert`, luego `render-html` |

El código contiene además un alias oculto `rendercv` para `convert`. No existe un comando de publicación: publicar es responsabilidad del workflow. [S3] [S11] [S24]

`render-html` invoca exactamente `rendercv render`, pide rutas para Markdown y HTML y desactiva PDF, PNG y Typst. Por tanto, v0 produce localmente YAML y HTML; no ofrece generación local de PDF, PNG o Typst mediante su interfaz pública. El Markdown es un detalle temporal y se elimina incluso si falla RenderCV. [S3]

### Contrato de entrada

`validate` usa `jsonschema.Draft7Validator` y `FormatChecker`, ordena los errores por ruta y mensaje y carga `schemas/jsonresume.schema.json` desde `Path.cwd()`. El schema copiado declara proceder de JSON Resume `v1.2.1`, commit `50798e359292ad4448d95b3bb0de5f694d6bcc4b`. No define campos obligatorios y permite propiedades adicionales tanto en la raíz como en los objetos principales. [S5] [S6] [S20]

El schema y el mapeador no establecen el mismo conjunto de entradas aceptadas:

- `validate` admite `basics.phone` como cualquier string, pero `convert` y `html` exigen que `phonenumbers` pueda interpretarlo como un número internacional real y lo normalizan a E.164. [S4] [S6]
- `convert` no llama a `validate_jsonresume`; puede transformar fechas u otros valores que `validate` rechazaría. `html` sí valida primero. [S3]
- El schema admite `{}` y objetos con extensiones. El mapeador también convierte `{}` a un documento con `cv: {}`, tema y locale, pero los tests no demuestran que RenderCV pueda renderizar ese resultado. [S4] [S6] [S12]
- El schema estándar define educación mediante `area` y `courses`; el mapeador heredado consulta las extensiones `title`, `details`, `notes` y `status`. Esas extensiones pasan la validación porque `additionalProperties` es `true`, mientras los campos estándar `area` y `courses` no se mapean. [S4] [S6]

### Contrato de transformación

El mapeo efectivo conserva el orden de las listas, recorta strings y elimina valores `None`, strings vacíos, listas vacías y objetos vacíos. La serialización usa `yaml.safe_dump(sort_keys=False, allow_unicode=True)` y antepone un comentario `$schema` que apunta al tag remoto de RenderCV `v2.8`. [S4]

| JSON Resume leído | RenderCV emitido | Semántica adicional |
|---|---|---|
| `basics.name` | `cv.name` | Omite valores vacíos |
| `basics.label` | `cv.headline` | Omite valores vacíos |
| `basics.location.city`, `region`, `countryCode` | `cv.location` | Concatena los presentes con `, `; ignora `address` y `postalCode` |
| `basics.email` | `cv.email` | Recorta espacios |
| `basics.phone` | `cv.phone` | Valida con `phonenumbers` y normaliza a E.164 |
| `basics.url` | `cv.website` | Recorta espacios |
| `basics.summary` | `cv.sections.Summary` | Separa párrafos por una o más líneas en blanco |
| `work[].name` | `experience[].company` | Los items no objeto se descartan |
| `work[].position`, `location`, `summary`, `highlights` | Campos homónimos | `highlights` admite string o lista de strings |
| `work[].startDate`, `endDate` | `start_date`, `end_date` | Año pasa a enero; fecha diaria pierde el día; ausencia de fin pasa a `present` |
| `education[].institution` | `education[].institution` | Omite valores vacíos |
| `education[].title` | `education[].area` | Usa una extensión no declarada por JSON Resume v1.2.1 |
| `education[].studyType` | `education[].degree` | Omite valores vacíos |
| `education[].startDate`, `endDate`, `status` | `start_date`, `end_date` | `status == in_progress` fuerza `present` |
| `education[].details`, `notes` | `education[].highlights` | Concatena detalles y, al final, notas |
| `skills[].name`, `keywords` | `skills[].label`, `details` | Une keywords con `, `; ignora `level` |
| `languages[]` | Un item adicional de `skills` | Etiqueta fija `Idiomas`; cada valor queda como `idioma (fluidez)` |

No se leen `basics.image`, `basics.profiles`, `volunteer`, `awards`, `certificates`, `publications`, `interests`, `references`, `projects` ni `meta`. Tampoco se leen varios campos estándar dentro de las secciones sí soportadas, como `work.url`, `work.description`, `education.area`, `education.url`, `education.score`, `education.courses` o `skills.level`. La omisión es silenciosa. [S4] [S6]

Las fechas con forma `YYYY` se convierten a `YYYY-01`, las `YYYY-MM-DD` pierden el día y las `YYYY-MM` se conservan. Cualquier otra string se devuelve sin cambio si se usa `convert` directamente. [S4] [S12]

El documento siempre incluye:

```yaml
design:
  theme: profileengine01classic
locale:
  language: spanish
```

La CLI no expone opciones de tema o locale. El YAML puede editarse después, pero una conversión posterior vuelve a emitir esos defaults. [S2] [S4] [S11]

### Contrato de salidas y diagnósticos

Los códigos propios son `2` para uso, `3` para parseo JSON, violación del schema o `ValueError` de conversión, `4` para E/S y `5` para error inesperado o fallo de RenderCV. Los diagnósticos se escriben en `stderr` con prefijo `Error:`; una validación puede emitir varios errores ordenados. Un fallo semántico como un teléfono inválido comparte el código `3` con JSON mal formado. [S3] [S11] [S13]

Cuando RenderCV falla sin diagnóstico bajo `--quiet`, la CLI repite la ejecución sin `--quiet` para recuperar detalle. Si no encuentra el ejecutable devuelve código `5`. RenderCV no es dependencia del paquete `profilectl`: el workflow lo instala por separado con el extra `full`. [S3] [S7] [S8]

La escritura no es transaccional. `html` puede dejar el YAML y las plantillas creados aunque falle después el render; `render-html` no elimina de forma preventiva un HTML previo. Al escribir un YAML, la CLI crea directorios y copia con `dirs_exist_ok=True` tres árboles adyacentes (`profileengine01classic/`, `markdown/` y `html/`), pudiendo reemplazar archivos con el mismo nombre. Si la salida es `stdout`, no copia esas plantillas aunque el YAML referencia el tema custom. [S3] [S11]

### HTML observado

La plantilla HTML custom envuelve el HTML que RenderCV deriva del Markdown, añade CSS responsive y consume en el navegador hojas de estilo y scripts desde cdnjs y jsDelivr, con versiones e integridad fijadas. El HTML no es autocontenido. [S9]

El despliegue público estaba accesible el 7 de septiembre de 2026. En el artefacto observado:

- el atributo `lang` era `es` y los encabezados/contactos aparecían localizados al español;
- el `<title>` del documento estaba vacío aunque el encabezado visible sí contenía el nombre;
- el texto visible de la URL personal eliminaba todas las barras (`github.comfraguio` en el caso desplegado), aunque el `href` conservaba la URL;
- el layout incluía una media query para reducir padding por debajo de 768 px. [S9] [S10] [S18]

No se reproducen datos personales en este informe. Sí es material para la frontera de publicación que el YAML transformado, incluidos datos de contacto y el contenido profesional, estaba públicamente accesible en `rendercv_CV.yaml`, además del HTML. También era accesible al menos un override de plantilla bajo su ruta del artefacto. [S19] [S26]

### Arquitectura material

La arquitectura implementada tiene estas piezas:

| Pieza | Responsabilidad observada | Acoplamientos materiales |
|---|---|---|
| `src/profilecli/cli.py` | Parseo de argumentos, E/S, secuencia del pipeline, copia de plantillas y ejecución del renderer | Typer, directorio de trabajo, filesystem, ejecutable `rendercv` |
| `src/profilecli/validate.py` | Validación JSON Resume y formato determinista de errores | Schema bajo `<cwd>/schemas/` |
| `src/profilecli/convert_rendercv.py` | Normalización, mapeo parcial y serialización YAML | Forma de JSON Resume, forma de RenderCV 2.8, PyYAML, `phonenumbers` |
| `src/profilecli/templates/` | Overrides de tema, i18n, Markdown y HTML | Convención de descubrimiento de plantillas de RenderCV 2.8 y ubicación junto al YAML |
| `.github/workflows/pages.yml` | Obtención del Perfil fuente, build y publicación | GitHub Actions, repo hermano privado, secret, Pages, PyPI y runners alojados |

No hay API remota, servidor, base de datos ni estado persistente propio. Aunque las funciones son importables, la documentación declara la CLI como interfaz pública y no promete una API Python. [S2] [S3] [S14]

La frontera con RenderCV es simultáneamente de datos, proceso y filesystem: se genera su YAML, se colocan templates donde RenderCV espera encontrarlos y se ejecuta su binario. El repositorio contiene una copia de `rendercv.schema.json`, pero los módulos de runtime no la cargan; `convert` solo emite el enlace remoto en un comentario y la validación efectiva de salida sucede, si se renderiza, dentro del subproceso. [S1] [S3] [S4]

### Empaquetado y entorno local

El build usa `setuptools`. El paquete incluye `src/profilecli/templates/**/*`, pero no declara los schemas como package data. A la vez, `validate` exige el schema bajo el directorio de trabajo actual. En consecuencia, la instalación por sí sola no aporta el contrato requerido para validar desde un directorio arbitrario; los ejemplos y tests se ejecutan desde el checkout. [S5] [S7] [S13] [S23]

`pip install -e .[dev]` instala pytest pero no RenderCV. El devcontainer ejecuta esa orden, mientras el runbook presupone que `rendercv` está disponible para los pasos de render. El workflow sí instala explícitamente `rendercv[full]>=2.8,<2.9`. [S7] [S8] [S23] [S27]

El repositorio no mostraba tags ni releases el 7 de septiembre de 2026. La versión de paquete seguía siendo `0.1.0`. [S7] [S28]

### Publicación y operación

El único workflow observado se llama `Publish CV to GitHub Pages` y se activa por:

- push a `main` del propio engine;
- `workflow_dispatch`, con `profile_data_ref` y `profile_data_path`;
- `repository_dispatch` de tipo `profile-data-updated`, con los mismos valores opcionales en `client_payload`.

Los defaults son el ref mutable `main` y `data/resume.json`. El workflow descarga `${owner}/profile-data` en `external/profile-data` mediante `PROFILE_DATA_REPO_TOKEN`, genera en `output/`, solo comprueba que exista `output/index.html`, sube el directorio `output/` completo y despliega Pages. No ejecuta pytest ni valida explícitamente qué otros archivos se publican. [S8]

Las actions están fijadas por SHA, pero las dependencias Python no tienen lock completo: `jsonschema` no tiene rango; otras dependencias tienen rangos; RenderCV permite cualquier `2.8.x`; el runner es `ubuntu-latest`; y la fuente usa `main` por defecto. [S7] [S8]

El workflow concede `contents: read`, `pages: write` e `id-token: write`, y usa un environment `github-pages`. La concurrencia comparte el grupo `pages` y no cancela la ejecución en curso. El productor del evento `repository_dispatch` y la configuración del secret no viven en este repositorio. [S8]

El último run del snapshot, disparado por el push de `d6cb420`, completó build y deploy con éxito. El historial de Actions consultado el 7 de septiembre de 2026 contenía 48 runs: 34 exitosos y 14 fallidos. En fallos examinados del 11 y 13 de abril, el build, la generación y el upload habían terminado bien y el job `deploy` falló antes de mostrar pasos; los logs ya no estaban disponibles, por lo que no se atribuye causa. [S16] [S17]

El historial también registra correcciones en fronteras operativas concretas:

- se cambió la búsqueda del schema a `cwd`; [H1]
- el workflow necesitó `rendercv[full]` para funcionar; [H2]
- el trigger de push necesitó un default de ruta fuera de `workflow_dispatch`; [H3]
- el HTML custom había quedado excluido por `.gitignore`; [H4]
- email, teléfono y web se añadieron al mapeo después del pipeline inicial; [H5]
- la validación y el diagnóstico del teléfono se añadieron en dos correcciones posteriores; [H6] [H7]
- el encabezado visible del CV cambió de `CV de <nombre>` a solo el nombre. [H8]

Esto prueba evolución e incidencias de integración; no permite inferir por sí solo prioridades para la reconstrucción.

## Decisiones heredadas

Esta sección registra únicamente elecciones explícitas de v0. Ninguna queda adoptada por la nueva versión.

| ID | Decisión declarada o materializada en v0 | Evidencia | Lo que no se hereda automáticamente |
|---|---|---|---|
| DH-01 | Tratar JSON Resume como frontera del sistema y al engine como consumer independiente | README y arquitectura [S2] [S14] | La versión del schema, su grado de tolerancia y el subconjunto representado |
| DH-02 | Versionar copias locales de los schemas para evitar validación remota en ejecución | ADR 0002 [S15] | La ubicación, mecanismo de empaquetado, calendario de actualización o necesidad de dos copias |
| DH-03 | Ofrecer una CLI pequeña con comportamiento y códigos estables | Arquitectura y CLI [S3] [S14] | Nombres de comandos, flags, alias, códigos y mensajes heredados |
| DH-04 | Soportar un único target de conversión, RenderCV 2.8 | Código y documentación [S2] [S4] | La forma exacta del YAML o la versión 2.8 |
| DH-05 | Fijar por defecto un tema custom y locale español, configurables editando YAML | Conversor y README [S2] [S4] | El tema, el locale, la edición manual del intermedio o la convención de templates |
| DH-06 | Mantener RenderCV fuera de las dependencias del paquete e invocarlo como ejecutable | Packaging, CLI y workflow [S3] [S7] [S8] | El límite de proceso ni la instalación separada |
| DH-07 | Separar Perfil fuente privado, engine y sitio público en repositorios/servicios de GitHub | Workflow y runbook [S8] [S24] | Nombres de repositorio, secret, protocolo de evento y contenido del artefacto |
| DH-08 | Publicar desde el propio repositorio del engine mediante Pages, tanto por cambios de código como de datos | Workflow [S8] | Triggers, permisos, environment, política de concurrencia o unidad de despliegue |
| DH-09 | Preservar compatibilidad de la CLI durante la evolución de v0 | Arquitectura y alias oculto [S3] [S14] | Cualquier compatibilidad, excluida expresamente para la reconstrucción |

## Riesgos derivados de los hechos

### R-01: frontera pública más amplia que el HTML

El workflow sube `output/` completo y la ejecución de la CLI coloca allí YAML y templates además de `index.html`. El YAML está servido públicamente y contiene una representación legible de los datos personales del Perfil fuente. [S3] [S8] [S19]

Esto entra en tensión directa con la restricción actual de no exponer datos del Perfil fuente. El hecho no determina si el intermedio debe existir, pero obliga a decidir qué archivos cruzan la frontera pública y a verificar el artefacto, no solo la existencia de HTML. [S25]

### R-02: aceptación, transformación y render no comparten contrato

El schema es permisivo, `convert` no lo usa, el teléfono añade una regla fuera del schema, campos JSON Resume estándar se descartan y extensiones privadas sí se consumen. Un input puede pasar `validate` y fallar `convert`, pasar `convert` pero no `validate`, o validar y perder información silenciosamente. [S3] [S4] [S6]

Las decisiones posteriores necesitan distinguir como mínimo contrato fuente, política de extensiones, cobertura de mapeo, contrato RenderCV y comportamiento ante datos no representables.

### R-03: instalación no autocontenida

El schema requerido no se empaqueta y se busca en `cwd`; RenderCV tampoco se instala con el paquete. Una CLI instalada puede convertir desde cualquier directorio, pero `validate` y `html` dependen de ejecutar dentro de un checkout con `schemas/` y de provisionar otro ejecutable. [S3] [S5] [S7]

Esta dependencia implícita afecta distribución, portabilidad y diagnósticos de setup.

### R-04: reproducibilidad menor que la declarada

La documentación declara determinismo, pero el resultado operativo depende de rangos de dependencias, `ubuntu-latest`, un ref fuente `main`, el ejecutable externo y assets web de terceros. No hay release/tag ni lock de entorno completo. [S7] [S8] [S14]

No se ha comparado si dos ejecuciones actuales son byte a byte iguales. Debe definirse qué significa determinismo: mapeo semántico, bytes generados, renderer, artefacto publicado o todos ellos.

### R-05: acoplamiento a convenciones internas de RenderCV

El límite no es solo un YAML: depende de nombres y ubicaciones de templates, de flags del CLI y de un extra de instalación descubierto durante la evolución. La copia local del schema RenderCV no protege `convert`, y los tests de `render-html` sustituyen `subprocess.run` en vez de ejecutar RenderCV real. [S3] [S8] [S11] [H2] [H4]

Las versiones compatibles y la prueba contractual con el renderer quedan como decisiones explícitas para la reconstrucción.

### R-06: efectos parciales y colisiones en filesystem

La conversión con salida a fichero escribe más que el fichero solicitado y puede sobrescribir templates preexistentes. El pipeline no agrupa las salidas de forma atómica y puede dejar intermedios tras un fallo. La salida por `stdout`, en cambio, omite archivos necesarios para resolver el tema custom. [S3]

Esto deja sin contrato claro la propiedad de la carpeta de salida, la limpieza, la repetición idempotente y el estado tras error.

### R-07: publicación acoplada a cambios y entradas mutables

Todo push a `main` reconstruye y publica usando por defecto `profile-data@main`; un evento externo puede seleccionar ref y ruta. El valor de ruta se inserta sin comillas en el comando de shell. Las fuentes de v0 no documentan quién puede emitir el evento ni validan su payload. [S8]

No se afirma una explotación, pero la reconstrucción necesita un modelo de confianza para eventos, refs, rutas y secrets, además de decidir si un cambio documental o de código debe publicar producción.

### R-08: HTML no autocontenido y defectos visibles

El HTML desplegado requiere CDNs para estilo y KaTeX. El `<title>` vacío y el texto de URL deformado muestran que comprobar solo la existencia de `index.html` no cubre calidad funcional del documento. [S8] [S9] [S18]

Hay que aclarar si la exigencia actual de ejecución sin red incluye la visualización del HTML y qué comprobaciones de contenido, accesibilidad, enlaces, responsive y ausencia de recursos remotos forman parte del contrato. [S25]

### R-09: tratamiento de contenido no probado como frontera de seguridad

El Perfil fuente termina en HTML público a través de YAML, templates Jinja y conversión Markdown. Los tests heredados no establecen cómo se escapan HTML, Markdown, URLs o contenido activo procedente del perfil. [S4] [S9] [S11] [S12]

No se afirma que exista XSS. El nivel de confianza del Perfil fuente y el escape esperado son niebla que debe resolverse antes de especificar la publicación.

### R-10: portabilidad no demostrada

Hay instrucciones manuales para PowerShell y entorno Python, pero el único entorno automatizado observado es Ubuntu. El Makefile presupone `make` y comandos de shell; no hay matriz Linux/macOS/Windows ni artefactos de distribución publicados. [S8] [S22] [S23]

Los hechos no permiten afirmar que el recorrido completo funcione hoy en macOS o Windows.

### R-11: señal operativa limitada

El único workflow publica; no ejecuta la suite. El historial demuestra éxitos extremo a extremo, pero también 14 fallos durante la evolución y no conserva ya logs suficientes para explicar algunos deploys fallidos. [S8] [S16] [S17]

El legado no aporta una política observable de rollback, promoción, retención, health check posterior ni separación entre verificación y despliegue.

## Decisiones que los hechos hacen necesarias

Estas son preguntas para trabajo posterior, no respuestas heredadas:

| Área | Hecho que obliga a decidir | Pregunta abierta |
|---|---|---|
| Perfil fuente | Schema permisivo, extensiones privadas consumidas y campos estándar ignorados | ¿Qué versión y perfil de JSON Resume son autoritativos, y qué ocurre con campos desconocidos o no representables? |
| Invariantes | `validate`, `convert` y `html` discrepan | ¿Todas las rutas de transformación comparten una única validación, o se declaran contratos diferentes? |
| Mapeo | Solo se representan basics, work, education, skills y languages, parcialmente | ¿Cuál es la cobertura funcional mínima y qué pérdidas deben ser error, warning o aceptación explícita? |
| Documentos locales | v0 produce YAML y HTML y desactiva PDF/PNG/Typst | ¿Qué documentos componen exactamente la primera versión y cuáles son finales frente a intermedios? |
| Carpeta de salida | Una orden escribe y reemplaza varios árboles | ¿Cuál es la unidad de generación, su layout, propiedad, atomicidad y política de limpieza? |
| Presentación | Tema y español están hardcodeados; el intermedio es editable | ¿Qué significa configuración mínima de presentación y locale, y en qué contrato vive? |
| RenderCV | Acoplamiento por YAML, CLI y filesystem | ¿Cuál es la frontera soportada, cómo se fija la versión y cómo se prueba contra RenderCV real? |
| Distribución | El paquete no contiene schema ni renderer | ¿Qué instalación debe dejar operativo el recorrido completo en las tres plataformas? |
| Determinismo | Dependencias, runner y fuente son mutables | ¿Qué entradas y versiones forman la identidad de un build reproducible? |
| Publicación | Pages sirve YAML y templates además del HTML | ¿Cuál es la allowlist pública y cómo se prueba que no contiene datos o artefactos no previstos? |
| Automatización | Push y evento externo publican directamente | ¿Qué protocolo, autenticación, validación, promoción y concurrencia rigen el evento entre repositorios? |
| HTML | Usa red en el navegador y las pruebas no inspeccionan contenido | ¿Debe ser autocontenido y cuáles son sus criterios observables de calidad y seguridad? |
| Fallos | Puede quedar salida parcial y varios errores comparten código | ¿Qué garantías hay tras fallo y qué taxonomía consumen personas, scripts y CI? |

## Niebla nueva

- **Formatos finales locales:** v0 no demuestra si la reconstrucción necesita PDF además de HTML, ni si el YAML debe considerarse producto, intermedio depurable o detalle privado.
- **Dialecto real del Perfil fuente:** la fuente privada no está en v0. El conversor prueba dependencia de extensiones (`education.title/details/notes/status`), pero no documenta su contrato ni su origen.
- **Pérdida aceptable:** no hay evidencia que permita decidir si las secciones JSON Resume omitidas estaban fuera de necesidad, pendientes o perdidas accidentalmente.
- **Emisor del evento:** v0 contiene el receptor de `profile-data-updated`, no el productor ni su modelo de permisos, reintentos o entrega.
- **Política de privacidad:** el HTML está destinado a ser público, pero no está definido qué datos derivados pueden acompañarlo; el comportamiento actual publica el YAML completo.
- **Contrato offline:** no está claro si "sin red en runtime" comprende solo la ejecución local ya instalada o también abrir el HTML generado.
- **Contenido hostil:** no consta si el Perfil fuente se considera completamente confiable ni qué escape exige el HTML.
- **Determinismo:** no se define si incluye bytes de RenderCV y HTML, ni cómo tratar contenido dependiente del tiempo como duraciones calculadas por el renderer.
- **Portabilidad real:** no hay resultados de ejecución extremo a extremo para macOS o Windows.
- **Operación de Pages:** no se documentan rollback, promoción, URL estable, custom domain, comprobación posterior ni respuesta a un fallo de deploy tras upload correcto.
- **Causa de fallos históricos:** varios logs habían expirado; solo se pudo localizar el job fallido, no su causa.

## Fuentes

Fuentes de código y documentación fijadas al snapshot heredado:

- [S1] [`profile-engine-v0` en `d6cb420cb86eac69b3b2a3bd3d6cccf903f71b6b`](https://github.com/fraguio/profile-engine-v0/tree/d6cb420cb86eac69b3b2a3bd3d6cccf903f71b6b)
- [S2] [`README.md`](https://github.com/fraguio/profile-engine-v0/blob/d6cb420cb86eac69b3b2a3bd3d6cccf903f71b6b/README.md)
- [S3] [`src/profilecli/cli.py`](https://github.com/fraguio/profile-engine-v0/blob/d6cb420cb86eac69b3b2a3bd3d6cccf903f71b6b/src/profilecli/cli.py)
- [S4] [`src/profilecli/convert_rendercv.py`](https://github.com/fraguio/profile-engine-v0/blob/d6cb420cb86eac69b3b2a3bd3d6cccf903f71b6b/src/profilecli/convert_rendercv.py)
- [S5] [`src/profilecli/validate.py`](https://github.com/fraguio/profile-engine-v0/blob/d6cb420cb86eac69b3b2a3bd3d6cccf903f71b6b/src/profilecli/validate.py)
- [S6] [`schemas/jsonresume.schema.json`](https://github.com/fraguio/profile-engine-v0/blob/d6cb420cb86eac69b3b2a3bd3d6cccf903f71b6b/schemas/jsonresume.schema.json)
- [S7] [`pyproject.toml`](https://github.com/fraguio/profile-engine-v0/blob/d6cb420cb86eac69b3b2a3bd3d6cccf903f71b6b/pyproject.toml)
- [S8] [`.github/workflows/pages.yml`](https://github.com/fraguio/profile-engine-v0/blob/d6cb420cb86eac69b3b2a3bd3d6cccf903f71b6b/.github/workflows/pages.yml)
- [S9] [Template `html/Full.html`](https://github.com/fraguio/profile-engine-v0/blob/d6cb420cb86eac69b3b2a3bd3d6cccf903f71b6b/src/profilecli/templates/profileengine01classic/html/Full.html)
- [S10] [Templates de encabezado e i18n](https://github.com/fraguio/profile-engine-v0/tree/d6cb420cb86eac69b3b2a3bd3d6cccf903f71b6b/src/profilecli/templates/profileengine01classic)
- [S11] [`tests/test_cli.py`](https://github.com/fraguio/profile-engine-v0/blob/d6cb420cb86eac69b3b2a3bd3d6cccf903f71b6b/tests/test_cli.py)
- [S12] [`tests/test_convert_rendercv.py`](https://github.com/fraguio/profile-engine-v0/blob/d6cb420cb86eac69b3b2a3bd3d6cccf903f71b6b/tests/test_convert_rendercv.py)
- [S13] [`tests/test_validate.py`](https://github.com/fraguio/profile-engine-v0/blob/d6cb420cb86eac69b3b2a3bd3d6cccf903f71b6b/tests/test_validate.py)
- [S14] [`docs/architecture.md`](https://github.com/fraguio/profile-engine-v0/blob/d6cb420cb86eac69b3b2a3bd3d6cccf903f71b6b/docs/architecture.md)
- [S15] [ADR heredado 0002 sobre schemas locales](https://github.com/fraguio/profile-engine-v0/blob/d6cb420cb86eac69b3b2a3bd3d6cccf903f71b6b/docs/decisions/0002-schema-sources.md)
- [S22] [`Makefile`](https://github.com/fraguio/profile-engine-v0/blob/d6cb420cb86eac69b3b2a3bd3d6cccf903f71b6b/Makefile)
- [S23] [Runbook de desarrollo local](https://github.com/fraguio/profile-engine-v0/blob/d6cb420cb86eac69b3b2a3bd3d6cccf903f71b6b/docs/runbooks/local-development.md)
- [S24] [Runbook de GitHub Pages](https://github.com/fraguio/profile-engine-v0/blob/d6cb420cb86eac69b3b2a3bd3d6cccf903f71b6b/docs/runbooks/github-pages.md)
- [S27] [Devcontainer](https://github.com/fraguio/profile-engine-v0/blob/d6cb420cb86eac69b3b2a3bd3d6cccf903f71b6b/.devcontainer/devcontainer.json)

Fuentes operativas observadas el 7 de septiembre de 2026; son mutables salvo el run fijado:

- [S16] [Run exitoso del snapshot `d6cb420`](https://github.com/fraguio/profile-engine-v0/actions/runs/24366926658)
- [S17] [Historial de runs de `profile-engine-v0`](https://github.com/fraguio/profile-engine-v0/actions)
- [S18] [HTML desplegado en GitHub Pages](https://fraguio.github.io/profile-engine-v0/)
- [S19] [YAML transformado publicado](https://fraguio.github.io/profile-engine-v0/rendercv_CV.yaml)
- [S26] [Override `_i18n.j2` publicado](https://fraguio.github.io/profile-engine-v0/profileengine01classic/_i18n.j2)
- [S28] [Releases y tags del repositorio heredado](https://github.com/fraguio/profile-engine-v0/releases)

Contratos upstream fijados:

- [S20] [JSON Resume schema `v1.2.1` en `50798e359292ad4448d95b3bb0de5f694d6bcc4b`](https://github.com/jsonresume/resume-schema/blob/50798e359292ad4448d95b3bb0de5f694d6bcc4b/schema.json)
- [S21] [RenderCV `v2.8` en `2eba248100726dc2f75e634bea6b77654e951d0d`](https://github.com/rendercv/rendercv/tree/2eba248100726dc2f75e634bea6b77654e951d0d)

Contexto vigente de la reconstrucción, no evidencia heredada:

- [S25] [Mapa de especificación de la reconstrucción](https://github.com/fraguio/profile-engine/issues/2)

Commits históricos citados:

- [H1] [`0976609`: cargar el schema desde `cwd`](https://github.com/fraguio/profile-engine-v0/commit/097660914251388d6d8fdb88e1875124a50bf460)
- [H2] [`368ac6d`: instalar RenderCV con extras `full`](https://github.com/fraguio/profile-engine-v0/commit/368ac6d4a32222ce21600b3844ca4f734b7d9f02)
- [H3] [`9198a97`: aportar ruta por defecto fuera de `workflow_dispatch`](https://github.com/fraguio/profile-engine-v0/commit/9198a97c5e6fe082236d1c44ffaa84748e11ad94)
- [H4] [`91cf411`: incluir el template HTML ignorado](https://github.com/fraguio/profile-engine-v0/commit/91cf4118ccbf1c773b5696a89c9ae2a4b8098caa)
- [H5] [`cc6fd44`: mapear email, teléfono y web](https://github.com/fraguio/profile-engine-v0/commit/cc6fd448b69f5b4ce2984978c6cbab6ea075a2f8)
- [H6] [`c53d20e`: validar teléfono durante conversión](https://github.com/fraguio/profile-engine-v0/commit/c53d20e5f04d7eacef7e54b4e6438d36ee2564c0)
- [H7] [`45f523b`: enmascarar el teléfono en diagnósticos](https://github.com/fraguio/profile-engine-v0/commit/45f523b19729f74768560597115d155e5a8db751)
- [H8] [`e9233a8`: mostrar solo el nombre en el encabezado](https://github.com/fraguio/profile-engine-v0/commit/e9233a8e1a44adf80f3443bf65199c6438989ef7)
