# Arquitectura

## Objetivo

`profile-engine` centraliza validacion y transformacion de perfiles profesionales usando JSON Resume como formato de entrada.

## Componentes

- `src/profilecli/cli.py`: interfaz CLI (`profilectl`) y manejo de codigos de salida.
- `src/profilecli/validate.py`: validacion de payloads JSON Resume contra schema.
- `src/profilecli/convert_rendercv.py`: mapeo y conversion a formato RenderCV.
- `schemas/`: contratos JSON Schema usados por validacion y conversion.
- `tests/`: pruebas funcionales y de regresion de la CLI y modulos.

## Principios

- Compatibilidad de CLI primero (`profilectl` no cambia).
- Cambios pequenos y reversibles.
- Salidas deterministas para facilitar testing.
- Separacion entre capa CLI y logica de dominio.
