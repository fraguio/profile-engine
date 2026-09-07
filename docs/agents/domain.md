# Documentación de dominio

Cómo deben consultar las skills de ingeniería la documentación de dominio de este repositorio cuando exploren el código.

## Lecturas previas a la exploración

- **`CONTEXT.md`** en la raíz del repositorio.
- **`docs/adr/`**: lee los ADR relacionados con el área en la que vas a trabajar.

Si alguno de estos archivos no existe, **continúa sin indicarlo**. No señales su ausencia ni sugieras crearlo de antemano. La skill `/domain-modeling`, accesible mediante `/grill-with-docs` y `/improve-codebase-architecture`, los crea cuando realmente se resuelven términos o decisiones.

## Estructura de archivos

Este es un repositorio de contexto único:

```
/
|-- CONTEXT.md
|-- docs/adr/
|   |-- 0001-event-sourced-orders.md
|   `-- 0002-postgres-for-write-model.md
`-- src/
```

## Uso del vocabulario del glosario

Cuando nombres un concepto de dominio, ya sea en el título de un issue, una propuesta de refactorización, una hipótesis o el nombre de un test, utiliza el término definido en `CONTEXT.md`. No emplees sinónimos que el glosario evite explícitamente.

Si el concepto que necesitas todavía no aparece en el glosario, considéralo una señal: quizá estás inventando terminología que el proyecto no utiliza, en cuyo caso debes reconsiderarla, o existe una carencia real que debes anotar para `/domain-modeling`.

## Conflictos con ADR

Si tu resultado contradice un ADR existente, indícalo explícitamente en lugar de sustituirlo de forma silenciosa:

> _Contradice ADR-0007 (pedidos basados en eventos), pero merece la pena reabrirlo porque..._
