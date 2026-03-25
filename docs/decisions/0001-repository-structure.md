# 0001 - Estructura documental base del repositorio

- Estado: aceptada
- Fecha: 2026-03-25

## Contexto

Se necesita una estructura documental minima, estable y facil de consumir por personas y agentes.

## Decision

Se adopta la siguiente estructura base en `docs/`:

```text
docs/
├─ architecture.md
├─ decisions/
│  └─ 0001-repository-structure.md
├─ runbooks/
│  └─ local-development.md
└─ workflows/
   └─ golden-path.md
```

## Consecuencias

- La documentacion se mantiene pequena y operativa.
- Nuevas decisiones se agregan como ADR numeradas en `docs/decisions/`.
- `README.md` y `AGENTS.md` deben apuntar solo a rutas existentes.
