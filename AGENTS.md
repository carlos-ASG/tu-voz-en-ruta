
# Convenciones para agentes de IA que contribuyen a este proyecto Django

Este documento recoge las normas y convenciones que cualquier agente (humano o IA) debe seguir al desarrollar, editar o revisar código y documentación en este proyecto Django.

IMPORTANTE: la base de datos del proyecto se encuentra en el archivo indicado en el contexto del repositorio: #file:database.sql

## Objetivo

Garantizar cambios consistentes, seguros y fáciles de revisar. Los agentes deben priorizar la calidad del código, la seguridad y la reproducibilidad.

## Contrato mínimo de un cambio

- Inputs: descripción del cambio, archivos modificados, motivos, datos de prueba (si aplica).
- Outputs esperados: cambios en el repositorio con mensajes de commit claros, pruebas (si aplica) y pasos para reproducir.
- Modos de error: validar precondiciones (migraciones pendientes, dependencias no instaladas, variables de entorno faltantes) y documentar cualquier fallo conocido.

## Normas generales

- Lenguaje: escribe los comentarios y la documentación en español preferiblemente.
- Pequeños cambios: mantener los commits atómicos (cada commit debe representar una única intención o reparación).
- Mensajes de commit: escritos en español, en tiempo imperativo breve, y con referencia a la tarea/issue si existe. Ejemplo: "Arregla validación de correo en formulario de quejas".
- No incluir secretos: nunca escribir contraseñas, tokens u otros secretos en el código o en los commits. Si necesitas credenciales de prueba, usa valores ficticios y documenta su uso.

## Estructura de los cambios

- Código: seguir las convenciones de estilo del proyecto (si no hay linter configurado, aplicar las convenciones de PEP8 para Python/Django).
- Tests: los cambios funcionales importantes deben acompañarse de tests unitarios o de integración mínimos que cubran el nuevo comportamiento.
- Migraciones: si se modifica el modelo, incluye la migración Django generada y explica su propósito.
- Documentación: actualizar o añadir documentación que explique la nueva funcionalidad o la corrección.

## Revisión de seguridad y privacidad

- Validar entradas: todo dato de entrada desde usuarios debe ser validado y saneado.
- Protección contra CSRF, XSS y SQL injection: usar las utilidades que provee Django y seguir las mejores prácticas.
- Datos sensibles: cuando trabajes con datos personales (PII), minimizar la exposición en los logs y en el historial de commits.

## Pruebas y verificación rápida

- Antes de enviar cambios, ejecutar al menos:
	- `python manage.py check`
	- `python manage.py test` (si el proyecto tiene tests)
	- Comprobación rápida de migraciones: `python manage.py makemigrations --dry-run --check`

Si no puedes ejecutar estos comandos por limitaciones del entorno, documenta los resultados esperados y cualquier riesgo.

## Formato de mensajes y metadatos en PR/commit

- Título PR/commit (línea corta): resumen claro en español.
- Descripción larga: contexto, por qué se hace el cambio, cómo probarlo, y lista de archivos claves cambiados.
- Checklist mínimo en la descripción:
	- [ ] Tests añadidos/actualizados (si aplica)
	- [ ] Migraciones incluidas (si aplica)
	- [ ] Documentación actualizada (si aplica)

## Ejemplos rápidos

- Commit correcto:

	"Corrige validación de fecha en formulario de incidencia"

	Descripción: "Se añade validación para impedir fechas futuras en el form de incidencia. Añadido test que cubre fecha válida/ inválida."

- Commit inadecuado:

	"arreglos varios"

	(Demasiado vago; no seguir esta forma)

## Buenas prácticas específicas para agentes IA

- Claridad ante automatización: cuando una IA proponga cambios automáticos (refactor, formateo, generación de código), describir en la PR exactamente qué se cambió y por qué.
- No actuar solo con cambios masivos sin pruebas: evitar reemplazos a gran escala sin tests ni revisión humana.
- Explicar supuestos: cualquier decisión tomada por inferencia (por ejemplo, elegir un comportamiento por defecto) debe documentarse en la PR.
- Ejecutar validaciones estáticas: siempre que sea posible, ejecutar linters y herramientas de análisis estático y reportar resultados.

## Formato y estilo del repositorio

- Archivos de texto: UTF-8 sin BOM.
- Ramas: nombrar ramas con prefijo corto tipo `feature/`, `fix/`, `chore/` seguido de una descripción y, opcionalmente, el id de issue: `feature/nueva-api-quejas-123`.
- Tests y fixtures: si añades fixtures, documenta cómo cargarlos y asegurarte de que no contienen datos reales.

## Gestión de la base de datos y datos de prueba

- La base de datos del proyecto (dump) está en: #file:database.sql
- Para pruebas locales, crea una nueva base de datos aislada y restaura el dump si es necesario. Documenta cualquier paso de restauración que realizaste.

## Registro de cambios y seguimiento

- Mantener un CHANGELOG.md para cambios importantes y breaking changes (si no existe, propon uno en la PR de la primera modificación significativa).

## Preguntas y aclaraciones

Si un agente necesita clarificaciones que no pueden inferirse del código o de este documento, abrir una issue o pedir revisión humana antes de grandes cambios.

---

Si quieres, puedo generar una versión breve traducida al inglés, o añadir ejemplos concretos adaptados a este repositorio (por ejemplo: convenciones para modelos de quejas, formularios y vistas). Indícame qué prefieres.

## Agents Rules

Best practices for automated agents working on this repository (short checklist):

- Respect repository conventions and commit formats described above.
- Keep changes small and reversible; prefer many small commits over a single large one.
- Run tests and checks locally before proposing a PR. If a test can't be run, document why and the expected outcome.
- Do not add or expose secrets in code or commits. Use environment variables and document any required test credentials.
- When modifying models, include migrations and database-safe steps; provide a rollback plan for destructive changes.
- Add or update tests for any functional change; include minimal fixtures or factories for predictable test data.
- Explain automated changes clearly in the PR: what was changed, why, and any assumptions made.
- If proposing code generation or large refactors, request a human review before merging.

Buenas prácticas (resumen en español):

- Mantener commits pequeños y descriptivos.
- Ejecutar `manage.py check` y `manage.py test` cuando sea posible; documentar fallos y limitaciones.
- No incluir secretos; usar variables de entorno para credenciales de prueba.
- Incluir migraciones y plan de reversión al tocar modelos.
- Añadir tests mínimos que cubran la nueva funcionalidad.
- Documentar supuestos y decisiones tomadas por la IA en la descripción de la PR.

---

Gracias por seguir las convenciones — si quieres personalizado para una carpeta (por ejemplo `apps/quejas/`), lo adapto.

