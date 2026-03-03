# cvtool

CLI profesional para validar y transformar CVs basados en JSON Resume
hacia formatos compatibles con RenderCV.

Proyecto orientado a demostrar diseño backend limpio, validación robusta
y arquitectura mantenible en Python.

------------------------------------------------------------------------

## 🧠 El problema

Mantener múltiples versiones de un currículum suele implicar:

-   Errores manuales\
-   Inconsistencias entre formatos\
-   Dificultad para versionar\
-   Falta de validación estructural

JSON Resume ofrece un estándar estructurado, pero:

-   No siempre se valida correctamente\
-   No está preparado para flujos automatizados\
-   No integra fácilmente transformaciones hacia otros formatos modernos

`cvtool` nace como una herramienta CLI profesional para:

> Validar, transformar y preparar CVs como artefactos versionables,
> reproducibles y automatizables.

------------------------------------------------------------------------

## 🎯 Objetivo del proyecto

Este proyecto no es un generador de CV más.

Está diseñado para demostrar:

-   Diseño modular en Python\
-   Separación clara entre CLI y lógica de negocio\
-   Validación estricta mediante JSON Schema (Draft 7)\
-   Uso de `FormatChecker`\
-   Orden determinista de errores\
-   Manejo explícito de códigos de salida\
-   Testing automatizado con pytest

Refleja prácticas habituales en entornos enterprise:

-   Validaciones explícitas\
-   Contratos formales (schema)\
-   Trazabilidad de errores\
-   Tests reproducibles

------------------------------------------------------------------------

## 🛠️ Instalación

    git clone https://github.com/fraguio/cvtool.git
    cd cvtool
    pip install -e .

Requiere Python 3.10 o superior.

------------------------------------------------------------------------

## 🚀 Uso

### Validar un CV

    cvtool validate resume.json

Salida exitosa:

    ✔ Resume is valid

En caso de error:

-   Se muestra la ruta exacta del campo (ej: `work[0].startDate`)\
-   Mensaje claro y estable\
-   Exit code coherente

### Exportar a RenderCV

    cvtool export-rendercv resume.json output.yaml

Genera un YAML compatible con RenderCV.

------------------------------------------------------------------------

## 🧪 Testing

Proyecto cubierto con pytest.

    pytest

Incluye pruebas para:

-   JSON válido\
-   JSON mal formado\
-   Archivo inexistente\
-   Violación de schema\
-   Conversión correcta a RenderCV\
-   Códigos de salida esperados

Estado actual:

    21 tests passing

------------------------------------------------------------------------

## 📦 Arquitectura

Estructura del proyecto:

    src/
     └── cvtool/
          ├── __main__.py
          ├── validate.py
          ├── convert_rendercv.py
    schemas/
     └── jsonresume.schema.json
    tests/

### Principios aplicados

-   Separación clara de responsabilidades\
-   Validación desacoplada de la CLI\
-   Conversores independientes\
-   Tests por módulo\
-   Orden determinista de errores\
-   Diseño preparado para extensiones futuras

------------------------------------------------------------------------

## 🚀 Roadmap

### Fase 1 (actual)

-   ✔ Validación JSON Resume\
-   ✔ Export RenderCV\
-   ✔ Testing base completo\
-   ✔ Manejo robusto de errores

### Fase 2

-   Soporte para múltiples templates\
-   Export a Markdown\
-   Integración CI (GitHub Actions)\
-   Mejora de cobertura de tests

### Fase 3

-   Publicación como paquete pip\
-   Validación incremental\
-   Hooks pre-commit\
-   Extensión a otros formatos de exportación

------------------------------------------------------------------------

## 👤 Contexto profesional

Proyecto desarrollado como parte de una actualización estratégica hacia
backend moderno en Python, con foco en:

-   Calidad de código\
-   Automatización\
-   Diseño mantenible\
-   Mentalidad enterprise\
-   Preparación para entornos corporativos exigentes

------------------------------------------------------------------------

## 📌 Estado

Proyecto funcional y testeado.\
Actualmente en fase de consolidación técnica antes de ampliar
funcionalidades.
