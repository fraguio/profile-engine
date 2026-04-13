# profile-engine

![Python](https://img.shields.io/badge/python-3.12+-blue)
![Tests](https://img.shields.io/badge/tests-pytest-green)
![Status](https://img.shields.io/badge/status-active--development-orange)

`profile-engine` es un pipeline backend determinista diseñado para validar y transformar datos de perfil estructurados de forma predecible y automatizable.

Como consumer independiente de JSON Resume, no conoce ni depende de otros consumers del mismo dominio.

La interfaz pública del pipeline es `profilectl`: valida contratos JSON Resume y genera YAML compatible con RenderCV mediante `convert`, priorizando consistencia, trazabilidad y facilidad de integración en pipelines.

## Caso de uso

Este proyecto está diseñado para integrarse en flujos automatizados (CI/CD o pipelines locales) con el objetivo de generar y validar currículums de forma reproducible a partir de una fuente versionada.

Flujo típico:

1. Almacenar `resume.json` en un repositorio privado
2. Validar estructura y contenido con `profilectl validate`
3. Convertir al formato de salida (RenderCV) con `profilectl convert`
4. Publicar el CV generado mediante un workflow de CI/CD (por ejemplo, GitHub Pages)

Este enfoque garantiza consistencia, trazabilidad y control total sobre el proceso de generación del CV.

## Por qué existe

La mayoría de herramientas de CV optimizan la presentación. Este proyecto prioriza fiabilidad operativa:

- contrato de entrada explícito
- transformación predecible
- errores estables para automatización
- ejecución por CLI para scripts y CI

## Qué demuestra

- diseño por capas: CLI, validación y transformación desacopladas
- contratos de datos como frontera del sistema
- comportamiento determinista para testing y pipelines reproducibles
- decisiones técnicas pequeñas y trazables en `docs/decisions/`
- simplicidad intencional: resolver un flujo concreto sin sobreingeniería

## Capacidades clave

- `validate`: valida JSON Resume con salida de error consistente
- `convert`: transforma JSON Resume a RenderCV YAML
- `render-html`: transforma RenderCV YAML a HTML publicable
- `html`: ejecuta el pipeline completo (validate -> convert -> render-html)
- entrada por archivo o `stdin`; salida por `stdout` o fichero
- ejecución estable en local, scripts y CI

## CLI

| Comando | Input | Output |
|---|---|---|
| `profilectl validate` | Input JSON Resume file | `stdout` (`OK`) y exit code |
| `profilectl convert` | Input JSON Resume file | RenderCV YAML (`stdout` o `-o`) |
| `profilectl render-html` | Input RenderCV YAML file | Output HTML file (`-o`) |
| `profilectl html` | Input JSON Resume file | YAML intermedio (`-o`) + HTML final (`--html-output`) |

Flujo recomendado:

```bash
profilectl validate -i examples/resume.example.json
profilectl convert -i examples/resume.example.json -o output/rendercv_CV.yaml
profilectl render-html -i output/rendercv_CV.yaml -o output/index.html
```

Pipeline en un comando:

```bash
profilectl html -i examples/resume.example.json -o output/rendercv_CV.yaml --html-output output/index.html
```

Nota: `profilectl` no expone flags de tema/idioma (`--theme`, `--locale`).
La personalizacion visual y de locale se realiza editando el YAML RenderCV (`design`, `locale`).
Por defecto, `convert` genera `design.theme: profileengine01classic` y `locale.language: spanish`.
Al generar YAML o HTML, `profilectl` sincroniza automaticamente los overrides versionados de
`src/profilecli/templates/` junto al YAML de entrada para que RenderCV los aplique en todos los formatos.

## Alcance

Resuelve un problema acotado: convertir de forma confiable un contrato JSON conocido a un formato de salida concreto.

El contrato de datos es la frontera del sistema y permite integrar `profilectl` con cualquier proveedor de JSON Resume válido.

No intenta cubrir, por ahora, edición visual, múltiples targets de exportación, versionado de perfiles ni orquestación distribuida.

## Uso real

### Ejemplo completo

Entrada (`examples/resume.example.json`):

```json
{
  "basics": {
    "name": "Jane Doe",
    "label": "Senior Backend Developer"
  }
}
```

Comando:

```bash
profilectl convert examples/resume.example.json
```

Salida (YAML generado):

```yaml
basics:
  name: Jane Doe
  label: Senior Backend Developer
```

### Automatización

Puedes ejecutar el flujo completo hasta HTML publicable mediante:

```bash
make html IN="../profile-data/data/resume.json" OUT="output/rendercv_CV.yaml" HTML_OUT="output/index.html"
```

Esto genera:

- `output/rendercv_CV.yaml`
- `output/index.html`

Ejemplos representativos de uso en local y en pipelines:

### Validar datos de entrada

```bash
profilectl validate examples/resume.example.json
```

### Convertir (salida por stdout)

Por defecto, la salida se escribe en stdout:

```bash
profilectl convert examples/resume.example.json
```

### Convertir a fichero

```bash
profilectl convert examples/resume.example.json -o out.yaml
```

### Pipeline E2E (validate -> convert -> render HTML)

```bash
make html IN="../profile-data/data/resume.json" OUT="output/rendercv_CV.yaml" HTML_OUT="output/index.html"
```

Comando equivalente directo con `profilectl`:

```bash
profilectl html --input "../profile-data/data/resume.json" --output "output/rendercv_CV.yaml" --html-output "output/index.html"
```

También puedes usar el argumento posicional:

```bash
profilectl html ../profile-data/data/resume.json --output output/rendercv_CV.yaml --html-output output/index.html
```

### Convertir desde stdin

Puedes proporcionar la entrada a través de `stdin` usando `-i -`.

#### Ejemplo con archivo (pipe)

```bash
cat examples/resume.example.json | profilectl convert -i -
```

#### Ejemplo mínimo (recomendado)

Uso de `printf` para evitar problemas de formato:

```bash
printf '%s' '{}' | profilectl convert -i -
```

#### Ejemplo mínimo con `echo` (simple, pero menos robusto que `printf`)

```bash
echo '{}' | profilectl convert -i -
```

#### Ejemplo inline más completo

```bash
printf '%s' '{
  "basics": {
    "name": "Jane Doe",
    "label": "Senior Backend Developer"
  }
}' | profilectl convert -i -
```

## Desarrollo

El repositorio incluye soporte para Dev Container, proporcionando un entorno reproducible con Python 3.12 y dependencias preconfiguradas.

También es posible trabajar en local mediante un entorno virtual (`.venv`).

## Arquitectura

`docs/architecture.md`

## Documentación relacionada

- `docs/architecture.md`
- `docs/cli.md`
- `docs/workflows/golden-path.md`
- `docs/runbooks/github-pages.md`
- `docs/decisions/`
