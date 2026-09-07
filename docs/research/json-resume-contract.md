# Contrato vigente de JSON Resume

Fecha de corte: 2026-09-07.

## Pregunta

¿Cuál es el contrato oficial vigente de JSON Resume —schema, versión,
extensiones, evolución y mecanismos de validación— que debe conocerse antes de
definir el contrato de entrada de Profile Engine?

## Respuesta breve

El contrato publicado vigente es `schema.json` de
[`@jsonresume/schema@1.3.1`](https://registry.npmjs.org/@jsonresume%2Fschema/1.3.1),
publicado el 2026-07-22 y fijado por la
[release `@jsonresume/schema@1.3.1`](https://github.com/jsonresume/jsonresume.org/releases/tag/%40jsonresume/schema%401.3.1)
al commit
[`8e4947d2030db8bba22d2b897461dc5587ee7125`](https://github.com/jsonresume/jsonresume.org/commit/8e4947d2030db8bba22d2b897461dc5587ee7125).
Es un JSON Schema Draft-07 permisivo: todos los campos son opcionales, todos
los objetos admiten propiedades adicionales y las restricciones se concentran
en tipos, formatos `email`/`uri` y un patrón de fecha parcial. La versión no se
puede deducir de forma fiable desde una instancia: se identifica sin ambigüedad
por la versión del paquete, su tag/commit o la integridad del artefacto.

## Alcance y jerarquía de fuentes

La documentación del propio paquete declara que el schema estable está
representado por `schema.json` y `sample.resume.json` ([README fijado,
líneas 11-16](https://github.com/jsonresume/jsonresume.org/blob/8e4947d2030db8bba22d2b897461dc5587ee7125/packages/schema/README.md#L11-L16)).
Por ello, este informe toma como contrato el `schema.json` contenido en el
paquete publicado, no implementaciones parecidas mantenidas por otras partes
del monorepo.

Las afirmaciones se clasifican así:

| Clase | Uso en este informe | Estabilidad |
| --- | --- | --- |
| Artefacto npm `@jsonresume/schema@1.3.1` | Versión y distribución publicadas, `sha512-S9zH1vmS67b1Ld6p9A+sHiZgqZox4lWTVHtca3VarRVkRtp3C/EMQ2bSNlO39+o+0OZbrY+Srnn7Q8uJOtxZhQ==` | Contenido versionado; [entrada de registro por versión](https://registry.npmjs.org/@jsonresume%2Fschema/1.3.1) |
| Tag/release `@jsonresume/schema@1.3.1` | Fuente correspondiente a la publicación | Versionado; [release](https://github.com/jsonresume/jsonresume.org/releases/tag/%40jsonresume/schema%401.3.1) y [schema en el commit](https://github.com/jsonresume/jsonresume.org/blob/8e4947d2030db8bba22d2b897461dc5587ee7125/packages/schema/schema.json) |
| `master`, `latest` y webs desplegadas | Comprobación de vigencia y documentación propia | Mutables; observados en la fecha de corte y, cuando es posible, acompañados de un snapshot por commit |
| JSON Schema Draft-07 y SemVer 2.0.0 | Semántica de los estándares invocados por JSON Resume | Especificaciones versionadas: [core Draft-07](https://json-schema.org/draft-07/draft-handrews-json-schema-01), [validación Draft-07](https://json-schema.org/draft-07/draft-handrews-json-schema-validation-01) y [SemVer 2.0.0](https://semver.org/spec/v2.0.0.html) |

## Schema y versión vigentes

- El paquete oficial es `@jsonresume/schema`; la versión publicada con el tag
  `latest` era `1.3.1` en el registro npm en la fecha de corte
  ([packument mutable](https://registry.npmjs.org/@jsonresume%2Fschema)). La
  entrada versionada registra además Node.js `>=20`, `validator.js` como
  entrada y `jsonschema@^1.4.1` como dependencia
  ([registro de `1.3.1`](https://registry.npmjs.org/@jsonresume%2Fschema/1.3.1)).
- El [`package.json` fijado](https://github.com/jsonresume/jsonresume.org/blob/8e4947d2030db8bba22d2b897461dc5587ee7125/packages/schema/package.json#L1-L42)
  declara nombre `@jsonresume/schema`, versión `1.3.1` e incluye
  `schema.json` en la distribución.
- El `schema.json` extraído del
  [tarball publicado](https://registry.npmjs.org/@jsonresume/schema/-/schema-1.3.1.tgz)
  y el del commit de la release tienen el mismo SHA-256:
  `a07eedd3d86ac5bb61d72e136d788269e35baf42c35391e15d0be39b3dc5a4bd`.
- La release apunta a `8e4947d...`; el tag anotado se resuelve a ese mismo
  commit. No había una release posterior de `@jsonresume/schema` en la fecha
  de corte.
- El snapshot de `master` observado en la fecha de corte era
  [`51e63a4f4e51bee7695fc88c8b79a9e1b7eba6f2`](https://github.com/jsonresume/jsonresume.org/commit/51e63a4f4e51bee7695fc88c8b79a9e1b7eba6f2).
  Su `packages/schema/schema.json` tenía el mismo blob Git
  `f2264619b89837268a3f38fe43ac5554b590e0f9` que la release `1.3.1`
  ([contenido en la release](https://api.github.com/repos/jsonresume/jsonresume.org/contents/packages/schema/schema.json?ref=8e4947d2030db8bba22d2b897461dc5587ee7125),
  [contenido en el snapshot de `master`](https://api.github.com/repos/jsonresume/jsonresume.org/contents/packages/schema/schema.json?ref=51e63a4f4e51bee7695fc88c8b79a9e1b7eba6f2)).
  Esto solo constata igualdad en esa fecha; `master` sigue siendo mutable.
- El paquete anterior `resume-schema@1.0.1` permanece publicado, pero su propia
  metadata lo marca como obsoleto y remite a `@jsonresume/schema` como contrato
  vigente ([registro versionado del paquete legado](https://registry.npmjs.org/resume-schema/1.0.1)).

`job-schema.json` se distribuye en el mismo paquete, pero el README lo presenta
como un borrador de descripción de puestos, no como parte del contrato estable
de un resume ([README fijado,
líneas 72-80](https://github.com/jsonresume/jsonresume.org/blob/8e4947d2030db8bba22d2b897461dc5587ee7125/packages/schema/README.md#L72-L80)).

## Identificación y versionado dentro del JSON

Hay tres conceptos distintos y no están enlazados de forma normativa:

1. El `$schema` del propio `schema.json` vale
   `http://json-schema.org/draft-07/schema#`: identifica el dialecto JSON
   Schema, no la versión de JSON Resume. Su `$id` es el placeholder
   `http://example.com/example.json`, sin nombre ni versión de JSON Resume
   ([schema, líneas 1-10](https://github.com/jsonresume/jsonresume.org/blob/8e4947d2030db8bba22d2b897461dc5587ee7125/packages/schema/schema.json#L1-L10)).
2. Una instancia puede contener una propiedad raíz `$schema`, pero es opcional
   y su única restricción es ser un `string` con formato `uri`; no hay `const`
   ni una lista de versiones admitidas ([schema, líneas
   12-17](https://github.com/jsonresume/jsonresume.org/blob/8e4947d2030db8bba22d2b897461dc5587ee7125/packages/schema/schema.json#L12-L17)).
3. `meta.version` también es opcional y solo se valida como `string`, aunque su
   descripción diga que sigue SemVer. `meta.lastModified` solo se valida como
   `string`, pese a describirse como ISO 8601; `meta.canonical` sí exige
   formato `uri` ([schema, líneas
   456-475](https://github.com/jsonresume/jsonresume.org/blob/8e4947d2030db8bba22d2b897461dc5587ee7125/packages/schema/schema.json#L456-L475)).

El ejemplo distribuido en `1.3.1` evidencia la ambigüedad: su `$schema`, su
`meta.canonical` y su `meta.version` siguen apuntando a `v1.0.0` del repositorio
anterior ([ejemplo fijado, líneas
1-3](https://github.com/jsonresume/jsonresume.org/blob/8e4947d2030db8bba22d2b897461dc5587ee7125/packages/schema/sample.resume.json#L1-L3)
y [136-140](https://github.com/jsonresume/jsonresume.org/blob/8e4947d2030db8bba22d2b897461dc5587ee7125/packages/schema/sample.resume.json#L136-L140)).
Por tanto, ni `$schema` ni `meta.version` prueban que una instancia se validó
contra `@jsonresume/schema@1.3.1`. La identidad reproducible disponible hoy es
externa al documento: nombre y versión exacta de paquete, integridad npm y/o
commit del schema.

## Dialecto y vocabulario JSON Schema

El contrato declara JSON Schema Draft-07 y la release `1.3.1` añadió pruebas
que lo validan contra el meta-schema Draft-07 y lo compilan con Ajv 8 tanto en
modo permisivo como estricto ([pruebas fijadas, líneas
12-63](https://github.com/jsonresume/jsonresume.org/blob/8e4947d2030db8bba22d2b897461dc5587ee7125/packages/schema/test/compliance.spec.js#L12-L63)).

El schema usa:

- keywords core: `$schema`, `$id`, `$ref` y `definitions`;
- assertions/aplicadores: `type`, `properties`, `additionalProperties`,
  `items`, `pattern` y `format`;
- anotaciones: `title` y `description`.

`definitions`, no `$defs`, es la keyword correcta en Draft-07. Este dialecto
describe vocabularios mediante el meta-schema; no dispone de la keyword
`$vocabulary` introducida en dialectos posteriores. Las referencias son solo
locales y reutilizan `#/definitions/iso8601`, por lo que validar el resume no
requiere resolver schemas externos.

Draft-07 permite que `format` funcione solo como anotación: que `email` y `uri`
sean assertions depende del validador y de su configuración ([sección 7.2 de
la especificación de validación](https://json-schema.org/draft-07/draft-handrews-json-schema-validation-01#rfc.section.7.2)).
La configuración de referencia del ecosistema sí activa formatos con
`ajv-formats`.

## Forma del documento

La raíz debe ser un objeto. Esta tabla transcribe los campos conocidos por
`schema.json`; salvo indicación, cada campo hoja es `string` y todos los campos
y secciones son opcionales.

| Propiedad raíz | Tipo | Propiedades conocidas de sus elementos |
| --- | --- | --- |
| `$schema` | `string`, formato `uri` | Enlace declarado por la instancia |
| `basics` | objeto | `name`, `label`, `image`, `email` (`email`), `phone`, `url` (`uri`), `summary`, `location`, `profiles` |
| `basics.location` | objeto | `address`, `postalCode`, `city`, `countryCode`, `region` |
| `basics.profiles` | array de objetos | `network`, `username`, `url` (`uri`) |
| `work` | array de objetos | `name`, `location`, `description`, `position`, `url` (`uri`), `startDate`, `endDate`, `summary`, `highlights` (array de strings) |
| `volunteer` | array de objetos | `organization`, `position`, `url` (`uri`), `startDate`, `endDate`, `summary`, `highlights` (array de strings) |
| `education` | array de objetos | `institution`, `url` (`uri`), `area`, `studyType`, `startDate`, `endDate`, `score`, `courses` (array de strings) |
| `awards` | array de objetos | `title`, `date`, `awarder`, `summary` |
| `certificates` | array de objetos | `name`, `date`, `url` (`uri`), `issuer` |
| `publications` | array de objetos | `name`, `publisher`, `releaseDate`, `url` (`uri`), `summary` |
| `skills` | array de objetos | `name`, `level`, `keywords` (array de strings) |
| `languages` | array de objetos | `language`, `fluency` |
| `interests` | array de objetos | `name`, `keywords` (array de strings) |
| `references` | array de objetos | `name`, `reference` |
| `projects` | array de objetos | `name`, `description`, `highlights` y `keywords` (arrays de strings), `startDate`, `endDate`, `url` (`uri`), `roles` (array de strings), `entity`, `type` |
| `meta` | objeto | `canonical` (`uri`), `version`, `lastModified` |

Las definiciones completas están agrupadas en el schema fijado: [`basics`,
líneas 18-99](https://github.com/jsonresume/jsonresume.org/blob/8e4947d2030db8bba22d2b897461dc5587ee7125/packages/schema/schema.json#L18-L99),
[`work` a `education`, líneas
100-231](https://github.com/jsonresume/jsonresume.org/blob/8e4947d2030db8bba22d2b897461dc5587ee7125/packages/schema/schema.json#L100-L231),
[`awards` a `languages`, líneas
232-356](https://github.com/jsonresume/jsonresume.org/blob/8e4947d2030db8bba22d2b897461dc5587ee7125/packages/schema/schema.json#L232-L356) y
[`interests` a `meta`, líneas
357-475](https://github.com/jsonresume/jsonresume.org/blob/8e4947d2030db8bba22d2b897461dc5587ee7125/packages/schema/schema.json#L357-L475).

### Restricciones efectivas

- No aparece `required` en ningún nivel. Conforme a Draft-07, omitirlo equivale
  a una lista vacía; por ello `{}`, cada sección vacía y cada elemento de array
  vacío son válidos ([semántica de `required`](https://json-schema.org/draft-07/draft-handrews-json-schema-validation-01#rfc.section.6.5.3)).
- No hay `minItems`, `minLength`, `uniqueItems`, `enum`, dependencias ni
  restricciones entre campos. Arrays y strings vacíos son válidos salvo cuando
  un `format` o el patrón de fecha activo diga lo contrario.
- Un campo conocido presente debe respetar su tipo. `null` no es una alternativa
  admitida para ninguno: la ausencia es válida, pero `null` no sustituye a un
  objeto, array o string.
- `email` y los campos señalados como `uri` dependen de que el validador afirme
  `format`. `image` solo es `string`; `countryCode`, `phone`, `meta.version` y
  `meta.lastModified` solo tienen descripciones, que no son assertions.
- `startDate`, `endDate`, `date` y `releaseDate` reutilizan el patrón
  `^([1-2][0-9]{3}-[0-1][0-9]-[0-3][0-9]|[1-2][0-9]{3}-[0-1][0-9]|[1-2][0-9]{3})$`.
  Acepta las formas `YYYY`, `YYYY-MM` y `YYYY-MM-DD`, con años 1000-2999, pero
  no comprueba calendarios reales: también admite meses `00`/`19` y días
  `00`/`39`. No admite `null`, string vacío, timestamps ni textos como
  `Present` ([definición, líneas
  5-10](https://github.com/jsonresume/jsonresume.org/blob/8e4947d2030db8bba22d2b897461dc5587ee7125/packages/schema/schema.json#L5-L10)).

## Extensibilidad

El contrato establece `additionalProperties: true` en la raíz y en todos los
objetos que define: `basics`, `location`, elementos de `profiles` y de cada
sección, y `meta` ([schema completo fijado](https://github.com/jsonresume/jsonresume.org/blob/8e4947d2030db8bba22d2b897461dc5587ee7125/packages/schema/schema.json)).
Una propiedad desconocida puede, por tanto, aparecer en cualquiera de esos
objetos y tener cualquier valor JSON sin invalidar el documento.

No existe en el schema un prefijo, namespace, contenedor o registro para
extensiones; tampoco hay `patternProperties`. La apertura es el único
mecanismo contractual. Esto no relaja campos conocidos: por ejemplo, una
extensión raíz es válida, pero `work` sigue teniendo que ser un array y cada
elemento de `work`, un objeto.

La extensibilidad de una instancia no debe confundirse con extender el propio
JSON Schema. Draft-07 permite keywords desconocidas en un schema, pero exige
acuerdo entre implementaciones para que tengan comportamiento; JSON Resume no
define vocabularios adicionales ([core Draft-07, secciones 4.3.1 y
6.4](https://json-schema.org/draft-07/draft-handrews-json-schema-01#rfc.section.4.3.1)).

## Evolución oficial

- El README declara SemVer 2.0.0: una incompatibilidad de API solo debe entrar
  en una major y una minor o patch que rompa compatibilidad debe retirarse o
  corregirse inmediatamente ([README fijado, líneas
  57-70](https://github.com/jsonresume/jsonresume.org/blob/8e4947d2030db8bba22d2b897461dc5587ee7125/packages/schema/README.md#L57-L70)).
- Desde la migración al monorepo, las publicaciones se gestionan con Changesets:
  cada cambio declara paquete y nivel SemVer; una PR de versiones actualiza
  versiones/changelogs y el workflow publica después en npm ([procedimiento
  fijado, líneas 1-9](https://github.com/jsonresume/jsonresume.org/blob/8e4947d2030db8bba22d2b897461dc5587ee7125/docs/RELEASING.md#L1-L9)).
- La serie con el nombre actual se publicó en npm como `1.0.1`, `1.1.0`,
  `1.1.1`, `1.1.2`, `1.2.0`, `1.2.1`, `1.3.0` y `1.3.1`
  ([historial mutable del registro, consultado en la fecha de
  corte](https://registry.npmjs.org/@jsonresume%2Fschema)).
- `1.1.0` (2024-07-10) cambió, entre otros aspectos, la fecha de certificados al
  tipo de fecha parcial, la librería de validación y el namespace del paquete
  ([release histórica fijada](https://github.com/jsonresume/resume-schema/releases/tag/v1.1.0)).
  `1.2.1` solo registró espaciado del schema
  ([release](https://github.com/jsonresume/resume-schema/releases/tag/v1.2.1)).
- `1.3.0` añadió tres ejemplos sin cambiar `schema.json`
  ([release](https://github.com/jsonresume/jsonresume.org/releases/tag/%40jsonresume/schema%401.3.0)).
  `1.3.1` retiró usos inefectivos de `additionalItems`, hizo explícita la
  conformidad Draft-07 y declaró no cambiar resultados de validación
  ([release](https://github.com/jsonresume/jsonresume.org/releases/tag/%40jsonresume/schema%401.3.1)).

SemVer expresa la intención de compatibilidad del proyecto, pero la versión del
paquete abarca conjuntamente el schema, el validador, ejemplos y
`job-schema.json`: una subida de versión no implica necesariamente un cambio en
el contrato de resume. El changelog y el diff de cada release son necesarios
para distinguirlos.

## Mecanismos de validación disponibles

### Paquete oficial

`@jsonresume/schema@1.3.1` exporta:

- `schema`, el objeto cargado desde `schema.json`;
- `validate(resumeJson, callback)`, que usa `jsonschema.Validator` y llama al
  callback con `(errors, false)` o `(null, true)`;
- `jobSchema`, separado del resume.

Este es el contrato efectivo de
[`validator.js`, líneas 1-22](https://github.com/jsonresume/jsonresume.org/blob/8e4947d2030db8bba22d2b897461dc5587ee7125/packages/schema/validator.js#L1-L22).
El callback es obligatorio en la implementación, aunque un segundo ejemplo del
README lo omite ([README, líneas
38-44](https://github.com/jsonresume/jsonresume.org/blob/8e4947d2030db8bba22d2b897461dc5587ee7125/packages/schema/README.md#L38-L44)); ese snippet no refleja la firma real.

La función siempre usa el schema empaquetado: no inspecciona el `$schema` de la
instancia para seleccionar o descargar otro. Para controlar exactamente el
contrato se puede importar `require('@jsonresume/schema').schema`, interfaz
documentada por el paquete ([README, líneas
47-51](https://github.com/jsonresume/jsonresume.org/blob/8e4947d2030db8bba22d2b897461dc5587ee7125/packages/schema/README.md#L47-L51)), y pasarlo explícitamente a un validador Draft-07.

### CLI oficial

`resume-cli@3.7.2` depende exactamente de `@jsonresume/schema@1.3.1` en su
artefacto npm ([registro versionado](https://registry.npmjs.org/resume-cli/3.7.2)).
`resume validate` carga por defecto ese `schema.json` empaquetado y permite
reemplazarlo con `--schema <path>` ([carga fijada](https://github.com/jsonresume/jsonresume.org/blob/8e4947d2030db8bba22d2b897461dc5587ee7125/packages/cli/lib/get-schema.js#L6-L15),
[comando fijado](https://github.com/jsonresume/jsonresume.org/blob/8e4947d2030db8bba22d2b897461dc5587ee7125/packages/cli/lib/main.js#L83-L120)).
Devuelve salida no cero ante un schema ilegible o una instancia inválida.

Su baseline es Ajv 8 con `allErrors: true`, `strict: false` y `ajv-formats`
activado ([implementación fijada](https://github.com/jsonresume/jsonresume.org/blob/8e4947d2030db8bba22d2b897461dc5587ee7125/packages/cli/lib/validate.js#L1-L21)).
Las pruebas de `@jsonresume/schema@1.3.1` reproducen esa configuración y además
garantizan que el schema compila con `strict: true`. Activar `ajv-formats` —o
una capacidad equivalente— es necesario para obtener la misma evaluación de
`email` y `uri` que el CLI.

### Validadores JSON Schema genéricos

Cualquier implementación compatible con Draft-07 puede validar el artefacto
fijado, pues sus únicos `$ref` son locales. Para comparar resultados con el CLI
oficial debe afirmarse `format`; un validador que lo trate solo como anotación
aceptará emails y URIs que el baseline rechaza. El comando `validate` del propio
`package.json` valida los archivos de schema contra el meta-schema; no valida
por sí solo un resume ([script fijado, líneas
7-10](https://github.com/jsonresume/jsonresume.org/blob/8e4947d2030db8bba22d2b897461dc5587ee7125/packages/schema/package.json#L7-L10)).

La documentación web oficial mutable también recomienda `resumed validate`
([página `/cli`, consultada en la fecha de corte](https://jsonresume.org/cli)).
Es una herramienta comunitaria, no un paquete de la organización JSON Resume;
`resumed@7.0.0` declara `@jsonresume/schema@^1.0.0`, no una versión exacta
([registro versionado](https://registry.npmjs.org/resumed/7.0.0)). Su resultado
depende de la resolución instalada y no identifica por sí solo qué artefacto
del schema se usó.

## Divergencias en superficies oficiales mutables

Estas superficies son información propia de JSON Resume, pero no reproducen el
contrato publicado de `packages/schema`:

- La página oficial [`jsonresume.org/schema`](https://jsonresume.org/schema)
  mostraba “version 1.0.0”. El texto está hardcodeado incluso en el snapshot de
  `master` observado ([fuente fijada, líneas
  3-9](https://github.com/jsonresume/jsonresume.org/blob/51e63a4f4e51bee7695fc88c8b79a9e1b7eba6f2/apps/homepage2/app/schema/components/SchemaDisplay.jsx#L3-L9)).
- `https://jsonresume.org/schema.json` respondía `404`; no existe ahí un URI
  canónico versionado del schema.
- El endpoint mutable
  [`registry.jsonresume.org/api/schema`](https://registry.jsonresume.org/api/schema)
  servía otro schema: Draft-04, `additionalProperties: false` en la raíz y un
  patrón de fecha que admite string vacío. Su fuente local confirma esas dos
  primeras diferencias ([implementación fijada, líneas
  16-42](https://github.com/jsonresume/jsonresume.org/blob/8e4947d2030db8bba22d2b897461dc5587ee7125/apps/registry/lib/schema.js#L16-L42)).
- Como ya se indicó, `sample.resume.json` de la propia versión `1.3.1` se
  autoidentifica como `v1.0.0`.

Estas discrepancias impiden usar la etiqueta de la web, el endpoint del
Registry o los metadatos del ejemplo como sustitutos de la release npm fijada.

## Hechos que condicionan la futura especificación

Sin decidir todavía la política de Profile Engine, el contrato observado deja
estas decisiones abiertas:

- versión exacta o rango de `@jsonresume/schema`, y proceso para evaluar cada
  actualización;
- identificador reproducible que se guardará junto al Perfil fuente, dado que
  `$id`, `$schema` y `meta.version` no identifican de forma fiable el artefacto;
- paridad de validador requerida, incluida la evaluación de `format` y el
  formato de errores;
- aceptación íntegra de la apertura de `additionalProperties` o aplicación de
  una capa adicional de restricciones propia de Profile Engine;
- convención para extensiones, ya que JSON Resume no reserva namespace ni
  contenedor;
- requisitos de contenido que JSON Resume no expresa: campos mínimos,
  strings/arrays no vacíos, fechas calendáricas, códigos de país, timestamps y
  relaciones entre fechas;
- tratamiento de las superficies oficiales divergentes y frecuencia con la
  que se comprobará drift entre npm, releases, `master` y documentación web.

## Conclusión

JSON Resume proporciona en `@jsonresume/schema@1.3.1` un contrato de
intercambio tipado, estable bajo una política SemVer declarada y deliberadamente
extensible. No proporciona por sí solo un perfil profesional completo, una
identidad de schema autoritativa dentro de cada documento ni validación fuerte
de contenido. La referencia reproducible para cualquier especificación
posterior es el artefacto npm/version/tag concretos; las decisiones de fijación,
endurecimiento y extensiones pertenecen al contrato futuro de Profile Engine.
