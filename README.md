# profile-engine

![Python](https://img.shields.io/badge/python-3.12+-blue)
![Tests](https://img.shields.io/badge/tests-pytest-green)
![Status](https://img.shields.io/badge/status-active--development-orange)

`profile-engine` es un repositorio backend para validar y transformar perfiles profesionales basados en JSON Resume.

La CLI actual se mantiene como `cvtool` por compatibilidad.

## Alcance actual

- Validacion de JSON Resume contra schema.
- Export a YAML compatible con RenderCV.
- Comportamiento determinista en errores y codigos de salida.
- Suite automatizada con pytest.

## Uso rapido

Instalacion local en modo editable:

```bash
pip install -e .
```

Validar un CV:

```bash
cvtool validate --in resume.example.json
```

Exportar a RenderCV YAML:

```bash
cvtool export resume.example.json -o out.yaml
```

## Desarrollo

Ejecutar tests:

```bash
pytest
```

## Documentacion

- Arquitectura: `docs/architecture.md`
- Decisiones: `docs/decisions/`
- Flujo principal: `docs/workflows/golden-path.md`
- Runbook local: `docs/runbooks/local-development.md`

## Estructura base

```text
src/profilecli/    CLI y logica principal
schemas/           Schemas JSON Resume/RenderCV
tests/             Suite pytest
docs/              Arquitectura, decisiones, runbooks y workflows
examples/          Archivos de ejemplo
```
