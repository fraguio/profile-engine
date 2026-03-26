# 0002 - Uso de schemas versionados locales para validación

## Estado
Aceptado

## Contexto

El proyecto `profile-engine` valida datos de entrada (JSON Resume) y salida (RenderCV) utilizando JSON Schema.

Una alternativa considerada es validar dinámicamente contra schemas remotos (por ejemplo, la última versión publicada upstream).

## Decisión

Se utilizarán schemas versionados y almacenados localmente dentro del repositorio.

No se realizará validación en tiempo de ejecución contra versiones remotas de los schemas.

## Motivación

### Determinismo

El objetivo del proyecto es ser un pipeline determinista. Validar contra schemas remotos introduce variabilidad en función del estado externo.

### Reproducibilidad

El mismo input debe producir siempre el mismo resultado. Dependencias externas rompen esta garantía.

### Fiabilidad operativa

La validación no debe depender de red, disponibilidad de terceros o cambios no controlados.

### Control del cambio

Las actualizaciones de schema deben ser explícitas, revisadas y versionadas mediante commits.

## Consecuencias

### Positivas

- Comportamiento estable y predecible
- Ejecución offline
- Trazabilidad de cambios en schemas
- Mayor control sobre compatibilidad

### Negativas

- Requiere mantenimiento manual de schemas
- Posible desfase respecto a upstream si no se actualiza periódicamente

## Estrategia de actualización

- Monitorizar cambios en los repositorios upstream
- Actualizar schemas de forma manual y controlada
- Validar impacto antes de integrar cambios
- Registrar la actualización en commits y documentación

## Alternativas consideradas

### Validación contra schemas remotos (rechazada)

Ventajas:
- Siempre alineado con última versión

Inconvenientes:
- Rompe determinismo
- Introduce dependencia de red
- Puede provocar fallos inesperados
- Reduce control sobre el sistema

## Conclusión

Se prioriza estabilidad, control y reproducibilidad frente a actualización automática.
