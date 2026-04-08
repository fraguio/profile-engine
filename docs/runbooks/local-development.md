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
profilectl validate --input examples/resume.example.json
profilectl convert examples/resume.example.json -o out.yaml
rendercv render out.yaml --html-path output/index.html --dont-generate-pdf --dont-generate-png --dont-generate-typst
```

Sin instalacion editable (alternativa):

```bash
PYTHONPATH=src python -m profilecli validate --input examples/resume.example.json
PYTHONPATH=src python -m profilecli convert examples/resume.example.json -o out.yaml
rendercv render out.yaml --html-path output/index.html --dont-generate-pdf --dont-generate-png --dont-generate-typst
```

```powershell
$env:PYTHONPATH = "src"
python -m profilecli validate --input examples/resume.example.json
python -m profilecli convert examples/resume.example.json -o out.yaml
rendercv render out.yaml --html-path output/index.html --dont-generate-pdf --dont-generate-png --dont-generate-typst
```

## Flujo local rapido

```bash
PYTHONPATH=src python -m profilecli validate --input examples/resume.example.json
PYTHONPATH=src python -m profilecli convert examples/resume.example.json -o out.yaml
rendercv render out.yaml --html-path output/index.html --dont-generate-pdf --dont-generate-png --dont-generate-typst
pytest
```

Flujo de una sola orden:

```bash
make html IN="../profile-data/data/resume.json" OUT="output/rendercv_CV.yaml" HTML_OUT="output/index.html"
```

```bash
profilectl html --input "../profile-data/data/resume.json" --output "output/rendercv_CV.yaml" --html-output "output/index.html"
```

## Notas

- `out.yaml` es un artefacto local y no debe versionarse.
- Los tests no requieren `pip install -e .`; los subprocess de tests inyectan `PYTHONPATH` hacia `src`.
- Mantener cambios pequenos y verificar tests cuando cambie comportamiento.
