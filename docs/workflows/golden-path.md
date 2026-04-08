# Golden Path

## Flujo esperado del dato

El flujo operativo de `profile-engine` es lineal y determinista:

1. Ingesta de JSON Resume desde archivo o `stdin`.
2. Validación de contrato de entrada.
3. Transformación a estructura RenderCV.
4. Emisión de YAML por `stdout` o fichero.
5. Render de HTML publicable con RenderCV.

La ruta principal es `convert`; `validate` permite validar de forma aislada cuando se necesita cortar antes del mapeo.

## Ejecución operativa

```bash
profilectl validate examples/resume.example.json
```

```bash
profilectl convert examples/resume.example.json
```

```bash
profilectl convert examples/resume.example.json -o out.yaml
```

```bash
rendercv render out.yaml --html-path output/index.html --dont-generate-pdf --dont-generate-png --dont-generate-typst
```

```bash
make html IN="../profile-data/data/resume.json" OUT="output/rendercv_CV.yaml" HTML_OUT="output/index.html"
```

```bash
profilectl html --input "../profile-data/data/resume.json" --output "output/rendercv_CV.yaml" --html-output "output/index.html"
```

```bash
cat examples/resume.example.json | profilectl convert -i -
```

## Uso en automatización

El diseño de CLI permite encadenar el pipeline en scripts y CI sin adaptadores extra:

- lectura por `stdin` para composición
- salida por `stdout` para piping
- códigos de salida estables para control de errores
- comportamiento determinista para pruebas repetibles

## Garantías del sistema

- `profilectl` mantiene compatibilidad de comandos y banderas existentes.
- Para una misma entrada, validación y conversión producen resultados estables.
- El repositorio no incorpora artefactos fuera de alcance.
