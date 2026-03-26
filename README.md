# profile-engine

![Python](https://img.shields.io/badge/python-3.12+-blue)
![Tests](https://img.shields.io/badge/tests-pytest-green)
![Status](https://img.shields.io/badge/status-active--development-orange)

`profile-engine` es un pipeline backend pequeño y determinista para validar y transformar datos de perfil estructurados.

La interfaz pública es `profilectl`: valida contratos JSON Resume y genera YAML compatible con RenderCV mediante `convert`.

## Por qué existe

La mayoría de herramientas de CV optimizan la presentación. Este proyecto optimiza fiabilidad operativa:

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
- entrada por archivo o `stdin`; salida por `stdout` o fichero
- ejecución estable en local, scripts y CI

## Alcance

Resuelve un problema acotado: convertir de forma confiable un contrato JSON conocido a un formato de salida concreto.

No intenta cubrir, por ahora, edición visual, múltiples targets de exportación, versionado de perfiles ni orquestación distribuida.

## Uso real

Ejemplos representativos de uso en local y en pipelines:

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

## Arquitectura

`docs/architecture.md`

## Documentación relacionada

- `docs/architecture.md`
- `docs/workflows/golden-path.md`
- `docs/decisions/`
