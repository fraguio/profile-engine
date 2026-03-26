# Runbook: desarrollo local

## Requisitos

- Python 3.12+
- Entorno virtual recomendado

## Setup

Opcion recomendada para desarrollo (editable):

```bash
python -m venv .venv
. .venv/Scripts/activate
pip install -e .[dev]
```

Alternativa sin instalacion editable:

```bash
python -m venv .venv
. .venv/Scripts/activate
pip install .[dev]
```

## Ejecutar CLI localmente

Con instalacion editable (recomendado):

```bash
profilectl validate --in examples/resume.example.json
profilectl convert examples/resume.example.json -o out.yaml
```

Sin instalacion editable (alternativa):

```bash
PYTHONPATH=src python -m profilecli validate --in examples/resume.example.json
PYTHONPATH=src python -m profilecli convert examples/resume.example.json -o out.yaml
```

```powershell
$env:PYTHONPATH = "src"
python -m profilecli validate --in examples/resume.example.json
python -m profilecli convert examples/resume.example.json -o out.yaml
```

## Flujo local rapido

```bash
PYTHONPATH=src python -m profilecli validate --in examples/resume.example.json
PYTHONPATH=src python -m profilecli convert examples/resume.example.json -o out.yaml
pytest
```

## Notas

- `out.yaml` es un artefacto local y no debe versionarse.
- Los tests no requieren `pip install -e .`; los subprocess de tests inyectan `PYTHONPATH` hacia `src`.
- Mantener cambios pequenos y verificar tests cuando cambie comportamiento.
