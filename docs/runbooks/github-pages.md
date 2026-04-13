# Runbook: publicacion en GitHub Pages

## Objetivo

Publicar un CV HTML generado por `profilectl` en GitHub Pages usando este repositorio (`profile-engine`) como validacion inicial.

## Alcance

- El deploy ocurre en Pages del mismo repo donde vive el workflow.
- El dato fuente (`resume.json`) se obtiene desde el repo privado `profile-data`.
- La rama/ref de `profile-data` es parametrizable en cada ejecucion.

## Requisitos

- GitHub Pages habilitado en `profile-engine` con fuente `GitHub Actions`.
- Secret del repositorio: `PROFILE_DATA_REPO_TOKEN`.
  - Debe tener permiso de lectura sobre `profile-data`.
  - Recomendado: fine-grained token con acceso minimo (`Contents: Read`).

## Workflow

Archivo: `.github/workflows/pages.yml`.

Runtime y versiones relevantes:

- Se fuerza runtime Node 24 para acciones JavaScript con `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: "true"`.
- Acciones usadas actualmente:
  - `actions/checkout@v6`
  - `actions/setup-python@v6`
  - `actions/upload-pages-artifact@v5.0.0`
  - `actions/deploy-pages@v5.0.0`

Disparador:

- `workflow_dispatch` (manual desde la pestaña Actions).
- `repository_dispatch` con tipo `profile-data-updated`.

Inputs disponibles:

- `profile_data_ref` (default: `main`): branch, tag o commit SHA de `profile-data`.
- `profile_data_path` (default: `data/resume.json`): ruta del JSON dentro de `profile-data`.

Para `repository_dispatch`, se leen estos campos opcionales en `client_payload`:

- `profile_data_ref`
- `profile_data_path`

Si no llegan en el payload, se usan los defaults (`main` y `data/resume.json`).

Pasos que ejecuta:

1. Checkout de `profile-engine`.
2. Instalacion de `profilectl` y `rendercv`.
3. Checkout de `${{ github.repository_owner }}/profile-data` con `PROFILE_DATA_REPO_TOKEN`.
4. Generacion de `output/rendercv_CV.yaml` y `output/index.html` con:

```bash
profilectl html \
  --input external/profile-data/<profile_data_path> \
  --output output/rendercv_CV.yaml \
  --html-output output/index.html
```

`profilectl` sincroniza automaticamente los overrides versionados de `src/profilecli/templates/`
junto al YAML generado para que RenderCV aplique:

- theme custom `profileengine01classic` (Typst/PDF/PNG)
- i18n de literales en Markdown/HTML
- estilos HTML alineados con los colores del theme

5. Subida del artefacto Pages desde `output/`.
6. Deploy con `actions/deploy-pages`.

## Operacion

1. Ir a `Actions` en `profile-engine`.
2. Ejecutar `Publish CV to GitHub Pages`.
3. Elegir `profile_data_ref` (por ejemplo, `main` o una rama de pruebas).
4. Ajustar `profile_data_path` si aplica.
5. Verificar URL publicada al finalizar el job `deploy`.

## Notas

- Este flujo no agrega un comando `profilectl publish`; la publicacion se mantiene en CI/CD.
- El despliegue objetivo final en `profile-site` puede agregarse despues como flujo separado.
- Se usa `actions/upload-pages-artifact@v5.0.0` (tag exacto) para evitar errores de resolucion con `@v5`.
