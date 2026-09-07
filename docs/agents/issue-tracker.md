# Gestor de issues: GitHub

Los issues y las especificaciones de este repositorio se gestionan como issues de GitHub. Utiliza la CLI `gh` para todas las operaciones.

## Convenciones

- **Crear un issue**: `gh issue create --title "..." --body "..."`. Utiliza un heredoc para cuerpos de varias líneas.
- **Leer un issue**: `gh issue view <number> --comments`, filtrando los comentarios con `jq` y obteniendo también las etiquetas.
- **Listar issues**: `gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'` con los filtros `--label` y `--state` apropiados.
- **Comentar un issue**: `gh issue comment <number> --body "..."`
- **Aplicar o quitar etiquetas**: `gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **Cerrar**: `gh issue close <number> --comment "..."`

Deduce el repositorio mediante `git remote -v`; `gh` lo hace automáticamente cuando se ejecuta dentro de un clon.

## Pull requests como superficie de triage

**PRs as a request surface: no.** _(Cambia el valor a `yes` si este repositorio trata las PR externas como solicitudes de funcionalidades; `/triage` lee esta marca.)_

Cuando el valor es `yes`, las PR pasan por las mismas etiquetas y estados que los issues mediante los comandos equivalentes de `gh pr`:

- **Leer una PR**: `gh pr view <number> --comments` y `gh pr diff <number>` para obtener el diff.
- **Listar PR externas para triage**: `gh pr list --state open --json number,title,body,labels,author,authorAssociation,comments`; conserva después solo los valores de `authorAssociation` `CONTRIBUTOR`, `FIRST_TIME_CONTRIBUTOR` o `NONE` y descarta `OWNER`, `MEMBER` y `COLLABORATOR`.
- **Comentar, etiquetar o cerrar**: `gh pr comment`, `gh pr edit --add-label`/`--remove-label`, `gh pr close`.

GitHub comparte un mismo espacio de numeración para issues y PR, por lo que un `#42` aislado puede ser cualquiera de los dos: compruébalo con `gh pr view 42` y, si falla, utiliza `gh issue view 42`.

## Cuando una skill indica que se publique en el gestor de issues

Crea un issue de GitHub.

## Cuando una skill indica que se obtenga el ticket pertinente

Ejecuta `gh issue view <number> --comments`.

## Operaciones de wayfinding

Las utiliza `/wayfinder`. El **mapa** es un único issue cuyos tickets son issues **hijos**.

- **Mapa**: un único issue con la etiqueta `wayfinder:map`, cuyo cuerpo contiene Notes / Decisions-so-far / Fog. `gh issue create --label wayfinder:map`.
- **Ticket hijo**: un issue vinculado al mapa como sub-issue de GitHub mediante `gh api` y el endpoint de sub-issues. Si los sub-issues no están habilitados, añade el hijo a una lista de tareas en el cuerpo del mapa y escribe `Part of #<map>` al principio del cuerpo del hijo. Etiquetas: `wayfinder:<type>` (`research`/`prototype`/`grilling`/`task`). Una vez reclamado, el ticket se asigna al desarrollador responsable.
- **Bloqueo**: las **dependencias nativas de issues** de GitHub son la representación canónica y visible en la interfaz. Añade una relación con `gh api --method POST repos/<owner>/<repo>/issues/<child>/dependencies/blocked_by -F issue_id=<blocker-db-id>`, donde `<blocker-db-id>` es el **identificador numérico de base de datos** del bloqueador (`gh api repos/<owner>/<repo>/issues/<n> --jq .id`, no el `#number` ni el `node_id`). GitHub informa de `issue_dependencies_summary.blocked_by`, que incluye solo los bloqueadores abiertos y actúa como condición vigente. Si las dependencias no están disponibles, utiliza como alternativa una línea `Blocked by: #<n>, #<n>` al principio del cuerpo del hijo. Un ticket queda desbloqueado cuando se cierran todos sus bloqueadores.
- **Consulta de frontera**: lista los hijos abiertos del mapa con `gh issue list --state open`, limitado a los sub-issues o la lista de tareas del mapa, y descarta aquellos que tengan un bloqueador abierto (`issue_dependencies_summary.blocked_by > 0` o un issue abierto en la línea `Blocked by`) o una persona asignada; prevalece el primero según el orden del mapa.
- **Reclamar**: `gh issue edit <n> --add-assignee @me`; esta es la primera escritura de la sesión.
- **Resolver**: ejecuta `gh issue comment <n> --body "<answer>"`, después `gh issue close <n>` y, por último, añade un puntero de contexto (gist y enlace) a Decisions-so-far en el mapa.
