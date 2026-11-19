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
- Qué puedo explicar ahora: pendiente de respuesta del usuario.
- Qué todavía me genera dudas: pendiente de respuesta del usuario.
- Pregunta de cierre: ¿qué diferencia ves entre el roadmap, el plan de commits
  y el registro de aprendizaje?
- Próximo incremento: 01, dejar de versionar `venv/`. Aún no iniciado.

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
