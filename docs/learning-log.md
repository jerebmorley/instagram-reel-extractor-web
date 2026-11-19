# Registro de aprendizaje

Registrar evidencia y respuestas reales. Dejar pendiente lo que el usuario aún
no respondió; no confundir un cambio terminado con un concepto comprendido.

## Incremento 00 — Plan y método de trabajo

Fecha: 2026-11-19.

- Qué intentaba resolver: convertir el roadmap en incrementos pequeños y dejar
  instrucciones persistentes para trabajar con la IA de forma guiada.
- Qué creía que iba a pasar: pendiente de reflexión del usuario; este incremento
  fue autorizado como preparación documental.
- Qué cambió: roadmap original conservado en `ROADMAP.md`, secuencia de commits
  en `implementation-plan.md`, este registro e instrucciones en `../AGENTS.md`.
- Concepto presentado: el roadmap define alcance y destino; el plan lo convierte
  en cambios verificables; el registro conserva evidencia y aprendizaje.
- Verificación realizada: `cmp` confirmó que el roadmap es idéntico al original;
  el diff contiene únicamente los cuatro documentos previstos y
  `git diff --cached --check` pasó sin errores. No se ejecutó la aplicación
  ni se crearon pruebas de código para estos cambios documentales.
- Qué puedo explicar ahora: el usuario identifica el roadmap y el plan como
  herramientas para una implementación ordenada y documentada; el registro es
  personal y acompaña su formación como ingeniero de datos. Se explicó que el
  roadmap define alcance y etapas, y el plan los convierte en cambios verificables.
- Qué todavía me genera dudas: pendiente de respuesta del usuario.
- Pregunta de cierre: ¿qué diferencia ves entre el roadmap, el plan de commits
  y el registro de aprendizaje?
- Próximo incremento al cerrar esta etapa: 01, dejar de versionar `venv/`.

## Incremento 01 — Dejar de versionar el entorno virtual

Fecha: 2026-11-19.

- Qué intentaba resolver: quitar del versionado los 3.118 archivos del entorno
  virtual, conservando la instalación local.
- Qué creía que iba a pasar (usuario): los archivos seguirían en su computadora,
  Git dejaría de registrarlos y las versiones antiguas los conservarían.
- Aclaración conversada: el cambio aparecerá en la versión actual de GitHub
  cuando se suba el commit; los commits anteriores seguirán conteniendo `venv/`.
- Cambio realizado: agregar `venv/` a `.gitignore` y ejecutar
  `git rm -r --cached venv`. `--cached` retira los archivos del índice (la
  preparación del próximo commit) y conserva los archivos de trabajo.
- Concepto presentado: `.gitignore` evita incorporar archivos no seguidos;
  por sí solo no deja de seguir archivos que ya estaban versionados.
- Verificación: los 3.118 archivos locales conservaron su contenido (comparación
  de SHA-256 y destinos de enlaces antes/después); `git ls-files venv` quedó
  vacío; el commit anterior conserva las 3.118 rutas. `git check-ignore -v`
  confirmó las reglas de `venv/` y `.venv/`. La revisión del diff no detectó
  cambios de código y `git diff --cached --check` pasó sin errores.
- Qué puedo explicar ahora: la predicción del usuario distingue archivos locales,
  versionado actual e historial. La comprensión de `.gitignore` queda por revisar.
- Qué todavía me genera dudas: pendiente de respuesta del usuario.
- Pregunta de cierre: ¿por qué agregar `venv/` a `.gitignore` no era suficiente?
- Próximo paso: incremento 02; aún no iniciado.

## Plantilla para el siguiente incremento

```markdown
## Incremento NN — Título

Fecha:

- Qué intentaba resolver:
- Qué creía que iba a pasar:
- Qué pasó:
- Cómo lo comprobé:
- Qué puedo explicar ahora:
- Qué todavía me genera dudas:
- Próximo paso:
```
