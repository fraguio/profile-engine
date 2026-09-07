# Caracterización de la automatización heredada

## Resumen

La automatización heredada forma una cadena de dos workflows y dos repositorios:

1. Un `push` a `main` del Perfil privado ejecuta un `curl` autenticado contra el endpoint REST de dispatch del repositorio de Profile Engine.
2. Profile Engine recibe `repository_dispatch` con el tipo `profile-data-updated` y ejecuta su workflow desde `main`.
3. El job `build` obtiene el código de Profile Engine, instala la CLI y RenderCV, obtiene aparte el repositorio privado del Perfil y genera un directorio `output/`.
4. Todo `output/` se empaqueta como el artefacto `github-pages`.
5. Un job separado despliega ese artefacto al entorno `github-pages` y GitHub Pages lo sirve públicamente.

La evidencia confirma que el recorrido funcionó, pero no que conserve la identidad causal del `push`: el emisor no envía el SHA del Perfil y el receptor vuelve a leer el `main` que exista al comenzar su checkout. También revela dos credenciales persistentes administradas como secrets, publicación accidental de un YAML intermedio con datos derivados del Perfil, falta de propagación del resultado al repositorio origen y una superficie de inyección de shell en un campo opcional de `client_payload`.

Este documento caracteriza la versión heredada. Sus nombres, pasos, herramientas y decisiones no son requisitos para la reconstrucción y no se presupone compatibilidad.

## Corte y fuentes de evidencia

La investigación se realizó el 7 de septiembre de 2026 sobre estos snapshots:

