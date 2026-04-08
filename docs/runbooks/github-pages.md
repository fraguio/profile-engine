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

Disparador:

- `workflow_dispatch` (manual desde la pestaña Actions).

Inputs disponibles:

- `profile_data_ref` (default: `main`): branch, tag o commit SHA de `profile-data`.
- `profile_data_path` (default: `data/resume.json`): ruta del JSON dentro de `profile-data`.

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
