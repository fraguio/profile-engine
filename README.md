# profile-engine

![Python](https://img.shields.io/badge/python-3.12+-blue)
![Tests](https://img.shields.io/badge/tests-pytest-green)
![Status](https://img.shields.io/badge/status-active--development-orange)

`profile-engine` es una CLI orientada a backend diseñada para validar,
transformar y renderizar perfiles profesionales estructurados (JSON
Resume / RenderCV).

Aborda la generación de CV como un **pipeline de datos**, poniendo el
foco en determinismo, validación y automatización, en lugar de en el
formato.

------------------------------------------------------------------------

## Por qué existe este proyecto

La mayoría de herramientas de CV se centran en el diseño y la
presentación.

Este proyecto trata el problema como un sistema backend:

-   Validación estricta de entrada (JSON Schema)
-   Transformaciones explícitas y testeables
-   Salidas y manejo de errores deterministas
-   Diseño CLI-first orientado a automatización

Esto refleja cómo los sistemas backend reales gestionan pipelines de
datos estructurados.

------------------------------------------------------------------------

## Qué demuestra este proyecto

-   Diseño de CLI orientado a backend (separación clara de
    responsabilidades)
-   Validación determinista y reporting de errores consistente
-   Pipelines de transformación de datos (JSON → YAML)
-   Workflows preparados para automatización (local y CI)
-   Estructura mantenible para desarrollo asistido por IA

------------------------------------------------------------------------

## Funcionalidades principales

-   Validar JSON Resume contra su schema con errores deterministas
-   Convertir perfiles estructurados a YAML compatible con RenderCV
-   CLI diseñada para workflows reproducibles y automatizables
-   Suite de tests completa con pytest

------------------------------------------------------------------------

## Uso

Instalación en modo editable:

``` bash
pip install -e .
```

### Validar datos de entrada

``` bash
profilectl validate examples/resume.example.json
```

### Convertir (salida por stdout)

Por defecto, la salida se escribe en stdout:

``` bash
profilectl convert examples/resume.example.json
```

### Convertir a fichero

``` bash
profilectl convert examples/resume.example.json -o out.yaml
```

### Convertir desde stdin

Puedes proporcionar la entrada a través de `stdin` usando `-i -`.

#### Ejemplo con archivo (pipe)

``` bash
cat examples/resume.example.json | profilectl convert -i -
```

#### Ejemplo mínimo (recomendado)

Uso de `printf` para evitar problemas de formato:

``` bash
printf '%s' '{}' | profilectl convert -i -
```

#### Ejemplo mínimo con `echo` (simple, pero menos robusto que `printf`)

``` bash
echo '{}' | profilectl convert -i -
```

#### Ejemplo inline más completo

``` bash
printf '%s' '{
  "basics": {
    "name": "Jane Doe",
    "label": "Senior Backend Developer"
  }
}' | profilectl convert -i -
```


------------------------------------------------------------------------

## Arquitectura

Ver [`docs/architecture.md`](docs/architecture.md)

Flujo de alto nivel:

    Input (JSON Resume)
       ↓
    Validación
       ↓
    Transformación
       ↓
    Output (RenderCV YAML)

------------------------------------------------------------------------

## Documentación

-   Arquitectura: `docs/architecture.md`
-   Decisiones: `docs/decisions/`
-   Flujo principal: `docs/workflows/golden-path.md`
-   Runbook local: `docs/runbooks/local-development.md`

------------------------------------------------------------------------

## Estructura del proyecto

    src/profilecli/    CLI y lógica principal
    schemas/           Schemas JSON Resume / RenderCV
    tests/             Suite de tests con pytest
    docs/              Arquitectura, decisiones y workflows
    examples/          Ejemplos de entrada