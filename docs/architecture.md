# Arquitectura

## Principios de diseño

- Contrato primero: el schema define la frontera de entrada.
- Determinismo operativo: misma entrada, misma salida, mismos códigos de error.
- Separación por capas: CLI para orquestación, módulos para lógica.
- Superficie pequeña: una ruta principal (`convert`) y comportamiento estable.
- Evolución controlada: cambios mínimos que preservan compatibilidad de `profilectl`.

## Visión del sistema

Flujo único y explícito:

`JSON Resume -> validate -> convert -> RenderCV YAML`

El sistema asume entrada estructurada, valida temprano y transforma solo datos válidos. La CLI no contiene lógica de mapeo; coordina lectura/escritura, códigos de salida y manejo de errores.

`profile-engine` se define como consumer del contrato JSON Resume y no establece dependencias con otros consumers.

## Componentes

- Capa de interfaz (CLI): `src/profilecli/cli.py`
- Capa de validación: `src/profilecli/validate.py`
- Capa de transformación: `src/profilecli/convert_rendercv.py`
- `schemas/`: definición de contratos usados por validación y conversión
- `tests/`: pruebas de CLI y comportamiento determinista

## Decisiones técnicas

### 1) Entrada y salida por CLI estándar

**Decisión técnica**
`profilectl convert` acepta archivo o `stdin` y escribe en `stdout` por defecto o en fichero con `-o`.

**Motivo**
Facilitar composición en scripts, integración en CI y uso local sin APIs adicionales.

**Trade-off**
No se expone una interfaz de servicio remota ni capacidades interactivas avanzadas.

### 2) Validación estricta antes de transformar

**Decisión técnica**
Separar `validate` y ejecutar validación antes de cualquier conversión.

**Motivo**
Fallar pronto reduce estados intermedios ambiguos y hace trazable el origen del error.

**Trade-off**
Menor tolerancia a entradas incompletas: se prioriza consistencia.

### 3) Un único formato de salida operativo

**Decisión técnica**
`convert` soporta `rendercv` como formato de salida.

**Motivo**
Reducir complejidad y estabilizar el contrato de salida.

**Trade-off**
Extensibilidad limitada sin cambios explícitos.

### 4) Determinismo como restricción de diseño

**Decisión técnica**
Mensajes de error, códigos de salida y serialización son estables para la misma entrada.

**Motivo**
Permitir tests reproducibles y automatización fiable.

**Trade-off**
Cambios en UX requieren mayor cuidado para evitar romper compatibilidad.
