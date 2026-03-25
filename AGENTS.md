# AGENTS.md

Guia operativa para agentes en `profile-engine`.

## Prioridades

1. Cambios minimos y focalizados.
2. No romper compatibilidad de la CLI `cvtool`.
3. No refactorizar logica Python sin necesidad directa.
4. Mantener salidas deterministas y tests estables.

## Referencias obligatorias

- Arquitectura: `docs/architecture.md`
- Flujo de trabajo: `docs/workflows/golden-path.md`
- Decisiones de diseño: `docs/decisions/`

## Forma de trabajo

- Leer contexto antes de editar.
- Tocar solo archivos necesarios para la tarea.
- Ejecutar `pytest` cuando haya cambios de comportamiento.
- Entregar resumen de cambios y mensaje de commit sugerido.