- Receptor heredado público: [`fraguio/profile-engine-v0@d6cb420`](https://github.com/fraguio/profile-engine-v0/tree/d6cb420cb86eac69b3b2a3bd3d6cccf903f71b6b), último commit de `main` en el corte.
- Emisor privado: [`fraguio/profile-data@d173809`](https://github.com/fraguio/profile-data/tree/d17380908305a50a4c56792edb331535d00f026f), último commit de `main` en el corte. Este enlace exige acceso al repositorio privado.
- Ejecución emparejada más reciente: [emisor `24355404296`](https://github.com/fraguio/profile-data/actions/runs/24355404296) y [receptor `24355408692`](https://github.com/fraguio/profile-engine-v0/actions/runs/24355408692).
- Acciones de terceros: todas las referencias `uses:` del receptor están fijadas a SHA completo; se inspeccionaron exactamente esos commits.
- Documentación oficial de GitHub consultada en la fecha del corte. Para REST se indica la versión aplicable cuando procede.

La API permite observar los nombres y fechas de actualización de los secrets, pero no sus valores, clase de token ni permisos efectivos. Los logs y artefactos históricos ya habían caducado; por ello no se pueden reconstruir las versiones exactas que resolvió `pip` ni inspeccionar el tar de aquella ejecución. No se ha inferido esa información.

## Recorrido extremo a extremo

```text
push a profile-data/main
        |
        v
dispatch-profile-engine.yml
  POST /repos/fraguio/profile-engine/dispatches
  event_type = profile-data-updated
        |
        v
pages.yml de Profile Engine, desde su rama por defecto
        |
        v
build (ubuntu-latest)
  checkout Profile Engine
  setup Python 3.12
  pip install Profile Engine + RenderCV
  checkout privado profile-data
  profilectl html
  upload output/ como artifact github-pages
        |
        v
deploy (entorno github-pages)
  pages:write + OIDC
        |
        v
https://fraguio.github.io/profile-engine-v0/
```

### 1. Evento en el repositorio fuente

El workflow emisor se activa ante **cualquier** `push` a `main`; no filtra rutas ni distingue cambios del documento fuente de otros cambios. Su único job ejecuta un `POST` con `event_type: profile-data-updated`, sin `client_payload`, usando `PROFILE_ENGINE_DISPATCH_TOKEN` como Bearer token ([workflow emisor, líneas 3-19](https://github.com/fraguio/profile-data/blob/d17380908305a50a4c56792edb331535d00f026f/.github/workflows/dispatch-profile-engine.yml#L3-L19)).

El endpoint oficial `POST /repos/{owner}/{repo}/dispatches` acepta ese tipo y opcionalmente un `client_payload`; una respuesta `204` solo confirma que GitHub aceptó crear el evento, no que el workflow receptor haya terminado correctamente ([REST API, versión `2022-11-28`](https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#create-a-repository-dispatch-event)).

La llamada heredada presenta tres propiedades operativas:

- No incluye SHA, ref, ruta, identificador de correlación ni URL de la ejecución origen. El contrato transmitido se reduce al literal `profile-data-updated`.
- No envía `X-GitHub-Api-Version`; GitHub asigna a solicitudes sin cabecera la versión por defecto `2022-11-28` ([versionado REST](https://docs.github.com/en/rest/about-the-rest-api/api-versions#specifying-an-api-version)).
- No usa `--fail` ni `--fail-with-body`. Según la documentación de curl, esas opciones son las que convierten respuestas HTTP de error en fallo del proceso; por tanto, una respuesta HTTP `4xx` o `5xx` puede dejar verde el step emisor. La referencia online consultada documenta curl `8.22.1`; la versión exacta del runner histórico no quedó recuperable ([manual de curl](https://curl.se/docs/manpage.html#-f)).

### 2. Recepción y selección de entrada

El receptor admite tres eventos ([workflow receptor, líneas 3-19](https://github.com/fraguio/profile-engine-v0/blob/d6cb420cb86eac69b3b2a3bd3d6cccf903f71b6b/.github/workflows/pages.yml#L3-L19)):

| Evento | Alcance | Selección del Perfil |
| --- | --- | --- |
| `push` | `main` del propio Profile Engine | Defaults `main` y `data/resume.json` |
| `workflow_dispatch` | Ejecución manual | Inputs obligatorios `profile_data_ref` y `profile_data_path`, ambos con default |
| `repository_dispatch` | Solo tipo `profile-data-updated` | Campos opcionales homónimos de `client_payload`; si faltan, defaults |

Las expresiones del job priorizan `client_payload` para `repository_dispatch`, después los inputs manuales y finalmente `main` / `data/resume.json` ([líneas 34-38](https://github.com/fraguio/profile-engine-v0/blob/d6cb420cb86eac69b3b2a3bd3d6cccf903f71b6b/.github/workflows/pages.yml#L34-L38)). Como el emisor real no manda payload, el recorrido automático siempre solicita el `main` y `data/resume.json` disponibles en el momento del build.

GitHub solo dispara `repository_dispatch` si el workflow existe en la rama por defecto. Para ese evento, `GITHUB_REF` es la rama por defecto y `GITHUB_SHA` su último commit, no el commit del repositorio emisor ([eventos de Actions](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#repository_dispatch)). Esto explica que la ejecución emparejada tuviera dos identidades distintas:

- Origen: `profile-data@d173809`, creado a las `16:46:09Z` y finalizado a las `16:46:15Z` ([run emisor](https://github.com/fraguio/profile-data/actions/runs/24355404296)).
- Receptor: `profile-engine@fcdd246`, creado a las `16:46:15Z` y finalizado a las `16:46:55Z` ([run receptor](https://github.com/fraguio/profile-engine-v0/actions/runs/24355408692)).

No hay un enlace causal persistido entre ambos runs más allá de la proximidad temporal, el actor y el tipo de evento.

### 3. Autenticación y acceso al Perfil privado

Hay cuatro identidades o credenciales diferentes:

| Credencial | Dónde reside | Uso observado | Alcance conocido y desconocido |
| --- | --- | --- | --- |
| `PROFILE_ENGINE_DISPATCH_TOKEN` | Secret de Actions en `profile-data` | Autoriza el `POST` al receptor | Existe en el corte. Su tipo y permisos reales no son visibles. La API exige `repo` para PAT classic o `Contents: write` sobre el receptor para tokens fine-grained. |
| `GITHUB_TOKEN` del emisor | Token efímero de su run | No se referencia explícitamente | El repositorio tenía permiso por defecto de solo lectura. No sustituye al token entre repositorios. |
| `PROFILE_DATA_REPO_TOKEN` | Secret de Actions en el receptor | `actions/checkout` del Perfil privado | Existe en el corte. El runbook heredado recomienda fine-grained `Contents: Read`, pero la configuración efectiva no es observable ([runbook, líneas 9-18](https://github.com/fraguio/profile-engine-v0/blob/d6cb420cb86eac69b3b2a3bd3d6cccf903f71b6b/docs/runbooks/github-pages.md#L9-L18)). |
| `GITHUB_TOKEN` del receptor | Token efímero de cada job | Checkout del receptor y API de Pages | Sus permisos están declarados por workflow/job; no da lectura al Perfil privado. |

`actions/checkout` confirma que `${{ github.token }}` está limitado al repositorio actual y que un segundo repositorio privado necesita un PAT propio ([`actions/checkout@de0fac2`, líneas 275-290](https://github.com/actions/checkout/blob/de0fac2e4500dabe0009e67214ff5f5447ce83dd/README.md#L275-L290)). El receptor lo aporta en `token`, obtiene `${{ github.repository_owner }}/profile-data` en `external/profile-data` y selecciona la ref calculada ([workflow, líneas 51-57](https://github.com/fraguio/profile-engine-v0/blob/d6cb420cb86eac69b3b2a3bd3d6cccf903f71b6b/.github/workflows/pages.yml#L51-L57)).

Al no configurar sparse checkout, queda disponible en el runner el árbol completo de esa ref, no solo `data/resume.json`. Checkout trae un único commit por defecto y conserva la credencial para comandos Git posteriores hasta el cleanup del job ([`actions/checkout@de0fac2`, líneas 20-25](https://github.com/actions/checkout/blob/de0fac2e4500dabe0009e67214ff5f5447ce83dd/README.md#L20-L25), [líneas 57-75](https://github.com/actions/checkout/blob/de0fac2e4500dabe0009e67214ff5f5447ce83dd/README.md#L57-L75)).

Los secrets no viajan en el dispatch. Cada repositorio administra el suyo y GitHub entrega un secret únicamente al runner del workflow que lo referencia. Si falta un secret, la expresión produce una cadena vacía ([documentación de secrets](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions#using-secrets-in-a-workflow)).

### 4. Ejecución de la generación

El job `build` corre en `ubuntu-latest` y realiza estos pasos ([workflow, líneas 34-76](https://github.com/fraguio/profile-engine-v0/blob/d6cb420cb86eac69b3b2a3bd3d6cccf903f71b6b/.github/workflows/pages.yml#L34-L76)):

1. Checkout del Profile Engine asociado al evento receptor.
2. Instalación de una versión `3.12` de Python.
3. `pip install . "rendercv[full]>=2.8,<2.9"`.
4. Checkout del Perfil privado.
5. Ejecución de `profilectl html` con entrada bajo `external/profile-data/` y salidas `output/rendercv_CV.yaml` y `output/index.html`.
6. Comprobación exclusiva de que `output/index.html` existe y listado recursivo de nombres bajo `output/`.
7. Upload de todo `output/` como artefacto de Pages.

`profilectl html` valida la entrada, la convierte a YAML y llama a RenderCV para producir HTML ([CLI, líneas 379-415](https://github.com/fraguio/profile-engine-v0/blob/d6cb420cb86eac69b3b2a3bd3d6cccf903f71b6b/src/profilecli/cli.py#L379-L415)). La llamada desactiva PDF, PNG y Typst, crea un Markdown temporal y lo elimina al finalizar ([líneas 193-258](https://github.com/fraguio/profile-engine-v0/blob/d6cb420cb86eac69b3b2a3bd3d6cccf903f71b6b/src/profilecli/cli.py#L193-L258)). No hay prueba semántica del HTML ni smoke test de la URL publicada.

La ejecución no es reproducible a partir del commit solamente:

- `ubuntu-latest` y el patch concreto de Python son móviles.
- RenderCV admite cualquier versión `>=2.8,<2.9`.
- Las dependencias de `profilectl` son rangos o carecen de límite inferior/superior completo; `jsonschema` no tiene versión declarada ([`pyproject.toml`, líneas 1-10](https://github.com/fraguio/profile-engine-v0/blob/d6cb420cb86eac69b3b2a3bd3d6cccf903f71b6b/pyproject.toml#L1-L10)).
- No hay lockfile, hashes ni artefacto de entorno.

En contraste, las cuatro actions están fijadas a commits completos e identificadas en comentarios como `checkout v6.0.2`, `setup-python v6.2.0`, `upload-pages-artifact v5.0.0` y `deploy-pages v5.0.0` ([workflow, líneas 40-49](https://github.com/fraguio/profile-engine-v0/blob/d6cb420cb86eac69b3b2a3bd3d6cccf903f71b6b/.github/workflows/pages.yml#L40-L49), [51-74](https://github.com/fraguio/profile-engine-v0/blob/d6cb420cb86eac69b3b2a3bd3d6cccf903f71b6b/.github/workflows/pages.yml#L51-L74) y [88-90](https://github.com/fraguio/profile-engine-v0/blob/d6cb420cb86eac69b3b2a3bd3d6cccf903f71b6b/.github/workflows/pages.yml#L88-L90)). El workflow fuerza además Node 24 para actions JavaScript ([líneas 30-31](https://github.com/fraguio/profile-engine-v0/blob/d6cb420cb86eac69b3b2a3bd3d6cccf903f71b6b/.github/workflows/pages.yml#L30-L31)).

### 5. Artefactos y contenido publicado

El artefacto contiene más que el CV HTML:

- `output/index.html`.
- `output/rendercv_CV.yaml`, que serializa datos convertidos del Perfil; el conversor incluye, entre otros, email, teléfono, experiencia, educación, skills e idiomas ([conversor, líneas 129-133](https://github.com/fraguio/profile-engine-v0/blob/d6cb420cb86eac69b3b2a3bd3d6cccf903f71b6b/src/profilecli/convert_rendercv.py#L129-L133) y [313-369](https://github.com/fraguio/profile-engine-v0/blob/d6cb420cb86eac69b3b2a3bd3d6cccf903f71b6b/src/profilecli/convert_rendercv.py#L313-L369)).
- Overrides de templates copiados junto al YAML en `profileengine01classic/`, `markdown/` y `html/` ([CLI, líneas 140-169](https://github.com/fraguio/profile-engine-v0/blob/d6cb420cb86eac69b3b2a3bd3d6cccf903f71b6b/src/profilecli/cli.py#L140-L169)).

`actions/upload-pages-artifact@fc324d3` crea por defecto un artefacto llamado `github-pages`, tarifica el directorio indicado y establece retención de un día ([`action.yml`, líneas 4-17](https://github.com/actions/upload-pages-artifact/blob/fc324d3547104276b827a68afc52ff2a11cc49c9/action.yml#L4-L17) y [28-89](https://github.com/actions/upload-pages-artifact/blob/fc324d3547104276b827a68afc52ff2a11cc49c9/action.yml#L28-L89)). En la ejecución emparejada se observó un artefacto comprimido de 9.543 bytes, creado el 13 de abril y expirado el 14 de abril de 2026.

Pages publica el contenido completo del tar, no solo `index.html`. En el corte respondían `200 OK` tanto la [raíz HTML](https://fraguio.github.io/profile-engine-v0/) como [`rendercv_CV.yaml`](https://fraguio.github.io/profile-engine-v0/rendercv_CV.yaml) y un [template de Markdown](https://fraguio.github.io/profile-engine-v0/profileengine01classic/SectionBeginning.j2.md). Por tanto, el YAML intermedio derivado del Perfil privado quedó públicamente descargable; la caducidad del artefacto de Actions no retira la versión desplegada en Pages.

### 6. Despliegue, permisos y protección

El workflow declara globalmente `contents: read`, `pages: write` e `id-token: write` ([líneas 21-24](https://github.com/fraguio/profile-engine-v0/blob/d6cb420cb86eac69b3b2a3bd3d6cccf903f71b6b/.github/workflows/pages.yml#L21-L24)). Esos permisos llegan al job `build`, incluidos sus scripts, dependencias instaladas y ambos checkouts.

El job `deploy`:

- depende de `build`;
- redefine sus permisos a `pages: write` e `id-token: write`, por lo que los permisos no declarados quedan en `none`;
- usa el entorno `github-pages` y publica como URL de entorno el output `page_url`;
- ejecuta `actions/deploy-pages@cd2ce8f` sin inputs, por lo que consume el artefacto por defecto `github-pages` ([workflow, líneas 78-90](https://github.com/fraguio/profile-engine-v0/blob/d6cb420cb86eac69b3b2a3bd3d6cccf903f71b6b/.github/workflows/pages.yml#L78-L90), [`deploy-pages`, líneas 13-55](https://github.com/actions/deploy-pages/blob/cd2ce8fcbc39b97be8ca5fce6e763baed58fa128/README.md#L13-L55)).

GitHub Pages requiere precisamente `pages: write` para crear el despliegue e `id-token: write` para solicitar un JWT OIDC único del job. Pages valida con él la rama/ref de origen ([`deploy-pages`, líneas 77-90](https://github.com/actions/deploy-pages/blob/cd2ce8fcbc39b97be8ca5fce6e763baed58fa128/README.md#L77-L90), [workflows personalizados de Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages#deploying-github-pages-artifacts)). OIDC no sustituye a los dos tokens entre repositorios; solo interviene en el despliegue de Pages.

El estado vivo observado por API era:

- Pages habilitado con `build_type: workflow`, HTTPS forzado y URL `https://fraguio.github.io/profile-engine-v0/` ([API de Pages](https://api.github.com/repos/fraguio/profile-engine-v0/pages)).
- Entorno `github-pages` sin reviewers ni wait timer, con una política que solo admite la rama `main` ([API del entorno](https://api.github.com/repos/fraguio/profile-engine-v0/environments/github-pages), [política de ramas](https://api.github.com/repos/fraguio/profile-engine-v0/environments/github-pages/deployment-branch-policies)).
- Ningún secret de entorno. `PROFILE_DATA_REPO_TOKEN` es de repositorio y queda disponible en `build`, que no está sujeto al entorno.

### 7. Concurrencia y semántica de entrega

Todos los eventos comparten el grupo de concurrencia estático `pages`; `cancel-in-progress: false` evita cancelar el run que ya está ejecutándose ([workflow, líneas 26-28](https://github.com/fraguio/profile-engine-v0/blob/d6cb420cb86eac69b3b2a3bd3d6cccf903f71b6b/.github/workflows/pages.yml#L26-L28)). Sin embargo, la semántica por defecto solo conserva un run pendiente por grupo y una llegada posterior cancela al pendiente anterior ([documentación de concurrencia](https://docs.github.com/en/actions/concepts/workflows-and-actions/concurrency)). En una ráfaga puede perderse la generación de estados intermedios aunque el run activo no se cancele.

No existe confirmación extremo a extremo:

- El emisor termina después de solicitar el evento y no espera el build o deploy.
- El receptor no informa estado ni URL al repositorio origen.
- No hay retry explícito, deduplicación, idempotency key ni correlación.
- La generación lee una rama móvil, así que varios eventos pueden acabar publicando el mismo último estado y no necesariamente el commit que originó cada evento.

## Evidencia operativa

La historia del workflow receptor conservaba nueve runs con evento `repository_dispatch`; los nueve constaban como exitosos en el corte. El más reciente recorrió con éxito todos los steps de `build`, incluido el checkout privado, la generación y el upload, y después el job `deploy` ([run `24355408692`](https://github.com/fraguio/profile-engine-v0/actions/runs/24355408692)). Esto demuestra viabilidad y una ejecución correcta concreta, no garantías de entrega o reproducibilidad.

También hay runs manuales y por `push`, incluidos fallos durante la evolución del workflow. Por tanto, el historial de Pages mezcla publicaciones causadas por cambios de datos, cambios del motor y pruebas manuales; el sitio no expone cuál de esas causas produjo su contenido actual.

## Riesgos y restricciones revelados

| Hallazgo | Consecuencia observada o posible |
| --- | --- |
| `output/` completo es la raíz pública | El YAML intermedio con datos derivados del Perfil y los templates están publicados junto al HTML. |
| `client_payload.profile_data_path` se interpola directamente y sin comillas dentro de `run:` | Un emisor autorizado puede introducir sintaxis de shell. GitHub considera los contextos controlables por actores como entrada no confiable y recomienda no insertarlos directamente en scripts ([secure use](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions#good-practices-for-mitigating-script-injection-attacks)). |
| El endpoint de dispatch exige una credencial con escritura sobre el receptor | La capacidad necesaria para emitir el evento implica más autoridad que una señal anónima; el tipo, propietario, expiración, rotación y alcance reales del token heredado no están documentados. |
| El receptor necesita otro token de lectura sobre el Perfil | Una dependencia, action o script comprometido durante `build` puede leer el árbol privado y la credencial persistida durante el job. |
| `pages: write` e `id-token: write` están concedidos también a `build` | La frontera de privilegios no coincide con la separación `build` / `deploy`; esos permisos están disponibles antes de aplicar el entorno de despliegue. |
| El evento no identifica el SHA del Perfil | No hay trazabilidad ni garantía de construir exactamente el estado que produjo el `push`; existe una carrera con cambios posteriores de `main`. |
| El emisor no falla necesariamente ante errores HTTP y no espera al receptor | Un run verde en `profile-data` no prueba recepción, generación ni publicación. |
| Concurrencia con un único pendiente | Una ráfaga puede cancelar eventos pendientes intermedios. |
| Dependencias Python y runner móviles | Repetir un commit puede producir un entorno y resultado diferentes. Los SHAs completos de actions reducen, pero no eliminan, esta variabilidad. |
| Validación final limitada a existencia de `index.html` | Un HTML vacío, incorrecto o con exposición no intencionada puede superar el gate. |
| Todo `push` a `main` de ambos repositorios puede publicar | Cambios no relacionados con el Perfil pueden consumir capacidad y reemplazar el sitio. |
| Nombres de repositorio codificados | El emisor está acoplado a `fraguio/profile-engine` y el receptor a `${owner}/profile-data`; un rename o una reconstrucción bajo el nombre anterior cambia el destino real. |

### Deriva actual por renombrado

El snapshot privado todavía hace `POST` a `repos/fraguio/profile-engine/dispatches` ([línea 18](https://github.com/fraguio/profile-data/blob/d17380908305a50a4c56792edb331535d00f026f/.github/workflows/dispatch-profile-engine.yml#L18)). En abril de 2026 ese nombre correspondía al sistema cuyos runs hoy aparecen bajo `profile-engine-v0`; el emparejamiento temporal anterior lo confirma. En el corte actual:

- el repositorio heredado se llama [`fraguio/profile-engine-v0`](https://api.github.com/repos/fraguio/profile-engine-v0), fue creado el 27 de marzo y conserva el workflow receptor;
- el nombre [`fraguio/profile-engine`](https://api.github.com/repos/fraguio/profile-engine) pertenece a este repositorio limpio, creado el 7 de septiembre y sin Pages habilitado.

Por ello, el emisor conservado ya no apunta al receptor heredado. Un futuro `push` al Perfil solicitaría un dispatch al repositorio limpio. Esta es deriva operacional existente, no una recomendación para el diseño nuevo.

## Restricciones de la plataforma observadas

Estas son condiciones de GitHub usadas por el sistema heredado, no decisiones adoptadas para su reemplazo:

- Un `repository_dispatch` ejecuta el workflow de la rama por defecto del receptor, no código procedente del emisor.
- El `GITHUB_TOKEN` de un workflow no puede obtener por sí solo otro repositorio privado; hace falta una identidad con acceso adicional.
- Un despliegue Pages mediante Actions consume un artefacto con formato Pages y necesita `pages: write`, `id-token: write` y una ref admitida por el entorno.
- Los permisos declarados a nivel de job reemplazan los globales y todo permiso omitido pasa a `none` ([sintaxis de `permissions`](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#permissions)).
- Un job que referencia un entorno debe superar sus reglas antes de ejecutarse; esa protección no alcanza jobs que no referencian el entorno ([documentación de entornos](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments#how-environments-relate-to-deployments)).

## Decisiones y niebla nuevas

La investigación no toma decisiones de diseño. Deja explícitas estas preguntas para la especificación:

1. **Unidad causal:** ¿la publicación representa un SHA exacto del Perfil o deliberadamente el último estado de una rama al iniciar el build?
2. **Frontera pública:** ¿qué derivados del Perfil pueden ser públicos además de `index.html`, si alguno?
3. **Semántica de entrega:** ¿se exige confirmación extremo a extremo, correlación, retries, orden, deduplicación o conservación de cada estado intermedio?
4. **Autoridad entre repositorios:** ¿qué principal será propietario de cada permiso, con qué alcance, expiración y rotación? Los permisos reales de los tokens heredados siguen siendo niebla.
5. **Contrato del evento:** ¿qué campos son admitidos y confiables, y qué validación requieren refs y rutas antes de usarse?
6. **Ámbito de disparo:** ¿deben publicar todos los pushes a `main`, solo cambios del Perfil, también cambios del motor y ejecuciones manuales?
7. **Reproducibilidad:** ¿qué versiones del runner, Python y dependencias forman parte de la identidad verificable de una publicación?
8. **Gobierno del despliegue:** ¿qué ramas, revisiones o gates deben poder reemplazar el sitio público?
9. **Identidad del destino:** el emisor heredado apunta hoy al nombre ocupado por la reconstrucción limpia; queda por decidir cuándo y cómo se retira o sustituye esa automatización para evitar señales ambiguas.

## Referencias primarias

- [Workflow receptor heredado, snapshot `d6cb420`](https://github.com/fraguio/profile-engine-v0/blob/d6cb420cb86eac69b3b2a3bd3d6cccf903f71b6b/.github/workflows/pages.yml).
- [Workflow emisor privado, snapshot `d173809`](https://github.com/fraguio/profile-data/blob/d17380908305a50a4c56792edb331535d00f026f/.github/workflows/dispatch-profile-engine.yml).
- [CLI heredada, snapshot `d6cb420`](https://github.com/fraguio/profile-engine-v0/blob/d6cb420cb86eac69b3b2a3bd3d6cccf903f71b6b/src/profilecli/cli.py) y [conversor](https://github.com/fraguio/profile-engine-v0/blob/d6cb420cb86eac69b3b2a3bd3d6cccf903f71b6b/src/profilecli/convert_rendercv.py).
- [Runbook de Pages heredado](https://github.com/fraguio/profile-engine-v0/blob/d6cb420cb86eac69b3b2a3bd3d6cccf903f71b6b/docs/runbooks/github-pages.md).
- GitHub Docs: [`repository_dispatch`](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#repository_dispatch), [Create a repository dispatch event, REST `2022-11-28`](https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#create-a-repository-dispatch-event), [`permissions`](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#permissions), [concurrencia](https://docs.github.com/en/actions/concepts/workflows-and-actions/concurrency), [secrets](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions), [secure use](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions) y [Pages con workflows personalizados](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).
- Actions fijadas: [`checkout@de0fac2`](https://github.com/actions/checkout/tree/de0fac2e4500dabe0009e67214ff5f5447ce83dd), [`setup-python@a309ff8`](https://github.com/actions/setup-python/tree/a309ff8b426b58ec0e2a45f0f869d46889d02405), [`upload-pages-artifact@fc324d3`](https://github.com/actions/upload-pages-artifact/tree/fc324d3547104276b827a68afc52ff2a11cc49c9) y [`deploy-pages@cd2ce8f`](https://github.com/actions/deploy-pages/tree/cd2ce8fcbc39b97be8ca5fce6e763baed58fa128).
