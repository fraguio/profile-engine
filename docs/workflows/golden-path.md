# Golden Path

## Objetivo

Definir el flujo minimo para cambios seguros en `profile-engine`.

## Pasos

1. Leer `README.md`, `docs/architecture.md` y decisiones en `docs/decisions/`.
2. Limitar el alcance a cambios pequenos y focalizados.
3. Implementar solo en archivos necesarios.
4. Ejecutar `pytest` si cambia comportamiento o salida.
5. Mantener tests autosuficientes: no depender de `pip install -e .`; en subprocess resolver `src` via `PYTHONPATH`.
6. Entregar resumen, diff por archivo y commit sugerido.

## Criterios de salida

- CLI `profilectl` compatible.
- Salidas deterministas conservadas.
- Sin artefactos locales en el diff.
